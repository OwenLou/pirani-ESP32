"""
a PID attempt
Hardware List:
    esp32 devkitC
    ssd1306 128x64
    resistors
"""

## import modules ################################

# from _typeshed import ReadableBuffer
import utime, time
from machine import SoftI2C, Pin
from machine import PWM, ADC
from ssd1306 import SSD1306_I2C
from myPID import myPID

## variables and parametres ######################

# Pins and Values
PinPwm0: Pin(int) = Pin(12, Pin.OUT)
VPwm0: float = 0.0
dataPwm0: int = 0

PinAdc0: Pin(int) = Pin(32, Pin.IN, Pin.PULL_UP)
Vadc0: float = 0.0
dataAdc0: int = 0

# ADC
adc0 = ADC(PinAdc0)
adc0.atten(ADC.ATTN_0DB)  # 无衰减, 测量范围为0-1V
adc0.width(ADC.WIDTH_12BIT)  # 12位宽, 4096
ADC_DATA_MAX = 4096
ADC_VOLT_MAX = 1.0


# 显示屏幕, 默认的location为60=0x3c
i2c = SoftI2C(scl=Pin(18), sda=Pin(19), freq=100000)  # Init i2c 如果是esp32，SCL接22口、SDA接21口
oled = SSD1306_I2C(128, 64, i2c)  # 创建oled对象
oled.init_display()  # 清空当前显示
DIG_WIDTH = 8
DIG_HEIGHT = 8

print("Peripheral devices initialization Completed.\n")


def ADC_Data2V(thisData):
    if (thisData < 0):
        print("\nin ADC_Data2V: data = %d out of range! Set to %d" % (thisData, 0))
        thisData = 0
    elif (thisData >= ADC_DATA_MAX):
        print("\nin ADC_Data2V: data = %d out of range! Set to %d" % (thisData, ADC_DATA_MAX-1))
        thisData = ADC_DATA_MAX-1
    return thisData / ADC_DATA_MAX * ADC_VOLT_MAX

def ADC_V2Data(thisV):
    if (thisV < 0):
        print("\nin ADC_V2Data: voltage = %d out of range! Set to %.2f" % (thisV, 0))
        thisV = 0
    elif (thisV > ADC_VOLT_MAX):
        print("\nin ADC_V2Data: voltage = %d out of range! Set to %.2f" % (thisV, ADC_VOLT_MAX))
        thisV = ADC_VOLT_MAX
    return int(thisV / ADC_VOLT_MAX * ADC_DATA_MAX)

def ADC_Data2V_cor(thisData):
    if (thisData < 0):
        print("\nin ADC_Data2V: data = %d out of range! Set to %d" % (thisData, 0))
        thisData = 0
    elif (thisData >= ADC_DATA_MAX):
        print("\nin ADC_Data2V: data = %d out of range! Set to %d" % (thisData, ADC_DATA_MAX-1))
        thisData = ADC_DATA_MAX-1
    # 0.07045  2.32719e-4
    return 2.32719e-4 * thisData + 0.07045

def printOled(rowNum, colNum, myStr, value):  # 10 pix = 1 rowWidth
    oled.fill_rect(DIG_HEIGHT * rowNum, DIG_WIDTH * colNum, DIG_WIDTH * len(myStr), DIG_HEIGHTsqa, 0)
    oled.show()
    oled.row
    # TODO! Not finished
    return

## operation #####################################

cnt = 0
dataCnt = 1000
dataSum = 0.0
while True:
    oled.init_display()
    for i in range(dataCnt):
        dataSum += adc0.read()
    dataSum /= dataCnt
    oled.text("adc = " + str(dataSum),0,0)
    oled.text("vol = " + str(ADC_Data2V_cor(dataSum)),0,8)
    cnt += 1
    oled.text("cnt = " + str(cnt),0,16)
    oled.show()
    dataSum = 0
    time.sleep_ms(1000)

# 0.07045  2.32719e-4

