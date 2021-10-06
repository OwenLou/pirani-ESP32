from machine import SoftI2C, Pin
from MCP4725 import MCP4725, MCP4725_BUS_ADDRESS, MCP4725_POWER_DOWN_MODE
import math, utime

mcp4725_i2c = SoftI2C(scl=Pin(25), sda=Pin(26), freq=100000)

dac0 = MCP4725(mcp4725_i2c, MCP4725_BUS_ADDRESS[0])

r = 0
# while (True):
#     dac0.write(int(4096 * math.sin(r * math.pi)))
#     r += 0.001
#     while (r > 1):
#         r = 0
#     utime.sleep_ms(5)
while (True):
    dac0.write(r)
    r += 1
    if (r >= 4096):
        r = 0
    utime.sleep_ms(5)


