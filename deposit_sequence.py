import motor_control_functions as motor
import line_sensor_control as sensor
import grabber_control as grabber
mode = "approach"
block_released = False
speed = 80


def deposit_block_mode(mode, state):
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
            return "rotate_start", False
        else:
            return "reversing", False
    elif mode == "rotate_start":
        if state == (1,0,0,1):
            return "rotate_end", False
        else:
            return "rotate_start", False
    elif mode == "rotate_end":
        if state == (0,1,1,0):
            return "rotate_end", True
        else:
            return "rotate_end", False
    return mode, False

   

def deposit_block_actions(mode, state):
    global block_released
    if mode == "approach":
        motor.set_left(speed)
        motor.set_right(speed)
    elif mode == "deposit":
        grabber.lift_down()
        grabber.grab_open()
        block_released = True
    elif mode == "reversing":
        motor.set_left(-speed)
        motor.set_right(-speed)
    elif mode == "rotate_start" or "rotate_end":
        motor.set_left(-speed)
        motor.set_right(speed)


def reset_deposit_state():
    global mode, block_released
    mode = "approach"
    block_released = False