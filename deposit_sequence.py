import motor_control_functions as motor
import line_sensor_control as sensor
import grabber_control as grabber
from utime import sleep, ticks_ms, ticks_diff
mode = "approach"
block_released = False
speed = 80
error = 0
centre_streak = 0
last_dir = 0
align_ticks = 0
correction_speed = 40
turn_start_ms = None
turn_duration = 1780



def deposit_block_mode(mode, state):
    global turn_start_ms
    if mode == "approach" and state == (0,1,1,0):
        return "approach", False
    elif mode == "approach" and state == (1,1,1,1):
        return "deposit", False
    elif mode == "deposit":
        if block_released:
            return "reversing", False
        else:
            return "deposit", False
    elif mode == "reversing":
        if state in [(0,1,1,0), (0,1,0,0), (0,0,1,0)]:
            turn_start_ms = ticks_ms()
            return "rotate", False
        else:
            return "reversing", False
    elif mode == "rotate":
        if turn_start_ms is None:
            return "rotate", False
        elif ticks_diff(ticks_ms(), turn_start_ms) >= turn_duration:
            return "rotate", True
        else:
            return "rotate", False
    return mode, False

   

def deposit_block_actions(mode, state):
    global block_released
    if mode == "approach":
        print("line following")
        follow_line(state)
    elif mode == "deposit":
        lowered = grabber.lift_down()
        opened = grabber.grab_open()
        block_released = lowered and opened
    elif mode == "reversing":
        motor.set_left(-speed)
        motor.set_right(-speed)
    elif mode == "rotate":
        motor.set_left(-speed)
        motor.set_right(speed)


def reset_deposit_state():
    global mode, block_released, turn_start_ms
    mode = "approach"
    block_released = False
    turn_start_ms = None


def update_error(new_error):
    global error, last_error
    last_error = error
    error = new_error


def follow_line(state):
        global error, last_error, last_dir, align_ticks, centre_streak
        inner = (state[1], state[2])
        if inner == (1,1):
            new_error = 0
        elif inner == (1,0):
            new_error = 1
        elif inner == (0,1):
            new_error = -1
        else:
            new_error = error

        alpha = 0.7
        new_error = alpha*new_error + (1-alpha)*new_error #needs changing

        update_error(new_error)
        base = speed #adjust
        

        if error != 0:
           
            last_dir = error
            # align_ticks = 0 
            centre_streak = 0

            kp = 20
            kd = 5
            correction = kp * error + kd * (error - last_error)
            motor.set_left(int(base - correction))
            motor.set_right(int(base + correction))


        else:
            centre_streak += 1
            if centre_streak == 1 and last_dir != 0:
                align_ticks = 6 #adjust
            if align_ticks > 0:
                motor.set_left(int(base - correction_speed*(-last_dir)))
                motor.set_right(int(base + correction_speed*(-last_dir)))
                align_ticks -= 1
            else:
                motor.set_left(speed)
                motor.set_right(speed)

                if centre_streak > 5:
                    last_dir = 0














#   elif mode == "reversing":
    #     if state in [(0,1,1,0), (0,1,0,0), (0,0,1,0)]:
    #         sleep(0.15)
    #         return "rotate_start", False
    #     else:
    #         return "reversing", False
    # elif mode == "rotate_start":
    #     if state in [ (1,1,1,1), (1,0,0,1)]:
    #         return "rotate_end", False
    #     else:
    #         return "rotate_start", False
    # elif mode == "rotate_end":
    #     if state == (0,1,1,0):
    #         sleep(1.9)
    #         return "rotate_end", True
    #     else:
    #         return "rotate_end", False
    # return mode, False