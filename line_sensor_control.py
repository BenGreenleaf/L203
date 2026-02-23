from machine import Pin, ADC, PWM
from utime import sleep

front_sensor      = Pin(16, Pin.IN)
right_sensor  = Pin(17, Pin.IN)
back_sensor = Pin(18, Pin.IN)
left_sensor     = Pin(19, Pin.IN)

def read_sensors():
    return (front_sensor.value(), right_sensor.value(), back_sensor.value(), left_sensor.value())