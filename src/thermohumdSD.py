from machine import Pin, SoftI2C
import time
from sht3x import SHT30
from ssd1306 import SSD1306_I2C


sensor = SHT30(scl_pin=22, sda_pin=21, delta_temp=-3, i2c_address=0x44)


# i2c = SoftI2C(scl=Pin(5), sda=Pin(4), freq=100000)       #Init i2c  如果是esp8266，SCL接5口、SDA接4口
i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=100000)  #Init i2c  如果是esp32，SCL接22口、SDA接21口
oled = SSD1306_I2C(128, 64, i2c) #创建oled对象

while True:
    oled.init_display()
    temperature, humidity = sensor.measure()
    oled.text(str(temperature), 0, 0)
    oled.text(str(humidity), 0, 10)
    oled.show()
    time.sleep_ms(2000)
    

