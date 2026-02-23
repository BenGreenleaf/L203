from machine import Pin, ADC
from utime import sleep

def test_led():

    adc = ADC(26)      # ADC0 = GP26
    VREF = 3.3
    R_KNOWN = 10000.0  # 10k resistor

    green_led = Pin(28, Pin.OUT)
    red_led = Pin(27, Pin.OUT)  # Pin 27 = GP27 (labelled 33 on the jumper)
    yellow_led = Pin(21, Pin.OUT)  # Pin 26 = GP26 (labelled 32 on the jumper)
    blue_led = Pin(22, Pin.OUT)  # Pin 22 = GP22 (labelled 31 on the jumper)

    tolerance = 0.05

    v_red = 1.75
    v_blue = 0.06
    v_green = 0.37
    v_yellow = 2.05

    v_upper = 2.11

    while True:

        raw = adc.read_u16()
        v_adc = raw * VREF / 65535

        print(v_adc)
        if v_adc >= v_upper:
            red_led.value(0)
            green_led.value(0)
            yellow_led.value(0)
            blue_led.value(0)
        elif v_adc > (v_red-tolerance) and v_adc < (v_red+tolerance):
            red_led.value(1)
            green_led.value(0)
            yellow_led.value(0)
            blue_led.value(0)
        elif v_adc > (v_blue-tolerance) and v_adc < (v_blue+tolerance):
            red_led.value(0)
            green_led.value(0)
            yellow_led.value(0)
            blue_led.value(1)
        elif v_adc > (v_green-tolerance) and v_adc < (v_green+tolerance):
            red_led.value(0)
            green_led.value(1)
            yellow_led.value(0)
            blue_led.value(0)
        elif v_adc > (v_yellow-tolerance) and v_adc < (v_yellow+tolerance):
            red_led.value(0)
            green_led.value(0)
            yellow_led.value(1)
            blue_led.value(0)
        sleep(0.5)
if __name__ == "__main__":
    test_led()
