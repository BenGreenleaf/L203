# might eventually be added to main but just wanted to add it in a separate file for now, for organisation

from machine import Pin, PWM
from utime import sleep
from line_sensor_control import read_sensors
import motor_control_functions as motor

speed = 80 #desired speed (just as a variable for now, can update or change depending on mode)
mode = "LINE_FOLLOWING"
phase = None 
last_seen = None
last_error = 0
error = 0
advance_counter = 0
last_dir = 0
align_ticks = 0
centre_streak = 0
reverse_ticks = 0
turning_mode = 1 #one for original two for the new one as of 3.3.26

def update_error(new_error):
    global error, last_error
    last_error = error
    error = new_error
    

def update_mode(state, mode, phase): # mode is the higher level state of the robot shown in capitals, state is the line sensor states, phase is the sub state of a mode to protect against changing states mid transition (shown in lower case)
    global last_seen, advance_counter, reverse_ticks, turning_mode
    
    if mode == "LINE_FOLLOWING":
        if state == (0,0,0,1):
            reverse_ticks = 7
            return "RIGHT_TURN", "reversing" #changed turning to reversing
        elif state == (1,0,0,0):
            reverse_ticks = 7 # added these for second mode. 
            return "LEFT_TURN", "reversing"
        elif state == (1,0,0,1):
            return "STOP", "turning"
        #elif state == (0,0,0,0):
        #    return "FIND_LINE", None
        # elif state == (1,1,1,1):
        #     return "BLOCK_DEPOSIT", None
        else:
            return "LINE_FOLLOWING", None
        
    elif mode == "RIGHT_TURN":
        if turning_mode == 1:
            if phase == "reversing": #can revert this if it doesnt work
                if reverse_ticks > 0:
                    return "RIGHT_TURN", "reversing"
                else:
                    return "RIGHT_TURN", "turning"
                
            if phase == "turning":
                if state == (0,1,1,1):
                    return "RIGHT_TURN", "exiting"
                else:
                    return "RIGHT_TURN", "turning"
            elif phase == "exiting":
                if state == (0,1,1,0):
                    return "LINE_FOLLOWING", None
                else:
                    return "RIGHT_TURN", "exiting"
        
        elif turning_mode == 2:
            if phase == "reversing": 
                if state == (0,1,1,1):
                    return "RIGHT_TURN", "turning_start"
                else: 
                    return "RIGHT_TURN", "reversing"
            elif phase == "turning_start":
                if state in [(0,1,1,0), (0,0,1,0)]:
                    return "RIGHT_TURN", "turning_end"
                else:
                    return "RIGHT_TURN", "turning_start"
            elif phase == "turning_end":
                if state == (0,1,1,1):
                    return "RIGHT_TURN", "exiting"
                else:
                    return "RIGHT_TURN", "turning_end"
            elif phase == "exiting":
                if state == (0,1,1,0):
                    return "LINE_FOLLOWING", None
                else:
                    return "RIGHT_TURN", "exiting"

    elif mode == "LEFT_TURN":
        if turning_mode == 1:
            if phase == "reversing":
                if reverse_ticks > 0:
                    return "LEFT_TURN", "reversing"
                else:
                    return "LEFT_TURN", "turning"
                
            if phase == "turning":
                if state == (1,1,1,0):
                    return "LEFT_TURN", "exiting"
                else:
                    return "LEFT_TURN", "turning"
            elif phase == "exiting":
                if state == (0,1,1,0): # might need to account for what happens when we jump from 0111 to 0100
                    return "LINE_FOLLOWING", None
                else:
                    return "LEFT_TURN", "exiting"
                
        elif turning_mode == 2:
            if phase == "reversing": 
                if state == (1,1,1,0):
                    return "LEFT_TURN", "turning_start"
                else: 
                    return "LEFT_TURN", "reversing"
            elif phase == "turning_start":
                if state in [(0,1,1,0), (0,1,0,0)]:
                    return "LEFT_TURN", "turning_end"
                else:
                    return "LEFT_TURN", "turning_start"
            elif phase == "turning_end":
                if state == (1,1,1,0):
                    return "LEFT_TURN", "exiting"
                else:
                    return "LEFT_TURN", "turning_end"
            elif phase == "exiting":
                if state == (0,1,1,0):
                    return "LINE_FOLLOWING", None
                else:
                    return "LEFT_TURN", "exiting"
        
    # elif mode == "FIND_LINE":

    #     if state == (1,1,1,0):
    #         advance_counter = 0
    #         return "FIND_LINE", "diagonal_approach_right_advance"
    #     elif state == (0,1,1,1):
    #         advance_counter = 0
    #         return "FIND_LINE", "diagonal_approach_left_advance"
    #     elif state in [(1,0,0,0), (1,1,0,0)]:
    #         last_seen = "left"
    #         return "FIND_LINE", "left_found"
    #     elif state in [(0,0,0,1), (0,0,1,1)]:
        #     last_seen = "right"
        #     return "FIND_LINE", "right_found"
        
        # if phase in ["diagonal_approach_right_advance", "diagonal_approach_left_advance"]:
        #     advance_counter += 1
        #     if advance_counter > 4:   # tune this
        #         advance_counter = 0
        #         if phase == "diagonal_approach_right_advance":
        #             return "FIND_LINE", "diagonal_approach_right_rotate"
        #         else:
        #             return "FIND_LINE", "diagonal_approach_left_rotate"
        #     return "FIND_LINE", phase
        
        # elif phase in ["diagonal_approach_right_rotate", "diagonal_approach_left_rotate"]:
        #     if state == (0,1,1,0):
        #         return "LINE_FOLLOWING", None
        #     return "FIND_LINE", phase
        
        # elif phase == "advance":
        #     advance_counter += 1
        #     if advance_counter > 7: #CHECK NUMBER AND EDIT VIA TESTING
        #         advance_counter = 0
        #         return "LINE_FOLLOWING", None
        #     return "FIND_LINE", "advance"

        # else:
        #     return "FIND_LINE", None
    
    elif mode == "STOP":
        if state == (1,1,1,1):
            return "STOP", "exiting"
        elif state == (0,1,1,0):
            return "LINE_FOLLOWING", None
        else:
            return "STOP", "turning"

    return mode, phase

