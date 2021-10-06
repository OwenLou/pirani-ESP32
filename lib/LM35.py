from machine import Pin, ADC

class LM35:
    """
    A LM35 class, with ADC read and convertor
    temperature range: 0 ~ 100 Celsius
    """
    def __init__(self, pinNum, ADC_SMOOTH_CNT=10):
        self.temperature: double = 26.0
        self.temperature_sum: double = 0.0
        self.adc_data: int = 0
        self.adc_pin = Pin(pinNum, Pin.IN, Pin.PULL_UP)
        self.adc = ADC(self.adc_pin)
        self.adc.atten(ADC.ATTN_0DB)  # 无衰减, 测量范围为0-1V
        self.adc.width(ADC.WIDTH_12BIT)  # 12位宽, 4096
        self.ADC_VOLT_MAX: float = 1.0
        self.ADC_SLOPE_COR: float = 2.32719e-4
        self.ADC_INTER_COR: float = 7.045e-2  # intersection
        #　V = COR_ADC0_SLOPE * adcData + COR_ADC0_INTER
        self.ADC_DATA_MAX: int = 4096  # determined by bit width above
        self.ADC_VOLT_MAX: float = 1.0  # determined by atten n db
        self.ADC_SMOOTH_CNT: int = 10
        return
    def adc_data2V_cor(self):
        if (self.adc_data < 0):
            print("\nin ADC_Data2V(): data = %d out of range! Set to %d" % (self.adc_data, 0))
            self.adc_data = 0
        elif (self.adc_data >= self.ADC_DATA_MAX):
            print("\nin ADC_Data2V(): data = %d out of range! Set to %d" % (self.adc_data, ADC_DATA_MAX-1))
            self.adc_data = self.ADC_DATA_MAX-1
        # 0.07045  2.32719e-4
        return self.ADC_SLOPE_COR * self.adc_data + self.ADC_INTER_COR
    def measure(self):
        self.temperature_sum = 0
        for i in range(self.ADC_SMOOTH_CNT):
            self.adc_data = self.adc.read()
            self.temperature_sum += self.adc_data2V_cor()
        self.temperature = self.temperature_sum / self.ADC_SMOOTH_CNT / 0.01
        return self.temperature


