from machine import Pin, ADC, PWM
from utime import sleep

left_sensor      = Pin(16, Pin.IN)
frontleft_sensor  = Pin(17, Pin.IN)
right_sensor = Pin(18, Pin.IN)
frontright_sensor     = Pin(19, Pin.IN)

def read_sensors():
    return (left_sensor.value(), frontleft_sensor.value(), frontright_sensor.value(), right_sensor.value())