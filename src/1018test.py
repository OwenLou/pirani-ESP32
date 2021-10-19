"""
# PID调控Pirani真空计
## 硬件清单:
- ESP32 devkitC
    - 包括的自带功能有: pwm, adc, i2c, etc.
- ads1115
    - 16bit, 推荐128SPS, 用于ADC
- MCP4725
    - ??bit, 用于DAC
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
from machine import SoftI2C, Pin
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
dac0_VREF: float = 3.181  # 参考电压, 来自REF3030
dac0_DATA_MAX: int = 4096
# dac0.write(value)  # 0 <= value < 4096

# DAC电压经过OPA, 给电桥的供电
OPA_DAC_MAG: float = 2.0
OPA_DAC_MAG_VOLT_MAX: float = dac0_VREF * OPA_DAC_MAG
# 电桥出来的电压, 差分放大
OPA_DIF_MAG: float = 3.0
# 合成电压中的电压大小
OPA_OFFSET_VOLTAGE: float = 0.5000  # 记得每次测量一下!!!

# ADC: ADS1115
adc0_i2c = SoftI2C(scl=Pin(25), sda=Pin(26), freq=100000)  # 这样定义会引起冲突吗?
adc0 = ADS1x15.ADS1115(adc0_i2c, ADS1115_BUS_ADDRESS[0], gain=4)  # ADDR -> GND  # gain 1 -> 4.096
adc0_CALIBRATION: float = 1.021931
# adc0_data = ad.read(rate=4)  # ch1读数一次, rate=4 -> 128SPS
# adc0_V = adc0_CALIBRATION * adc0.raw_to_v(adc0_data)
# 之后可以使用内部封装的函数进行转换! 不需要自己再写啦!

# PID stuff
pid_setPoint: float = 150.0  # 电压max = 3.3V, 所以150Ohm能达到
pid_loopTime: int = 1000  # in milliseconds
Kp: float = 1.0
Ki: float = 0.0
Kd: float = 1.0
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

testadda(1.5)


readCNT = 50

# temp = 0
# data = [0 for i in range(readCNT)]
# avg = 0
# std = 0
# while True:
#     avg = 0
#     std = 0
#     start = utime.ticks_ms()
#     for i in range(readCNT):
#         adc0_data = adc0.read(rate=7)
#         data[i] = adc0_CALIBRATION * adc0.raw_to_v(adc0_data)
#         avg += data[i]
#     end = utime.ticks_ms()
#     print("SPS =", (end - start)/readCNT, "ms")
#     avg /= readCNT
#     for i in range(readCNT):
#         std += (data[i] - avg)**2
#         std /= readCNT
#         std = math.sqrt(std)
#     print("avg =", avg,  "std =", std)

volt = 1.5

while True: 
    dac0_data = int(dac0_DATA_MAX * volt / dac0_VREF)
    print(volt, dac0_data, end=" ")
    if(dac0_data >= dac0_DATA_MAX or dac0_data < 0):
        print("Exceed 0.0 ~ 3.0V limit")
        break
#     dac0.write(dac0_data)
    utime.sleep_ms(100)
    adc0_data = 0.0
    for i in range(readCNT):
        adc0_data += adc0.read(rate=7)
    adc0_data /= readCNT
    print(adc0_data, adc0_CALIBRATION * adc0.raw_to_v(adc0_data))
    utime.sleep_ms(500)

# divCNT = 50
# for i in range(divCNT):
#     volt = dac0_VREF * i / divCNT
#     testadda(volt)
#     utime.sleep_ms(2000)

# 把repl输出copy到origin里就可





