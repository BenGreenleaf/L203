# might eventually be added to main but just wanted to add it in a separate file for now, for organisation

from machine import Pin, PWM
from utime import sleep
from line_sensor_control import read_sensors
import motor_control_functions as motor

speed = 40 #desired speed (just as a variable for now, can update or change depending on mode)
mode = "LINE_FOLLOWING"
phase = None 
last_seen = None
last_error = 0
error = 0

def update_error(new_error):
    global error, last_error
    global last_error
    last_error = error
    error = new_error
    

def update_mode(state, mode, phase): # mode is the higher level state of the robot shown in capitals, state is the line sensor states, phase is the sub state of a mode to protect against changing states mid transition (shown in lower case)
    global last_seen
    
    if mode == "LINE_FOLLOWING":
        if state == (0,0,0,1): 
            return "RIGHT_TURN", "turning"
        elif state == (1,0,0,0):
            return "LEFT_TURN", "turning"
        elif state == (1,0,0,1):
            return "STOP", "turning"
        elif state == (0,0,0,0):
            return "FIND_LINE", None
        # elif state == (1,1,1,1):
        #     return "BLOCK_DEPOSIT", None
        else:
            return "LINE_FOLLOWING", None
        
    elif mode == "RIGHT_TURN":
        if state == (0,1,1,1):
            return "RIGHT_TURN", "exiting"
        elif state == (0,1,1,0):
            return "LINE_FOLLOWING", None
        else:
            return "RIGHT_TURN", "turning"

    elif mode == "LEFT_TURN":
        if state == (1,1,1,0):
            return "LEFT_TURN", "exiting"
        elif state == (0,1,1,0):
            return "LINE_FOLLOWING", None
        else:
            return "LEFT_TURN", "turning"
        
    elif mode == "FIND_LINE":
        if state in [(1,0,0,1), (1,1,1,0), (0,1,1,1)]: #havent included 0110 as if it meets this it is likely to then meet 1001, which is the better state to intiate a rotation
            return "FIND_LINE", "rotating"
        elif state in [(1,0,0,0), (1,1,0,0)]:
            last_seen = "left"
            return "FIND_LINE", "left_found"
        elif state in [(0,0,0,1), (0,0,1,1)]:
            last_seen = "right"
            return "FIND_LINE", "right_found"
        elif state == (0,1,1,0) and phase == "rotating": 
            return "LINE_FOLLOWING", None
        else:
            return "FIND_LINE", None
    
    elif mode == "STOP":
        if state == (1,1,1,1):
            return "STOP", "exiting"
        elif state == (0,1,1,0):
            return "LINE_FOLLOWING", None
        else:
            return "STOP", "turning"

    return mode, phase

def update_actions(state, mode, phase):
    global error, last_error, last_seen

    if mode == "RIGHT_TURN":
        if phase == "turning":
            motor.set_left(speed)
            motor.set_right(-speed)
        elif phase == "exiting":
            motor.set_left(speed)
            motor.set_right(speed)

    elif mode == "LINE_FOLLOWING":
        if state == (0,1,1,0):
            new_error = 0
        elif state == (0,1,0,0):
            new_error = 1
        elif state == (1,1,0,0):
            new_error = 2
        elif state == (0,0,1,0):
            new_error = -1
        elif state == (0,0,1,1):
            new_error = -2
        else:
            new_error = error

        update_error(new_error)

        Kp = 10
        Kd = 5 #no idea whether these are right or not will adjust - test tomorrow

        d_error = error - last_error
        correction = Kp * error + Kd * d_error

        motor.set_left(speed - correction)
        motor.set_right(speed + correction)







        # if phase == None:
        #     motor.set_left(speed)
        #     motor.set_right(speed)
        # elif phase == "right drifted": #currently will be very oscillatory - need to scale the speed changes with how far we are from the line, or ramp the speed changes slowly down to decrease oscillations.
        #     motor.set_right(speed * 0.6)
        #     motor.set_left(speed)
        # elif phase == "left drifted":
        #     motor.set_right(speed)
        #     motor.set_left(speed * 0.6)

    elif mode == "LEFT_TURN":
        if phase == "turning":
            motor.set_left(-speed)
            motor.set_right(speed)
        elif phase == "exiting":
            motor.set_left(speed)
            motor.set_right(speed)

    elif mode == "FIND_LINE": # first draft 
        if phase == None:
            if last_seen == "left":
                motor.set_left(0.5* speed)
                motor.set_right(speed)
            elif last_seen == "right":
                motor.set_left(speed)
                motor.set_right(0.5* speed)
            else:
                motor.set_left(speed)
                motor.set_right(speed * 0.5) #need to add ultrasound sensor inputs here
        elif phase == "rotating":
            motor.set_left(-speed)
            motor.set_right(speed)
        elif phase == "left_found":
            motor.set_left(-speed)
            motor.set_right(speed)
        elif phase == "right_found":
            motor.set_left(speed)
            motor.set_right(-speed)


    elif mode == "STOP": #may need changing because the back might be too long to turn in place - may have to reverse first
        if phase == "turning":
            motor.set_left(speed)
            motor.set_right(-speed)
        elif phase == "exiting":
            motor.set_left(speed)
            motor.set_right(speed)


        

        





