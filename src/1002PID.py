"""
# PID调控Pirani真空计
## 硬件清单:
- ESP32 devkitC
    - 包括的自带功能有: pwm, adc, i2c, etc.
- ssd1306 (128x64)
    - 用于显示, 不用在电脑屏幕前监视
- 五色环电阻
- 运放电路 OPA
    - LM358, 四路高精度, 零点效果好
- 电源模块
    - 使用ANSJ HAW10-220D12B7
    - 最大输出功率约为6W, 满足实验要求
    - 为运放供电提供正负12V电压
## 变量命名规则
- 外设命名方式为: [外设名称][编号]
- 关于外设的变量
    - [外设名称][编号]_[变量名称]
- 一般变量
    - 驼峰式
- 注意:
    - PID调控使用`myPID`module
        - 因此命名方式同外设
    - 尽量使用小写, 除非遇到驼峰情况
    - 全大写用于常量
"""

## import modules ######################################################

import utime, time
from machine import SoftI2C, Pin
from machine import PWM, ADC
from ssd1306 import SSD1306_I2C
from PID import PID



## 外设和变量 ###############################################
print("Initializing Peripheral devices...")
# 电桥阻值
RBr1: float = 150.0
RPi: float = 150.0  # 这里用来储存读书, 而不是目标值
RBr3: float = 150.0
RBr4: float = 150.0
"""
    Wiring
         ┌--RBr4--┬--RBr3--┐
         │        +        │
    Vcc--┤       Vop       ├--GND
         │        -        │
         └--RPi---┴--RBr1--┘
"""

def getRPi(Vop, Vcc):
    a = - Vop / Vcc + RBr3 / (RBr4 + RBr3)  # 只是一个过程量
    global RPi
    RPi = RBr1 * (1 / a - 1)
    return RPi

# pmw
pwm0_pin: Pin(int) = Pin(12, Pin.OUT)  # pwm输出初始化
pwm0 = PWM(pwm0_pin, freq=10000, duty=0)  # 最后得到实际的对象
pwm0_duty: int = 0  # 用于存储pwm的duty
PWM_DUTY_MAX: int = 1024  # 应该小于这个数值!
pwm0_V: float = 0.0  # 用于存储输出电压
PWM_VOLT_MAX: float = 3.3  # 输出电压的最大值

# PWM滤波之后的电压, 经过OPA, 给电桥的供电
OPA_PWM_MAG: float = 2.0
OPA_PWM_MAG_VOLT_MAX: float = PWM_VOLT_MAX * OPA_PWM_MAG
# 电桥出来的电压, 差分放大
OPA_DIF_MAG: float = 3.0
# 合成电压中的电压大小
OPA_OFFSET_VOLTAGE: float = 0.4992  # 记得每次测量一下!!!


# adc
adc0_pin: Pin(int) = Pin(32, Pin.IN, Pin.PULL_UP)  # Pin.PULL_UP要不要加呢?
adc0 = ADC(adc0_pin)
adc0.atten(ADC.ATTN_0DB)  # 无衰减, 测量范围为0-1V
adc0.width(ADC.WIDTH_12BIT)  # 12位宽, 4096
adc0_data: int = 0  # 用于存储adc读到的data
ADC_DATA_MAX: int = 4096  # determined by bit width above
adc0_V: float = 0.0  # 用于存储读入电压
ADC_VOLT_MAX: float = 1.0  # 并没有atten, 所以最大1.0(同时也是为了测准)
ADC_SLOPE_COR: float = 2.32719e-4
ADC_INTER_COR: float = 7.045e-2  # intersection
#　换算公式为: V = COR_ADC0_SLOPE * adcData + COR_ADC0_INTER
ADC_SMOOTH_CNT: int = 1000  # 连续读数, 时间平滑一下

# PID stuff
setPoint: float = 150.0  # 电压max = 3.3V, 所以150Ohm能达到
loopTime: int = 1000  # in milliseconds
Kp: float = 1.0
Ki: float = 0.0
Kd: float = 1.0
pid = PID(Kp, Ki, Kd)

# # UART  # 似乎不需要UART, 直接print就好
# # UART0和usb实际上是一个
# uart0 = UART(1, baudrate=9600, tx=1, rx=32)

# 显示屏幕, 默认的location为60=0x3c
DIG_WIDTH: int = 8
DIG_HEIGHT: int = 8
SCREEN_WIDTH: int = 128
SCREEN_HEIGHT: int = 64
oled_i2c = SoftI2C(scl=Pin(18), sda=Pin(19), freq=100000)  # Init i2c 如果是esp32，SCL接22、SDA接21
oled = SSD1306_I2C(SCREEN_WIDTH, SCREEN_HEIGHT, oled_i2c)  # 创建oled对象
oled.init_display()  # 清空当前显示
tabNum: int = 8  # 用于打印屏幕

