from resistance_led_handler import resistance_loop
from test_input import test_input_poll
from test_motor import test_motor3
from test_linear_actuator import test_actuator1
from test_tcs3472 import test_tcs3472
from test_vl53l0x import test_vl53l0x
from test_mfrc522 import test_mfrc522
from test_TMF8x01_get_distance import test_TMF8x01_get_distance
from test_STU_22L_IO_Mode import test_STU_22L_IO_Mode
from test_STU_22L_UART import test_STU_22L_UART
from test_tiny_code_reader import test_tiny_code_reader
from utime import sleep
import motor_control_main as control
import line_sensor_control as sensors
import motor_control_functions as func

print("Welcome to main.py!")
sleep(4)
instructions = ["straight", "left", "straight", "straight", "straight", "straight", "straight", "straight", "straight", "straight", "straight", "straight", "straight","straight","straight","straight","straight", "left", "straight", "right"]
threshold_counter = [0,0,0] #t, l, r
threshold = 2
timeout_counter = 0
timeout_threshold = 3
timeout=False

while True: # continuous loop that controls the entire functionality
    state = sensors.read_sensors()
    turn = "None"
    if timeout == True:
        timeout_counter += 1
        if timeout_counter >= timeout_threshold:
            timeout = False
            timeout_counter = 0
    elif state == (1,0,0,1) and control.mode == "LINE_FOLLOWING": # if the robot is on the line and in line following mode, follow the line
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
    elif state == (1, 1, 1, 0) and control.mode == "LINE_FOLLOWING": # if the robot is at a junction and in line following mode, follow the instructions
        #optional left turn
        threshold_counter = [0, threshold_counter[1]+1, 0]
        if threshold_counter[1] >= threshold:
            threshold_counter = [0, 0, 0]
            if instructions[0] == "left":
                turn = "left"
                instructions.pop(0)
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
            elif instructions[0] == "straight":
                instructions.pop(0)
            timeout=True
    

    control.mode, control.phase = control.update_mode(state, control.mode, control.phase, turn)
    control.update_actions(state, control.mode, control.phase)
    sleep(0.01) # to be adjusted after testing
    print(f"State: {state}, Mode: {control.mode}, Phase: {control.phase}, Next Instruction: {instructions[0] if instructions else 'None'}, Timeout: {timeout}") # for testing/debugging - can be removed later



# Uncomment the test to run
# test_led()
# test_led_pwm()
# test_input_poll()
# test_motor3()
# test_tcs3472()
# test_actuator1()
# test_vl53l0x()
# test_mfrc522()
# test_TMF8x01_get_distance()
# test_STU_22L_IO_Mode()
# test_STU_22L_UART()
# test_tiny_code_reader()

print("main.py Done!")
