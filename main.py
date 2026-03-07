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
import network
import socket
import time
from machine import Pin

green_led = Pin(10, Pin.OUT)
red_led = Pin(12, Pin.OUT)
yellow_led = Pin(11, Pin.OUT)
blue_led = Pin(14, Pin.OUT)

print("Welcome to main.py!")

sleep(4)
#instructions = ["straight", "left", "straight", "straight", "straight", "straight", "straight", "straight", "straight", "straight", "straight", "straight", "straight", "straight","straight","straight","straight", "left", "straight", "right"]
instructions = ["right", "straight", "straight", "straight", "straight", "straight", "straight", "straight", "straight_drop_off", "left", "straight", "left", "straight", "straight", "straight", "straight","straight","straight","straight", "left", "straight", "right"]
threshold_counter = [0,0,0] #t, l, r
threshold = 3
timeout_counter = 0
timeout_threshold = 12
timeout=False
turn_delay=0

while True: # continuous loop that controls the entire functionality
    state = sensors.read_sensors()
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
    elif state == (1,1,1,1) and control.mode == "LINE_FOLLOWING" and instructions[0] == "straight_drop_off": # if the robot is at a junction and in line following mode, follow the instructions
        turn = "None"
        instructions.pop(0)
        control.drop_off_ready = True

    control.mode, control.phase= control.update_mode(state, control.mode, control.phase, turn)
    control.update_actions(state, control.mode, control.phase)
    if instructions[0] == "None":
        green_led.value(1)
        red_led.value(1)
        yellow_led.value(1)
        blue_led.value(1)
    elif instructions[0] == "straight":
        green_led.value(1)
        red_led.value(0)
        yellow_led.value(0)
        blue_led.value(0)
    elif instructions[0] == "left":
        green_led.value(0)
        red_led.value(1)
        yellow_led.value(0)
        blue_led.value(0)
    elif instructions[0] == "right":
        green_led.value(0)
        red_led.value(0)
        yellow_led.value(1)
        blue_led.value(0)
    sleep(0.01) # to be adjusted after testing
    print((
    f"State: {state}, "
    f"Mode: {control.mode}, "
    f"Phase: {control.phase}, "
    f"Next Instruction: {instructions[0] if instructions else 'None'}, "
    f"Timeout: {timeout}, "
    f"Remaining: {len(instructions)}"
))


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
