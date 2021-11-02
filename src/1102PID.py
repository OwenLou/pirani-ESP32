"""
# PID调控Pirani真空计
## 硬件清单:
- ESP32 devkitC
    - 包括的自带功能有: pwm, adc, i2c, etc.
- ads1115
    - 16bit, 推荐128SPS, 用于ADC
- MCP4725
    - 12bit, 用于DAC
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

import utime, math
from machine import SoftI2C, Pin, RTC
import ADS1x15  # AD
from ADS1x15 import ADS1115_BUS_ADDRESS
from MCP4725 import MCP4725, MCP4725_BUS_ADDRESS  # DA
from ssd1306 import SSD1306_I2C
from myPID import PID



## 外设和变量 ###############################################

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

# DAC: MCP4725
dac0_i2c = SoftI2C(scl=Pin(25), sda=Pin(26), freq=100000)
dac0 = MCP4725(dac0_i2c, MCP4725_BUS_ADDRESS[0])  # A0 -> GND
dac0_V: float = 1.5  # 存储电压
dac0_VREF: float = 2.994  # 参考电压, 来自REF3030
dac0_DATA_MAX: int = 4096
# dac0.write(value)  # 0 <= value < 4096

# DAC电压经过OPA, 给电桥的供电
OPA_DAC_MAG: float = 2.0
OPA_DAC_MAG_VOLT_MAX: float = dac0_VREF * OPA_DAC_MAG
# 电桥出来的电压, 差分放大
OPA_DIF_MAG: float = 3.0
# 合成电压中的电压大小
OPA_OFFSET_VOLTAGE: float = 0.5040  # 记得每次测量一下!!!

# ADC: ADS1115
adc0_i2c = SoftI2C(scl=Pin(25), sda=Pin(26), freq=100000)  # 这样定义会引起冲突吗?
adc0 = ADS1x15.ADS1115(adc0_i2c, ADS1115_BUS_ADDRESS[0], gain=3)  # ADDR -> GND  # gain 1 -> 4.096
adc0_CALIBRATION: float = 1.021931
adc0_V: float = 0
# adc0_data = ad.read(rate=4)  # ch1读数一次, rate=4 -> 128SPS
# adc0_V = adc0_CALIBRATION * adc0.raw_to_v(adc0_data)
# 之后可以使用内部封装的函数进行转换! 不需要自己再写啦!

# PID stuff
pid_setPoint: float = 150.0  # 电压max = 3.3V, 所以150Ohm能达到
pid_loopTime: int = 1000  # in milliseconds
Kp: float = 5e-3
Ki: float = 1e-4
Kd: float = 3e-3
pid = PID(Kp, Ki, Kd)
pid.allSet(pid_setPoint)

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

def testadda(volt):
    """
    数据顺序: 要求电压  da_data  ad_data  AD电压
    """
    dac0_data = int(dac0_DATA_MAX * volt / dac0_VREF)
    print(volt, dac0_data, end=" ")
    if(dac0_data >= dac0_DATA_MAX or dac0_data < 0):
        print("Exceed 0.0 ~ 3.0V limit")
        return
    dac0.write(dac0_data)
    utime.sleep_ms(100)
    adc0_data = adc0.read(rate=4)
    print(adc0_data, adc0_CALIBRATION * adc0.raw_to_v(adc0_data))

def dac_setVolt(volt):
    dac0_data = int(dac0_DATA_MAX * volt / dac0_VREF)
    if(dac0_data >= dac0_DATA_MAX or dac0_data < 0):
        print("Exceed 0.0 ~ 3.0V limit. round to max")
        dac0_data = dac0_DATA_MAX - 1
    dac0.write(dac0_data)
    return dac0_data

def getStat(adc, file=None, cnt=100, rate=4):
    """
    只记录ad数值, 不做转换
    """
    data = [0 for i in range(cnt)]
    avg = 0
    std = 0
    for i in range(cnt):
        data[i] = adc.read(rate)
        if (i % int(cnt/10) == 0):
            print("-", end="")
    avg = sum(data) / cnt
    print("avg =", avg)
    for i in range(cnt):
        if (file != None):
            file.write(str(data[i]) + "\n")
        std += (data[i] - avg)**2
        if (i % int(cnt/10) == 0):
            print("-", end="")
    std = math.sqrt(std/cnt)
    print("std =", std)
    return [avg, std]

def genRTCfname():
    # 输出一个文件名
    rtc = RTC()
    fname = ""
    for item in rtc.datetime()[0:-2]:
        fname += str(item) + "-"
    fname = "/data/" + fname + str(rtc.datetime()[-2]) + ".dat"
    return fname


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
    oled.text("adc0_V = ", 0*DIG_WIDTH, 0*DIG_HEIGHT)
    oled.text("   RPi = ", 0*DIG_WIDTH, 1*DIG_HEIGHT)
    oled.text("   pid = ", 0*DIG_WIDTH, 2*DIG_HEIGHT)
    oled.text("dac0_V'= ", 0*DIG_WIDTH, 3*DIG_HEIGHT)
    oled.text("d_Time = ", 0*DIG_WIDTH, 7*DIG_HEIGHT)
    return



## operation ############################################################

# datafile = open(genRTCfname(), "w")

dac_setVolt(0)
print("dac0_V\tadc0_V\tRPi\tpidOut\tpwm0_V'", end="\n")
print("%.2f" % dac0_V, end="\t")
oledSetup(oled)
loopTime = 100
utime.sleep_ms(loopTime)
# 这样不删除buffer, 是不是还需要定时清除buffer?


while True:
    printOled(str(dac0_V)[0:5], tabNum*DIG_WIDTH, 0*DIG_HEIGHT)
    adc0_data = adc0.read(rate=4)
    adc0_V = adc0_CALIBRATION * adc0.raw_to_v(adc0_data)
#     printOled(str(adc0_V)[0:5], tabNum*DIG_WIDTH, 1*DIG_HEIGHT)
    RPi = getRPi((adc0_V - OPA_OFFSET_VOLTAGE)/OPA_DIF_MAG, dac0_V * OPA_DAC_MAG)
#     printOled(str(RPi)[0:5], tabNum*DIG_WIDTH, 2*DIG_HEIGHT)
    pid.compute(RPi)
#     printOled(str(pid.output)[0:5], tabNum*DIG_WIDTH, 3*DIG_HEIGHT)
    dac0_V += pid.output
#     printOled(str(dac0_V)[0:5], tabNum*DIG_WIDTH, 4*DIG_HEIGHT)
    dac_setVolt(dac0_V)
    print("%.4f\t%.3f\t%.3f\t%.3f" % (adc0_V, RPi, pid.output, dac0_V), end="\n")
    print("%.3f" % dac0_V, end='\t')
#     utime.sleep_ms(loopTime)









