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
d_window = []
window_size = 7
plus_threshold = 100
minus_threshold = -100 #need to tune these



x = 150 #threshold? may be better to determine state based on jumps between a further and closer distance
xt = 20 #another threshold that needs tuning

def update_distance(new_distance):
    global distance, last_distance, d, d_window
    last_distance = distance
    distance = new_distance
    d = distance - last_distance
    d_window.append(d)
    if len(d_window) > window_size:
        d_window.pop(0)
    d_sum = sum(d_window)

    return d_sum
    

def update_mode(state, mode, phase, d_sum):
    global d, timer, saved_timer, wall_counter

    if mode == "block_finding":

        if d_sum >= plus_threshold:
            timer = 0
            return "block_finding", "obstruction"
        elif d_sum <= minus_threshold:
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
    d_sum = update_distance(new_distance)
    mode, phase = update_mode(state, mode, phase, d_sum)
    print(f"distance: {distance}, d: {d}, mode: {mode}, phase: {phase}")
    





print(distance)