# https://blog.csdn.net/qq_29011249/article/details/104086335
import utime, time, math
from machine import SoftI2C, Pin
from machine import PWM, ADC
import ADS1x15
# from ssd1306 import SSD1306_I2C
# from PID import PID


adI2C = SoftI2C(scl=Pin(25), sda=Pin(26), freq=100000)
print(adI2C.scan())
ad = ADS1x15.ADS1115(adI2C, 0x48, 1)

start = 0
end = 0
CNT = 20
temp = 0
data = [0 for i in range(CNT)]
avg = 0
std = 0
while True:
    avg = 0
    std = 0
    start = utime.ticks_ms()
    for i in range(CNT):
        data[i] = ad.read(rate=4)
        avg += data[i]
    end = utime.ticks_ms()
    print("SPS =", (end - start)/CNT, "ms")
    avg /= CNT
    for i in range(CNT):
        std += (data[i] - avg)**2
        std /= CNT
        std = math.sqrt(std)
    print("avg =", avg,  "std =", std)


