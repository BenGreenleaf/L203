import motor_control_functions as mcf
import line_sensor_control as lsc
from utime import sleep

import motor_control_functions as mcf
import line_sensor_control as lsc
from utime import sleep

speed = 40

while True: # continuous loop that controls the entire functionality
    state = lsc.read_sensors()
    print(state)
    if state == (0,1,1,0):
        mcf.set_left(speed)
        mcf.set_right(speed)
    elif state in [(0,1,0,0), (1,1,0,0)]:
        mcf.set_right(speed * 0.6)
        mcf.set_left(speed)
    elif state in[(0,0,1,0), (0,0,1,1)]:
        mcf.set_right(speed)
        mcf.set_left(speed * 0.6)
    elif state == (0,0,0,0):
        mcf.stop()
    else:
        mcf.stop()
    sleep(0.01) # to be adjusted after testing