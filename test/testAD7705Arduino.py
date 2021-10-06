import utime, time
from machine import SoftI2C, Pin
from machine import PWM, ADC
from ssd1306 import SSD1306_I2C


pwm0_pin: Pin(int) = Pin(12, Pin.OUT)  # pwm输出初始化
pwm0 = PWM(pwm0_pin, freq=10000, duty=0)  # 最后得到实际的对象
pwm0_duty: int = 0  # 用于存储pwm的duty
PWM_DUTY_MAX: int = 1024  # 应该小于这个数值!
pwm0_V: float = 0.0  # 用于存储输出电压
PWM_VOLT_MAX: float = 3.3  # 输出电压的最大值
pwm0.duty(512)

