import motor_control_main as control
import line_sensor_control as sensors

threshold_counter = [0,0,0] #t, l, r
threshold = 3
timeout_counter = 0
timeout_threshold = 12
timeout=False
turn_delay=0


def turn_decisions(instructions, state):
    global threshold_counter, timeout_counter, timeout
    turn = "None"
    turn_delay=0
    
    if timeout == True:
        timeout_counter += 1
        if timeout_counter >= timeout_threshold:
            timeout = False
            timeout_counter = 0
    elif state  == (1,0,0,1) and control.mode == "LINE_FOLLOWING": # if the robot is on the line and in line following mode, follow the line
        threshold_counter = [threshold_counter[0]+1, 0, 0]
        #T-Junction
        if threshold_counter[0] >= threshold:
            threshold_counter = [0, 0, 0]
            if instructions[0] == "right":
                turn = "right"
                instructions.pop(0)
            elif instructions[0] == "left":
                turn = "left"
                instructions.pop(0)
            timeout = True
    elif state in [(1, 1, 1, 0), (1,1,0,0)] and control.mode == "LINE_FOLLOWING": # if the robot is at a junction and in line following mode, follow the instructions
        #optional left turn
        threshold_counter = [0, threshold_counter[1]+1, 0]
        if threshold_counter[1] >= threshold:
            threshold_counter = [0, 0, 0]
            if instructions[0] == "left":
                turn = "left"
                instructions.pop(0)
                control.optional_left_turn=True
            elif instructions[0] == "straight":
                instructions.pop(0)
            timeout=True
    elif state == (0, 1, 1, 1) and control.mode == "LINE_FOLLOWING": # if the robot is at a junction and in line following mode, follow the instructions
        #optional right turn
        threshold_counter = [0, 0, threshold_counter[2]+1]
        if threshold_counter[2] >= threshold:
            threshold_counter = [0, 0, 0]
            if instructions[0] == "right":
                turn = "right"
                instructions.pop(0)
                control.optional_right_turn=True
            elif instructions[0] == "straight":
                instructions.pop(0)
            timeout=True
    elif state == (1,1,1,1) and control.mode == "LINE_FOLLOWING" and instructions[0] == "straight_drop_off": # if the robot is at a junction and in line following mode, follow the instructions (why 1111?)
        turn = "None"
        instructions.pop(0)
        control.drop_off_ready = True
    
    return turn