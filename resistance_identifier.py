
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

length = 10

v_red = 1.56 #done
v_blue = 0.04 #done
v_green = 0.2
v_yellow = 2.08 #new


def identify():
    global raw, v_adc
    vals = [0,0,0,0] #r, b, y, g

    for i in range(0, length):
           

        raw = adc.read_u16()
        v_adc = raw * VREF / 65535

        print(v_adc)

        if v_adc > (v_red-tolerance) and v_adc < (v_red+tolerance):
                red_led.value(1)
                green_led.value(0)
                yellow_led.value(0)
                blue_led.value(0)
                vals = [vals[0]+1, vals[1], vals[2], vals[3]]
        elif v_adc > (v_blue-tolerance) and v_adc < (v_blue+tolerance):
                red_led.value(0)
                green_led.value(0)
                yellow_led.value(0)
                blue_led.value(1)
                vals = [vals[0], vals[1]+1, vals[2], vals[3]]

        elif v_adc > (v_green-tolerance) and v_adc < (v_green+tolerance):
                red_led.value(0)
                green_led.value(1)
                yellow_led.value(0)
                blue_led.value(0)
                vals = [vals[0], vals[1], vals[2], vals[3]+1]
        elif v_adc > (v_yellow-tolerance) and v_adc < (v_yellow+tolerance):
                red_led.value(0)
                green_led.value(0)
                yellow_led.value(1)
                blue_led.value(0)
                vals = [vals[0], vals[1], vals[2]+1, vals[3]]

        sleep(0.03)
    print(vals)
    if max(vals) == vals[0]:
        red_led.value(1)
        green_led.value(0)
        yellow_led.value(0)
        blue_led.value(0)
        return "RED"
    elif max(vals) == vals[1]:
        red_led.value(0)
        green_led.value(0)
        yellow_led.value(0)
        blue_led.value(1)
        return "BLUE"
    elif max(vals) == vals[2]:
        red_led.value(0)
        green_led.value(0)
        yellow_led.value(1)
        blue_led.value(0)
        return "YELLOW"
    elif max(vals) == vals[3]:
        red_led.value(0)
        green_led.value(1)
        yellow_led.value(0)
        blue_led.value(0)
        return "GREEN"
    else:
        red_led.value(1)
        green_led.value(0)
        yellow_led.value(0)
        blue_led.value(0)
        return "RED"
             