print("Peripheral devices initialization Completed.\n")
oled.text("Peripheral", 0*DIG_WIDTH, 0*DIG_HEIGHT)
oled.text("devices", 0*DIG_WIDTH, 1*DIG_HEIGHT)
oled.text("initialization", 0*DIG_WIDTH, 2*DIG_HEIGHT)
oled.text("Completed", 0*DIG_WIDTH, 3*DIG_HEIGHT)
oled.show()


## def functions ########################################################

def PWM_Duty2V(thisDuty):
    if (thisDuty < 0):
        print("\nin PWM_Duty2V(): duty = %d out of range! \
              Set to %d" % (thisDuty, 0))
        thisDuty = 0
    elif (thisDuty >= PWM_DUTY_MAX):
        print("\nin PWM_Duty2V(): duty = %d out of range! Set to %d" % (thisDuty, PWM_DUTY_MAX-1))
        thisDuty = PWM_DUTY_MAX-1
    return thisDuty / PWM_DUTY_MAX * OPA_PWM_MAG_VOLT_MAX

def PWM_V2Duty(thisV):
    if (thisV < 0):
        print("\nin PWM_V2Duty(): voltage = %.2f out of range! Set to %.2f" % (thisV, 0.0))
        thisV = 0.0
    elif (thisV >= OPA_PWM_MAG_VOLT_MAX):
        print("\nin PWM_V2Duty(): voltage = %.2f out of range! Set to %.2f" % (thisV, OPA_PWM_MAG_VOLT_MAX))
        thisV = OPA_PWM_MAG_VOLT_MAX
    return int(thisV / PWM_VOLT_MAX * PWM_DUTY_MAX)

def ADC_Data2V(thisData):
    if (thisData < 0):
        print("\nin ADC_Data2V(): data = %d out of range! Set to %d" % (thisData, 0))
        thisData = 0
    elif (thisData >= ADC_DATA_MAX):
        print("\nin ADC_Data2V(): data = %d out of range! Set to %d" % (thisData, ADC_DATA_MAX-1))
        thisData = ADC_DATA_MAX-1
    return thisData / ADC_DATA_MAX * ADC_VOLT_MAX

def ADC_Data2V_cor(thisData):
    if (thisData < 0):
        print("\nin ADC_Data2V(): data = %d out of range! Set to %d" % (thisData, 0))
        thisData = 0
    elif (thisData >= ADC_DATA_MAX):
        print("\nin ADC_Data2V(): data = %d out of range! Set to %d" % (thisData, ADC_DATA_MAX-1))
        thisData = ADC_DATA_MAX-1
    # 0.07045  2.32719e-4
    return ADC_SLOPE_COR * thisData + ADC_INTER_COR

def ADC_V2Data(thisV):
    if (thisV < 0):
        print("\nin ADC_V2Data(): voltage = %d out of range! Set to %.2f" % (thisV, 0))
        thisV = 0
    elif (thisV > ADC_VOLT_MAX):
        print("\nin ADC_V2Data(): voltage = %d out of range! Set to %.2f" % (thisV, ADC_VOLT_MAX))
        thisV = ADC_VOLT_MAX
    return int(thisV / ADC_VOLT_MAX * ADC_DATA_MAX)

def heatUp(thisPwm):
    print("Heat up:\t%d / " % PWM_DUTY_MAX, end="")
    for i in range(0, PWM_DUTY_MAX):
        thisPwm.duty(i)
        i = thisPwm.duty()
        if i%16 == 0:
            print(i, end=" ")
            if i%256 == 0:
                print("", end="\n")
        utime.sleep_ms(5)
    VPwm0 = PWM_Duty2V(PWM_DUTY_MAX-1)
    print("\nHeat up finished, VPwm0 = %.2f" % VPwm0, end="\n\n")
    return

def printOled(myStr, rowNum, colNum):
    if type(myStr) != str:
        myStr = str(myStr)
    oled.fill_rect(DIG_HEIGHT * rowNum, DIG_WIDTH * colNum, DIG_WIDTH * len(myStr), DIG_HEIGHT, 0)
    oled.show()
    oled.text(myStr, DIG_HEIGHT * rowNum, DIG_WIDTH * colNum)
    oled.show()
    return

