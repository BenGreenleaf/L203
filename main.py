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
import route_executor as route
import task_control as task
import path_finding as path
import network
import socket
import time
from machine import Pin
import resistance_identifier as res

green_led = Pin(10, Pin.OUT)
red_led = Pin(12, Pin.OUT)
yellow_led = Pin(11, Pin.OUT)
blue_led = Pin(14, Pin.OUT)

print("Welcome to main.py!")

sleep(4)
#instructions = ["straight", "left", "straight", "straight", "straight", "straight", "straight", "straight", "straight", "straight", "straight", "straight", "straight", "straight","straight","straight","straight", "left", "straight", "right"]
# instructions = ["right", "straight", "straight", "straight", "straight", "straight", "straight", "straight", "straight_drop_off", "left", "straight", "left", "straight", "straight", "straight", "straight","straight","straight","straight", "left", "straight", "right"]
instructions = []
current_node = 3
current_orientation = "east"
route_loaded = False
goal = None
path_nodes = None
total_dist = None
colour = None


while True: # continuous loop that controls the entire functionality
    state = sensors.read_sensors()
    step = task.get_current_step()
    step_type = step["type"]
    print(step)
    if step_type == "NAVIGATE":
        if not route_loaded:
            print("loading route")
            goal = task.get_current_goal()
            print(goal)
            path_nodes, instructions, total_dist = path.plan_route(current_node, goal, current_orientation)
            print(instructions)
            route_loaded = True

        turn = route.turn_decisions(instructions, state)
        control.mode, control.phase= control.update_mode(state, control.mode, control.phase, turn)
        control.update_actions(state, control.mode, control.phase)
        print(control.mode, control.phase)

        if not instructions and control.mode == "LINE_FOLLOWING": #check this condition
            print("goal reached")
            if path_nodes is not None and len(path_nodes) >= 2:
                current_node = goal
                u = path_nodes[-2]
                v = path_nodes[-1]
                _dist, current_orientation = path.graph[u][v]
                print("advancing step")
                task.advance_stage()
                route_loaded = False
        
    elif step_type == "SCAN":
        ... #insert loading bay script
        colour = res.identify()
        if colour == "RED":
            task.set_next_deposit_goal(6)
        elif colour == "BLUE":
            task.set_next_deposit_goal(44)
        elif colour == "GREEN":
            task.set_next_deposit_goal(43)
        elif colour == "YELLOW":
            task.set_next_deposit_goal(4)
        task.advance_stage()
        route_loaded = False


    elif step_type == "DEPOSIT":
        ...
        colour = None
        task.advance_stage()
        route_loaded = False

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
