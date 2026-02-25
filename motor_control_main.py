# might eventually be added to main but just wanted to add it in a separate file for now, for organisation

from machine import Pin, PWM
from utime import sleep
from line_sensor_control import read_sensors
import motor_control_functions as motor

speed = 50 #desired speed (just as a variable for now, can update or change depending on mode)
current_speed = 1
mode = "line following"

#delays for movement/rotation: need to measure distance between detecting the lines and being over the centre point of a corner. replace 0.5 with this distance/angular displacement.
rotation_delay = 0.5 / current_speed # will need to be found from testing - may need to rotate/move just beyond the time when the sensors detect the line in order to travel in straight lines
travelling_delay = 0.5 / current_speed 

def update_mode(state, mode): # mode is the higher level state of the robot, state is the line sensor states
    if mode == "line following":
        if state == (0,0,0,1): 
            return "strict right turn" # strict right turning
        elif state == (1,0,0,0):
            return "strict left turn"
        elif state == (1,0,0,1):
            return "stop"
        elif state == (0,0,0,0):
            return "find line"
        else:
            return "line following"
        
    elif mode == "strict right turn":
        if state == (0,1,1,1):
            return "line following"
        else:
            return "strict right turn"

    elif mode == "strict left turn":
        if state == (1,1,1,0):
            return "line following"
        else:
            return "strict left turn"
        


        
  
    elif state == (1,1,1,0):
        return "optional right turn" # t junction type turning - needs a decision made based on whether blocks are being held or not
    elif state == (0,0,1,1):
        return "strict left turn"
    elif state == (1,0,1,1):
        return "optional left turn"
    elif state == (0,1,1,1):
        return "stopped" #this needs to be edited based on the task: need to find a way to determine whether we are turning or placing/putting blocks (whether we hit the block deposit state beforehand)
    elif state == (1,1,1,1):
        return "block deposit" #the small path extension that indicates the start of the block storage area - needs to then shift to another logic loop for lifting/placing blocks. need to decide whether to turn, which path to then turn down to deposit a specific block. will depend on resistance value
    elif state == (0,0,0,0):
        return "find line" # if it gets lost / when starting


def update_actions(state, mode):
    if mode == "strict right turn":
        motor.turn_right(speed)

    elif mode == "line following":
        if state == (0,1,1,0):
            motor.set_left(speed)
            motor.set_right(speed)
        elif state == (0,1,0,0):
            motor.set_left(speed * 0.8)
        elif state == (0,0,1,0):
            motor.set_right(speed * 0.8)

    elif mode == "strict left turn":
        motor.turn_left(speed)


        

        





