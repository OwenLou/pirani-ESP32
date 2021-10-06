import utime

class PID:
    """
    A PID class, with basic functions
    """
    def __init__(self, Kp=1.0, Ki=1.0, Kd=1.0):
        self.kp: float = Kp
        self.ki: float = Ki
        self.kd: float = Kd
        self.setPoint: float = 0.0
        self.input: float = 0.0
        self.output: float = 0.0
        self.err: float = 0.0
        self.errSum: float = 0.0
        self.lastErr: float = 0.0
        self.nowTime: int = 0  # utime.ticks_ms()
        self.lastTime: int = 0  # utime.ticks_ms()
        self.deltaTime: float = 0.0  # in seconds
        self.cnt: int = 0
        return
    def setTunings(self, Kp=1.0, Ki=1.0, Kd=1.0):
        self.kp: float = Kp
        self.ki: float = Ki
        self.kd: float = Kd
        return
    def allSet(self, mySetPoint):
        self.lastTime = utime.ticks_ms()  # import utime
        self.setPoint = mySetPoint
        self.errSum = 0.0
        self.lastErr = 0.0
        return
    def compute(self, myInput):
        self.input = myInput
        self.err = self.setPoint - self.input
        self.output = 0.0
        self.nowTime = utime.ticks_ms()
        self.deltaTime = (self.nowTime - self.lastTime) / 1000.0
        # kp
        self.output += self.kp * self.err
        # ki
        self.errSum += self.err * self.deltaTime
        self.output += self.ki * self.errSum
        if self.cnt != 0:
            # kd
            self.output += self.kd * (self.err - self.lastErr) / self.deltaTime
        # next time
        self.lastErr = self.err
        self.lastTime = self.nowTime
        self.cnt += 1
        return self.output



