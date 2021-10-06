from machine import SoftI2C, Pin
from machine import PWM, ADC
import time


PinPwm0: Pin(int) = Pin(12, Pin.OUT, Pin.PULL_UP)
PWM_DUTY_MAX = 1024

try:
    pwm0.deinit()
except (NameError):
    print("pwm0 undefined. redefining...")
pwm0 = PWM(PinPwm0, freq=10000, duty=0)  # 占空比暂时为0
PWM_DUTY_MAX = 1024
PWM_VOLT_MAX = 3.3

while True:
    for i in range(PWM_DUTY_MAX/4):
        pwm0.duty(i*4)
        time.sleep_ms(1)

