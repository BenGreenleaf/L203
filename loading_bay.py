from machine import I2C, Pin
from sensor_ToF import DistanceSensor
import line_sensor_control as sensors
from utime import sleep
import motor_control_functions as motor

frontsensor = DistanceSensor(111)
leftsensor = DistanceSensor(110)
rightsensor = DistanceSensor(100) #need to find ids for each of these sensors

mode = "block_finding"
phase = None

speed = 80
timer = 0
wall_counter = 0
saved_timer = 0
window_size = 7
plus_threshold = 100
minus_threshold = -100 #need to tune these
scanning_done = False
collection_done = False
front_threshold = 20
front_timer = 0 
block_collected = False
block_lifted = False
error = 0
centre_streak = 0
last_dir = 0
align_ticks = 0
correction_speed = 40

sensor_states = {
    "front": {
        "distance": frontsensor.read_distance(),
        "last_distance": frontsensor.read_distance(),
        "d": 0,
        "d_window": [],
        "d_sum": 0
    },
    "left": {
        "distance": leftsensor.read_distance(),
        "last_distance": leftsensor.read_distance(),
        "d": 0,
        "d_window": [],
        "d_sum": 0
    },
    "right": {
        "distance": rightsensor.read_distance(),
        "last_distance": rightsensor.read_distance(),
        "d": 0,
        "d_window": [],
        "d_sum": 0
    }
}

x = 150 #threshold? may be better to determine state based on jumps between a further and closer distance
xt = 20 #another threshold that needs tuning

def update_error(new_error):
    global error, last_error
    last_error = error
    error = new_error

def update_distance(sensor, new_distance):
    global sensor_states
    distance_state = sensor_states[sensor]

    distance_state["last_distance"] = distance_state["distance"]
    distance_state["distance"] = new_distance
    
    distance_state["d"] = distance_state["distance"] - distance_state["last_distance"]
    distance_state["d_window"].append(distance_state["d"])
    if len(distance_state["d_window"]) > window_size:
        distance_state["d_window"].pop(0)
    distance_state["d_sum"] = sum(distance_state["d_window"])

    return distance_state["d_sum"]
    

def scanning_mode(state, mode, phase, d_sum):
    global timer, saved_timer, wall_counter

    if mode == "block_finding":

        if d_sum >= plus_threshold:
            timer = 0
            return "block_finding", "obstruction", False
        elif d_sum <= minus_threshold:
            return "block_finding", "obstruction_end", False
        elif phase == "obstruction_end" and timer <= xt:
            wall_counter += 1
            return "block_finding", None, False
        elif phase == "obstruction" and timer > xt:
             return "block_found", None, False
        elif phase == "obstruction" and timer <= xt:
            timer += 1
            return "block_finding", "obstruction", False
    
    if mode == "block_found" and phase == None:
        if state == (0,1,1,0) and phase == None:
            return "block_found", "reversing", False
        if state == (1,1,1,0) and phase == "reversing":
            return "block_found", "turning", False
        if state == (1,1,1,1) and phase == "turning":
            return "block_found", "approach", True
        
    return mode, phase, False

def scanning_actions():
    ...
    
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
        new_error = alpha*new_error + (1-alpha)*new_error

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
    

def collection_actions(mode, phase, state):
    global error, last_error, last_dir, align_ticks, centre_streak
    if mode == "block_found" or mode == "collecting" and phase == "approach": #literally copied line following code because it is much easier than trying to navigate through to line following from this function
        follow_line(state)
    elif mode == "collecting" and phase == "lowering":
        ...

    
    
def collection_mode(state, mode, phase, d):
    global front_timer
    if mode == "block_found" and phase == "approach":
        front_timer = 0
        return "collecting", "approach", False
    
    if mode == "collecting":
        if phase == "approach":
            if d > front_threshold:
                return "collecting", "approach", False
            elif d <= front_threshold:
                if front_timer < 4:
                    front_timer += 1
                    return "collecting", "approach", False
                elif front_timer > 4:
                    return "collecting", "lowering", False
        
        elif phase == "lowering":
            if block_collected == False:
                return "collecting", "lowering", False
            elif block_collected == True:
                return "collecting", "lifting", False
            
        elif phase == "lifting":
            if block_lifted == False:
                return "collecting", "lifting", False
            elif block_lifted == True:
                return "collecting", "reversing", False
            
        elif phase == "reversing":
            sleep(2) #check
            return "turning", "turn_start"
        
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
        


        
        
               
        
            
    

        

    ...

    
    

def reset_scan_state():
    global sensor_states, scanning_done, front_timer, timer, wall_counter
    sensor_states = {
    "front": {
        "distance": frontsensor.read_distance(),
        "last_distance": frontsensor.read_distance(),
        "d": 0,
        "d_window": [],
        "d_sum": 0
    },
    "left": {
        "distance": leftsensor.read_distance(),
        "last_distance": leftsensor.read_distance(),
        "d": 0,
        "d_window": [],
        "d_sum": 0
    },
    "right": {
        "distance": rightsensor.read_distance(),
        "last_distance": rightsensor.read_distance(),
        "d": 0,
        "d_window": [],
        "d_sum": 0
    }
    }
    front_timer = 0
    timer = 0
    wall_counter = 0
    scanning_done = False






def scanning_tick(state, sensor):
    global mode, phase, scanning_done
    if sensor == "left":
        new_distance = leftsensor.read_distance()
    elif sensor == "right":
        new_distance = rightsensor.read_distance()
    
    d_sum = update_distance(sensor, new_distance)
    mode, phase, scanning_done = scanning_mode(state, mode, phase, d_sum)
    print(f"distance: {sensor_states[sensor]['distance']}, d: {sensor_states[sensor]['distance']}, mode: {mode}, phase: {phase}")

    return scanning_done
    

def collection_tick(state):
    global mode, phase, collection_done
    sensor = "front" 
    new_distance = frontsensor.read_distance()


