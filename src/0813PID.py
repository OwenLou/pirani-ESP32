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

RSa: float = 50.0
RPi: float = 180.0
# VPWM0_MAX = 3.3 V
# VADC0_MAX = 0.92 V

# PID stuff
setPoint: float = 130.0
loopTime: int = 1000  # in milliseconds
Kp: float = 1.0
Ki: float = 0.0
Kd: float = 1.0

## peripheral devices ############################

print("Initializating Peripheral devices initialization...")

# PWM, 0<freq<=78125Hz, 0<=duty<=1023, duty=512->50%
try:
    pwm0.deinit()
except (NameError):
    print("pwm0 undefined. redefining...")
pwm0 = PWM(PinPwm0, freq=10000, duty=0)  # 占空比暂时为0
PWM_DUTY_MAX = 1024
PWM_VOLT_MAX = 3.3

# ADC
adc0 = ADC(PinAdc0)
adc0.atten(ADC.ATTN_0DB)  # 无衰减, 测量范围为0-1V
adc0.width(ADC.WIDTH_12BIT)  # 12位宽, 4096
ADC_DATA_MAX = 4096
ADC_VOLT_MAX = 1.0

# myPID
pid = myPID(Kp, Ki, Kd)

# # 串口UART  # 似乎不需要UART, 直接print就好, UART0和usb实际上是一个
# uart0 = UART(1, baudrate=9600, tx=1, rx=32)

# 显示屏幕, 默认的location为60=0x3c
i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=100000)  # Init i2c 如果是esp32，SCL接22口、SDA接21口
oled = SSD1306_I2C(128, 64, i2c)  # 创建oled对象
oled.init_display()  # 清空当前显示
DIG_WIDTH = 8
DIG_HEIGHT = 8

print("Peripheral devices initialization Completed.\n")

## def functions #################################

def heatUp(thisPwm):
    print("Heat up:\t%d / " % PWM_DUTY_MAX, end="")
    for i in range(0, PWM_DUTY_MAX):
        thisPwm.duty(i)
        if i%16 == 0:
            print(i, end=" ")
            if i%256 == 0:
                print("", end="\n")
        time.sleep_ms(5)
    VPwm0 = PWM_Duty2V(PWM_DUTY_MAX-1)
    print("\nHeat up finished, VPwm0 = %.2f" % VPwm0, end="\n\n")
    return

def PWM_Duty2V(thisDuty):
    if (thisDuty < 0):
        print("\nin PWM_Duty2V: duty = %d out of range! Set to %d" % (thisDuty, 0))
        thisDuty = 0
    elif (thisDuty >= PWM_DUTY_MAX):
        print("\nin PWM_Duty2V: duty = %d out of range! Set to %d" % (thisDuty, PWM_DUTY_MAX-1))
        thisDuty = PWM_DUTY_MAX-1
    return thisDuty / PWM_DUTY_MAX * PWM_VOLT_MAX
        
def PWM_V2Duty(thisV):
    if (thisV < 0):
        print("\nin PWM_V2Duty: voltage = %.2f out of range! Set to %.2f" % (thisV, 0.0))
        thisV = 0.0
    elif (thisV >= PWM_VOLT_MAX):
        print("\nin PWM_V2Duty: voltage = %.2f out of range! Set to %.2f" % (thisV, PWM_VOLT_MAX))
        thisV = PWM_VOLT_MAX
    return int(thisV / PWM_VOLT_MAX * PWM_DUTY_MAX)

def ADC_Data2V(thisData):
    if (thisData < 0):
        print("\nin ADC_Data2V: data = %d out of range! Set to %d" % (thisData, 0))
        thisData = 0
    elif (thisData >= ADC_DATA_MAX):
        print("\nin ADC_Data2V: data = %d out of range! Set to %d" % (thisData, ADC_DATA_MAX-1))
        thisData = ADC_DATA_MAX-1
    return thisData / ADC_DATA_MAX * ADC_VOLT_MAX

def ADC_Data2V_cor(thisData):
    if (thisData < 0):
        print("\nin ADC_Data2V: data = %d out of range! Set to %d" % (thisData, 0))
        thisData = 0
    elif (thisData >= ADC_DATA_MAX):
        print("\nin ADC_Data2V: data = %d out of range! Set to %d" % (thisData, ADC_DATA_MAX-1))
        thisData = ADC_DATA_MAX-1
    # 0.07045  2.32719e-4
    return 2.32719e-4 * thisData + 0.07045

def ADC_V2Data(thisV):
    if (thisV < 0):
        print("\nin ADC_V2Data: voltage = %d out of range! Set to %.2f" % (thisV, 0))
        thisV = 0
    elif (thisV > ADC_VOLT_MAX):
        print("\nin ADC_V2Data: voltage = %d out of range! Set to %.2f" % (thisV, ADC_VOLT_MAX))
        thisV = ADC_VOLT_MAX
    return int(thisV / ADC_VOLT_MAX * ADC_DATA_MAX)

def printOled(rowNum, colNum, myStr, value):  # 10 pix = 1 rowWidth
    oled.fill_rect(DIG_HEIGHT * rowNum, DIG_WIDTH * colNum, DIG_WIDTH * len(myStr), DIG_HEIGHTsqa, 0)
    oled.show()
    oled.row
    # TODO! Not finished
    return

## operation #####################################

heatUp(pwm0)
pid.allSet(setPoint)
print("VPwm0\tVAdc0\tRPi\tpidOut\tVPwm0*", end="\n")
VPwm0 = PWM_Duty2V(PWM_DUTY_MAX-1)  # 不知道为什么, 不加这条就是VPwm0 = 0.00
print("%.2f" % VPwm0, end="\t")

while True:
    oled.init_display()
    oled.text("VPwm0 = " + str(VPwm0)[0:5],0,0)
    oled.show()
    dataAdc = adc0.read()
    while dataAdc == 0:
        print('*', end="")
        dataAdc = adc0.read()
    VAdc0 = ADC_Data2V(dataAdc)
    oled.text("VAdc0 = " + str(VAdc0)[0:5],0,8)
    oled.show()    
    RPi = VPwm0 / (VAdc0 / 50)
    oled.text("RPi   = " + str(RPi)[0:5],0,16)
    oled.show()
    pid.compute(RPi)
    oled.text("pid   = " + str(pid.output)[0:5],0,24)
    oled.show()
    VPwm0 += 0.005 * pid.output
    oled.text("VPwm0 = " + str(VPwm0)[0:7],0,32)
    oled.show()
    dataPwm0 = PWM_V2Duty(VPwm0)
    pwm0.duty(dataPwm0)
    print("%.3f\t%.3f\t%.3f\t%.3f" % (VAdc0,RPi,pid.output,VPwm0), end="\n")
    print("%.2f" % VPwm0, end="\t")
    # printOled()
    time.sleep_ms(loopTime)

print("Procedure exited.")

# TODO: loop
    # get VAdc0
    # do myPID.compute and change the voltage
# TODO: show the results in shell
# TODO: show: voltage / current applied, resistance, Kp, Ki, Kd










pwm0.deinit()  # 记得销毁, 不然无法复用

