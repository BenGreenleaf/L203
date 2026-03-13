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
import deposit_sequence as deposit
import route_executor as route
import task_control as task
import path_finding as path
import grabber_control as grabber
import motor_control_functions as mc
import loading_bay as loading
import network
import socket
import time
from machine import Pin, reset
import resistance_identifier as res
#import loading_bay as loading

reset_button = Pin(22, Pin.IN, Pin.PULL_UP)
green_led = Pin(10, Pin.OUT)
red_led = Pin(12, Pin.OUT)
blue_led = Pin(14, Pin.OUT)
print("Welcome to main.py!")

#instructions = ["straight", "left", "straight", "straight", "straight", "straight", "straight", "straight", "straight", "straight", "straight", "straight", "straight", "straight","straight","straight","straight", "left", "straight", "right"]
# instructions = ["right", "straight", "straight", "straight", "straight", "straight", "straight", "straight", "straight_drop_off", "left", "straight", "left", "straight", "straight", "straight", "straight","straight","straight","straight", "left", "straight", "right"]
instructions = []
current_node = 2
current_orientation = "east"
route_loaded = False
goal = None
path_nodes = None
total_dist = None
colour = None
scan_started = False
scan_done = False
collected = False
start = True

# grabber.grab_open()
# grabber.lift_down_top_rack()
# grabber.grab_close()
# grabber.lift_up()

# sleep(2)

if reset_button.value() == 0:
    print("reset pressed")
    sleep(0.2)
    reset()


while True: # continuous loop that controls the entire functionality
    state = sensors.read_sensors()
    step = task.get_current_step()
    step_type = step["type"]
    #print(step)
    if step_type == "NAVIGATE":
        if not route_loaded:
            print("loading route")
            goal = task.get_current_goal()
            print(goal)
            path_nodes, instructions, total_dist = path.plan_route(current_node, goal, current_orientation)
            if start == True and instructions:
                instructions = instructions[1:] # skip the first instruction as the robot is already facing the correct direction for the first move
                start = False
            elif task.get_previous_step()['type'] == "DEPOSIT" and instructions:
                instructions = instructions[1:]
                
            print(f"{instructions}--------------------------------------------------------------------------------------------------------------")
            route_loaded = True
        
        if instructions and instructions[0] == "straight":
            green_led.value(1)
            red_led.value(0)
            blue_led.value(0)
        elif instructions and instructions[0] == "left":
            green_led.value(0)
            red_led.value(1)
            blue_led.value(0)
        elif instructions and instructions[0] == "right":
            green_led.value(0)
            red_led.value(0)
            blue_led.value(1)

        turn = route.turn_decisions(instructions, state)
        control.mode, control.phase= control.update_mode(state, control.mode, control.phase, turn)
        control.update_actions(state, control.mode, control.phase)
        print(control.mode, control.phase, turn)

        if not instructions and control.mode == "LINE_FOLLOWING": #check this condition
            print("goal reached")
            if path_nodes is not None and len(path_nodes) >= 2:
                current_node = goal
                u = path_nodes[-2]
                v = path_nodes[-1]
                _dist, current_orientation = path.graph[u][v]
                print("advancing step")
                task.advance_stage()
                print(step)
                route_loaded = False
        
    elif step_type == "SCAN":
        print('entered scan')
        if not scan_started:
           loading.reset_scan_state()
           scan_type = step["name"]

           if scan_type == "scan_1" or "scan_3":
               sensor = "left"
               scan_started = True
           elif scan_type == "scan_2" or "scan_4":
               sensor = "right"
               scan_started = True
       
        if scan_started:
            if not scan_done:
               scan_done = loading.scanning_tick(state, sensor)
               print(f"scanning, sensor: {sensor}, scan_done: {scan_done}")
            else:
                collected = loading.collection_tick(state)
        if collected:
            print("collection done")        
        # colour = res.identify()
        # if colour == "RED":
        #     task.set_next_deposit_goal(6)
        # elif colour == "BLUE": #set node and positioning as east if in lower right, west if in lower left (loading bay will leave the robot facing outward)
        #     task.set_next_deposit_goal(44)
        # elif colour == "GREEN":
        #     task.set_next_deposit_goal(43)
        # elif colour == "YELLOW":
        #     task.set_next_deposit_goal(4)
        # task.advance_stage()
        # route_loaded = False
        # scan_started = False


    elif step_type == "DEPOSIT":
        
        deposit.mode, deposit_done = deposit.deposit_block_mode(deposit.mode, state)
        deposit.deposit_block_actions(deposit.mode, state)
        print(f"deposit, mode:{deposit.mode} phase:{state}")
        if deposit_done:
            colour = None
            current_orientation = "north"
            task.advance_stage()
            route_loaded = False
            deposit.reset_deposit_state()

    

    elif step_type == "STOP":
        mc.set_left(80)
        mc.set_right(80)
        sleep(2)
        mc.set_left(0)
        mc.set_right(0)

    sleep(0.01)

#     if instructions[0] == "None":
#         green_led.value(1)
#         red_led.value(1)
#         yellow_led.value(1)
#         blue_led.value(1)
#     elif instructions[0] == "straight":
#         green_led.value(1)
#         red_led.value(0)
#         yellow_led.value(0)
#         blue_led.value(0)
#     elif instructions[0] == "left":
#         green_led.value(0)
#         red_led.value(1)
#         yellow_led.value(0)
#         blue_led.value(0)
#     elif instructions[0] == "right":
#         green_led.value(0)
#         red_led.value(0)
#         yellow_led.value(1)
#         blue_led.value(0)
#     sleep(0.01) # to be adjusted after testing
# #     # print((
# #     # f"State: {state}, "
# #     # f"Mode: {control.mode}, "
# #     # f"Phase: {control.phase}, "
# #     # f"Next Instruction: {instructions[0] if instructions else 'None'}, "
# #     # f"Timeout: {timeout}, "
# #     # f"Remaining: {len(instructions)}"
# # ))


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