def oledSetup(oled):
    oled.init_display()
    oled.text("pwm0_V = ", 0*DIG_WIDTH, 0*DIG_HEIGHT)
    oled.text("adc0_V = ", 0*DIG_WIDTH, 1*DIG_HEIGHT)
    oled.text("RPi    = ", 0*DIG_WIDTH, 2*DIG_HEIGHT)
    oled.text("pidOut = ", 0*DIG_WIDTH, 3*DIG_HEIGHT)
    oled.text("pwm0_V'= ", 0*DIG_WIDTH, 4*DIG_HEIGHT)
    oled.text("d_Time = ", 0*DIG_WIDTH, 7*DIG_HEIGHT)
    return

def adc_read_smooth(adc):
    adcReadSum = 0
    adcReadData = 0
    for i in range(ADC_SMOOTH_CNT):
        adcReadData = adc.read()
        while adcReadData == 0:
            print('*', end='')
            adcReadData = adc0.read()
        adcReadSum += adcReadData
    return adcReadSum / ADC_SMOOTH_CNT


## operation ############################################################

"""
这个.py文件的目标在于测试ESP32的PWM和ADC是否正常工作.
虽然PID相关内容也被包括进去, 但是实际上是不用的
需要完成的内容:
    - 开启pwm, 开启adc
    - 两者数据输出到ssd1306, 检查正确性
"""

# heatUp(pwm0)
# pid.allSet(setPoint)
pwm0_V = 1.5
pwm0.duty(512)
print("pwm0_V\tadc0_V\tRPi\tpidOut\tpwm0_V'", end="\n")
print("%.2f" % pwm0_V, end="\t")
oledSetup(oled)
# 这样不删除buffer, 是不是还需要定时清除buffer?


while True:
    printOled(str(pwm0_V)[0:5], tabNum*DIG_WIDTH, 0*DIG_HEIGHT)
    adc0_data = adc_read_smooth(adc0)
    adc0_V = ADC_Data2V_cor(adc0_data)
    printOled(str(adc0_V)[0:5], tabNum*DIG_WIDTH, 1*DIG_HEIGHT)
    RPi = getRPi((adc0_V - OPA_OFFSET_VOLTAGE)/OPA_DIF_MAG, pwm0_V*OPA_PWM_MAG)
    printOled(str(RPi)[0:5], tabNum*DIG_WIDTH, 2*DIG_HEIGHT)
    # pid.compute(RPi)
    # printOled(str(pid.output)[0:5], tabNum*DIG_WIDTH, 3*DIG_HEIGHT)
    # pwm0_V += 0.005 * pid.output
    printOled(str(pwm0_V)[0:5], tabNum*DIG_WIDTH, 4*DIG_HEIGHT)
    pwm0_duty = PWM_V2Duty(pwm0_V)  # PWM_V2Duty 并没有解决1024超过pwm范围的事情
    if pwm0_duty >= PWM_DUTY_MAX:
        pwm0 = PWM_DUTY_MAX - 1
#     pwm0.duty(pwm0_duty)  # 仅仅是测试, 先取消设置
    print("%.3f\t%.3f\t%.3f\t%.3f" % (adc0_V, RPi, pid.output, pwm0_V), end="\n")
    print("%.3f" % pwm0_V, end='\t')
    time.sleep_ms(loopTime)


# while True:
#     printOled(str(pwm0_V)[0:5], tabNum*DIG_WIDTH, 0*DIG_HEIGHT)
#     adc0_data = adc_read_smooth(adc0)
#     adc0_V = ADC_Data2V_cor(adc0_data)
#     printOled(str(adc0_V)[0:5], tabNum*DIG_WIDTH, 1*DIG_HEIGHT)
#     RPi = getRPi(adc0_V, pwm0_V*2)
#     printOled(str(RPi)[0:5], tabNum*DIG_WIDTH, 2*DIG_HEIGHT)
#     pid.compute(RPi)
#     printOled(str(pid.output)[0:5], tabNum*DIG_WIDTH, 3*DIG_HEIGHT)
#     pwm0_V += 0.005 * pid.output
#     printOled(str(pwm0_V)[0:5], tabNum*DIG_WIDTH, 4*DIG_HEIGHT)
#     pwm0_duty = PWM_V2Duty(pwm0_V)  # PWM_V2Duty 并没有解决1024超过pwm范围的事情
#     if pwm0_duty >= PWM_DUTY_MAX:
#         pwm0 = PWM_DUTY_MAX - 1
# #     pwm0.duty(pwm0_duty)  # 仅仅是测试, 先取消设置
#     print("%.3f\t%.3f\t%.3f\t%.3f" % (adc0_V, RPi, pid.output, pwm0_V), end="\n")
#     print("%.3f" % pwm0_V, end='\t')
#     time.sleep_ms(loopTime)

