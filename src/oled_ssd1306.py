# Esp8266的Pin5一般指芯片上的D1针脚、Pin4一般是指D2针脚

from machine import SoftI2C, Pin
from ssd1306 import SSD1306_I2C
import time


# i2c = SoftI2C(scl=Pin(25), sda=Pin(26), freq=100000)  #Init i2c, 为了后续改进方便, 使用了hardwareI2C的指定接口
i2c = SoftI2C(scl=Pin(18), sda=Pin(19), freq=100000)  #Init i2c, 为了后续改进方便, 使用了hardwareI2C的指定接口
oled = SSD1306_I2C(128, 64, i2c) #创建oled对象

# 我们的库和hardwareI2C并不配套, 所以下面的代码并不能用
# i2c = I2C(0, scl=Pin(18), sda=Pin(19), freq=100000)  #Init i2c  如果是esp32，SCL接22口、SDA接21口
# oled = SSD1306_I2C(128, 64, i2c) #创建oled对象

oled.rect(0, 0, 127, 63, 1)
oled.show()

# oled.text("SSD1306 Test",0,0)         #在指定坐标显示内容
# oled.text("12345678ABCDEFGH",0,16)
# oled.text("abcdefgh,.?!@#$%",0,26)
oled.text("123456789012345\n123456789012345",0,0)

# 功能演示：
oled.pixel(127,0,1)              #画点：  X坐标，y坐标
oled.hline(0,40,15,1)            #画横线： X坐标，y坐标，宽度多少像素，颜色1
oled.vline(20,40,15,1)           #画竖线： X坐标，y坐标，高度多少像素，颜色1
oled.line(32,40, 48,55, 1)       #画两点之间的线：起点Xy坐标，终点xy坐标，颜色1
oled.rect(60,40, 20,15, 1)       #画矩形： X坐标，y坐标，宽度，调试，颜色1
oled.fill_rect(84,40, 20,15, 1)  #画矩形并填充：  X坐标，y坐标，宽度，调试，颜色1
#lcd.scroll(10,10)              #图像复制移位： 右移几个像素、下移几个像素

#正式显示
oled.show()

