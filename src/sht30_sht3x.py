from machine import Pin, SoftI2C
import time
from sht3x import SHT30


# i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=400000)
sensor = SHT30(scl_pin=22, sda_pin=21, delta_temp=-3, i2c_address=0x44)
temperature, humidity = sensor.measure()
print(temperature, humidity)

