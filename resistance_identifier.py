
from machine import Pin, ADC
from utime import sleep
import grabber_control as grabber

adc = ADC(27)      # ADC0 = GP26
VREF = 3.3
R_KNOWN = 10000.0  # 10k resistor

green_led = Pin(10, Pin.OUT)
red_led = Pin(12, Pin.OUT)  # Pin 27 = GP27 (labelled 33 on the jumper)
yellow_led = Pin(11, Pin.OUT)  # Pin 26 = GP26 (labelled 32 on the jumper)
blue_led = Pin(14, Pin.OUT)  # Pin 22 = GP22 (labelled 31 on the jumper)

tolerance = 0.1

v_red = 1.65 #done
v_blue = 0.045 #done
v_green = 0.29
v_yellow = 2.09 #done

v_upper = 2.11

def identify():
    global raw, v_adc
    raw = adc.read_u16()
    v_adc = raw * VREF / 65535

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
            return "RED"
    elif v_adc > (v_blue-tolerance) and v_adc < (v_blue+tolerance):
            red_led.value(0)
            green_led.value(0)
            yellow_led.value(0)
            blue_led.value(1)
            return "BLUE"
    elif v_adc > (v_green-tolerance) and v_adc < (v_green+tolerance):
            red_led.value(0)
            green_led.value(1)
            yellow_led.value(0)
            blue_led.value(0)
            return "GREEN"
    elif v_adc > (v_yellow-tolerance) and v_adc < (v_yellow+tolerance):
            red_led.value(0)
            green_led.value(0)
            yellow_led.value(1)
            blue_led.value(0)
            return "YELLOW"

avg = 0
n = 0
sum = 0
grabber.grab_open()
sleep(2)
grabber.grab_close()
sleep(1)
while True:
        colour = identify()
        print(colour, v_adc)
        sum += v_adc
        n += 1
        avg = sum / n
        print("Average voltage:", avg)
        sleep(0.1)
    