def update_actions(state, mode, phase):
    global error, last_error, last_seen, advance_counter, last_dir, align_ticks, centre_streak, reverse_ticks

    turn_speed = 60 # test and adjust
    correction_speed = 10

#variation 1 of the turning code - old

    # if mode == "RIGHT_TURN":
    #     if phase == "turning":
    #         motor.set_left(0.95*speed)
    #         motor.set_right(-1.2*speed)
    #     elif phase == "exiting":
    #         motor.set_left(speed)
    #         motor.set_right(speed)


    # elif mode == "LEFT_TURN":
    #     if phase == "turning":
    #         motor.set_left(-1.2*speed)
    #         motor.set_right(1.05*speed)
    #     elif phase == "exiting":
    #         motor.set_left(speed)
    #         motor.set_right(speed)

# variation 2 of turning code


    if mode == "RIGHT_TURN":
        if turning_mode == 1:
            if phase == "reversing":
                if reverse_ticks > 0:
                    motor.set_left(int(-0.7*speed))
                    motor.set_right(int(-0.7*speed))
                    reverse_ticks -= 1
            elif phase == "turning":
                motor.set_left(1*turn_speed)
                motor.set_right(-1.2*turn_speed)
            elif phase == "exiting":
                motor.set_left(speed)
                motor.set_right(speed)
        if turning_mode == 2:
            if phase == "reversing":
                motor.set_left(int(-0.7*speed))
                motor.set_right(int(-0.7*speed))
            elif phase == "turning_start":
                motor.set_left(turn_speed)
                motor.set_right(-turn_speed)
            elif phase == "turning_end":
                motor.set_left(turn_speed)
                motor.set_right(-turn_speed) #could even adjust the speed of these values if the curve is too large or too small
            elif phase == "exiting":
                motor.set_left(speed)
                motor.set_right(speed)


    elif mode == "LEFT_TURN":
        if turning_mode == 1:
            if phase == "reversing":
                if reverse_ticks > 0:
                    motor.set_left(int(-0.7*speed))
                    motor.set_right(int(-0.7*speed))
                    reverse_ticks -= 1
            elif phase == "turning":
                motor.set_left(-1.2*turn_speed)
                motor.set_right(1.05*turn_speed)
            elif phase == "exiting":
                motor.set_left(speed)
                motor.set_right(speed) 
        
        if turning_mode == 2:
            if phase == "reversing":
                motor.set_left(int(-0.7*speed))
                motor.set_right(int(-0.7*speed))
            if phase == "turning_start":
                motor.set_left(-turn_speed)
                motor.set_right(turn_speed)
            if phase == "turning_end": #phases look identical but need to separate them as states are contained within each that need to be interpreted differenty
                motor.set_left(-turn_speed)
                motor.set_right(turn_speed)
            if phase == "exiting":
                motor.set_left(speed)
                motor.set_right(speed)


    elif mode == "LINE_FOLLOWING":
        inner = (state[1], state[2])
        if inner == (1,1):
            new_error = 0
        elif inner == (1,0):
            new_error = 1
        elif inner == (0,1):
            new_error = -1
        else:
            new_error = error

        update_error(new_error)
        base = speed #adjust
        if error != 0:
            last_dir = error
            align_ticks = 0 
            centre_streak = 0

            kp = 20
            motor.set_left(int(base - kp * error))
            motor.set_right(int(base + kp * error))

        else:
            centre_streak += 1
            if centre_streak == 1 and last_dir != 0:
                align_ticks = 15 #adjust
            if align_ticks > 0:
                motor.set_left(int(base - correction_speed*(-last_dir)))
                motor.set_right(int(base + correction_speed*(-last_dir)))
                align_ticks -= 1
            else:
                motor.set_left(speed)
                motor.set_right(speed)

                if centre_streak > 5:
                    last_dir = 0







    elif mode == "STOP": #may need changing because the back might be too long to turn in place - may have to reverse first
        if phase == "turning":
            motor.set_left(speed)
            motor.set_right(-speed)
        elif phase == "exiting":
            motor.set_left(speed)
            motor.set_right(speed)


        
    # elif mode == "FIND_LINE": # first draft 
    #     if phase == None:
    #         if last_seen == "left":
    #             motor.set_left(0.5* speed)
    #             motor.set_right(speed)
    #         elif last_seen == "right":
    #             motor.set_left(speed)
    #             motor.set_right(0.5* speed)
    #         else:
    #             motor.set_left(speed)
    #             motor.set_right(speed * 0.5) #need to add ultrasound sensor inputs here
    #     elif phase == "advance":
    #         motor.set_left(0.7 * speed)
    #         motor.set_right(0.7 * speed)
    #     elif phase == "left_found":
    #         motor.set_left(-speed)
    #         motor.set_right(speed)
    #     elif phase == "right_found":
    #         motor.set_left(speed)
    #         motor.set_right(-speed)
    #     elif phase in ["diagonal_approach_right_advance", "diagonal_approach_left_advance"]:
    #         creep = 0.7 * speed
    #         motor.set_left(creep)
    #         motor.set_right(creep)
        
    #     elif phase == "diagonal_approach_right_rotate":
    #         motor.set_left(speed)
    #         motor.set_right(-speed)
    #     elif phase == "diagonal_approach_left_rotate":
    #         motor.set_left(-speed)
    #         motor.set_right(speed)
        





