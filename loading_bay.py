from machine import I2C, Pin
from sensor_ToF import VL53L0X
import line_sensor_control as sensors

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)

tof = VL53L0X(i2c)

timer = 0
wall_counter = 0
saved_timer = 0

#might need a threshold for detecting d being a certain value for a certain time

x = 0 #threshold? may be better to determine state based on jumps between a further and closer distance
xt = 0 #another threshold that needs tuning

def update_distance(new_distance):
    global distance, last_distance, d
    last_distance = distance
    distance = new_distance
    d = distance - last_distance
    

def update_mode(state, mode, phase):
    global d, timer, saved_timer, wall_counter

    if mode == "block_finding" and phase == None:

        if d >= x:
            timer = 0
            return "block_finding", "obstruction"
        elif d <= -x:
            return "block_finding", "obstruction_end"
        elif phase == "obstruction_end" and timer <= xt:
            wall_counter += 1
            return "block_finding", None
        elif phase == "obstruction" and timer > xt:
            mode = "block found"
        elif phase == "obstruction" and timer <= xt:
            timer += 1
            return "block finding", "obstruction"
    
    if mode == "block_found" and phase == None:
        if state == (0,1,1,0) and phase == None:
            return "block_found", "reversing"
        if state == (1,1,1,0) and phase == "reversing":
            return "block_found", "turning"
        if state == (1,1,1,1) and phase == "turning":
            return "block_found", "approach"

    






while True:
    state = sensors.read_sensors()
    distance = tof.read_mm()





print(distance)