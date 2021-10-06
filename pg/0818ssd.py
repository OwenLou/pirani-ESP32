import utime, time
from machine import SoftI2C, Pin
from ssd1306 import SSD1306_I2C

# 显示屏幕, 默认的location为60=0x3c
DIG_WIDTH: int = 8
DIG_HEIGHT: int = 8
SCREEN_WIDTH: int = 128
SCREEN_HEIGHT: int = 64
i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=100000)  # Init i2c 如果是esp32，SCL接22口、SDA接21口
oled = SSD1306_I2C(SCREEN_WIDTH, SCREEN_HEIGHT, i2c)  # 创建oled对象
oled.init_display()  # 清空当前显示

def printOled(rowNum, colNum, myStr):
    oled.fill_rect(DIG_HEIGHT * rowNum, DIG_WIDTH * colNum, DIG_WIDTH * len(myStr), DIG_HEIGHT, 0)
    oled.text(myStr, DIG_HEIGHT * rowNum, DIG_WIDTH * colNum)
    oled.show()
    return

myStr = "a" * int(SCREEN_WIDTH/DIG_WIDTH)

for i in range(SCREEN_HEIGHT/DIG_HEIGHT):
    oled.text(myStr, 0, DIG_WIDTH * i)
    
oled.show()

time.sleep_ms(2000)






