import motor_control_functions as mcf
import line_sensor_control as lsc
from utime import sleep

while True: # continuous loop that controls the entire functionality
    speed = 20
    mcf.forward(speed)
    state = lsc.read_sensors()
    print(state)
    if state == (0,1,1,0):
        mcf.forward(speed)
    elif state == (0,1,0,0):
        mcf.set_left(speed * 0.8)
        mcf.set_right(speed)
    elif state == (0,0,1,0):
        mcf.set_left(speed)
        mcf.set_right(speed * 0.8)
    elif state == (0,0,0,0):
        mcf.stop()
    sleep(0.01) # to be adjusted after testing