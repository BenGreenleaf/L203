from machine import I2C, Pin
from sensor_ToF import DistanceSensor
import line_sensor_control as sensors

tof = DistanceSensor()

mode = "block_finding"
phase = None

timer = 0
wall_counter = 0
saved_timer = 0
distance = tof.read_distance()
last_distance = distance
d = 0

#might need a threshold for detecting d being a certain value for a certain time

x = 150 #threshold? may be better to determine state based on jumps between a further and closer distance
xt = 20 #another threshold that needs tuning

def update_distance(new_distance):
    global distance, last_distance, d
    last_distance = distance
    distance = new_distance
    d = distance - last_distance
    return d
    

def update_mode(state, mode, phase):
    global d, timer, saved_timer, wall_counter

    if mode == "block_finding":

        if d >= x:
            timer = 0
            return "block_finding", "obstruction"
        elif d <= -x:
            return "block_finding", "obstruction_end"
        elif phase == "obstruction_end" and timer <= xt:
            wall_counter += 1
            return "block_finding", None
        elif phase == "obstruction" and timer > xt:
             return "block_found", None
        elif phase == "obstruction" and timer <= xt:
            timer += 1
            return "block_finding", "obstruction"
    
    if mode == "block_found" and phase == None:
        if state == (0,1,1,0) and phase == None:
            return "block_found", "reversing"
        if state == (1,1,1,0) and phase == "reversing":
            return "block_found", "turning"
        if state == (1,1,1,1) and phase == "turning":
            return "block_found", "approach"
        
    return mode, phase
    






while True:
    state = sensors.read_sensors()
    new_distance = tof.read_distance()
    d = update_distance(new_distance)
    mode, phase = update_mode(state, mode, phase)
    print(f"distance: {distance}, d: {d}, mode: {mode}, phase: {phase}")
    





print(distance)