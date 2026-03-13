from machine import I2C, Pin
from sensor_ToF import DistanceSensor
import line_sensor_control as sensors
from utime import sleep, ticks_ms, ticks_diff
import motor_control_functions as motor
import grabber_control as grabber
import task_control as task

frontsensor = DistanceSensor(0, 8, 9, 65)
leftsensor = DistanceSensor(1, 2, 3, 41)
rightsensor = DistanceSensor(0, 8, 9, 41) #need to find ids for each of these sensors
mode = "block_finding" #change back to block finding
phase = "initialise" #change back to initialise

speed = 40
timer = 0
wall_counter = 0
saved_timer = 0
window_size = 7
plus_threshold = 100
minus_threshold = -100 #need to tune these
scanning_done = False
collection_done = False
front_threshold = 130
front_timer = 0 
block_collected = False
block_lifted = False
error = 0
centre_streak = 0
last_dir = 0
align_ticks = 0
correction_speed = 8
last_error = 0
reverse_timer = 0
turn_start_ms = None
turn_duration = 3000

sensor_states = {
    "front": {
        "distance": frontsensor.read_distance(),
        "last_distance": frontsensor.read_distance(),
        "d": 0,
        "d_window": [],
        "d_sum": 0,
        "raw_data": []
    },
    "left": {
        "distance": leftsensor.read_distance(),
        "last_distance": leftsensor.read_distance(),
        "d": 0,
        "d_window": [],
        "d_sum": 0,
        "raw_data": []
    },
    "right": {
        "distance": rightsensor.read_distance(),
        "last_distance": rightsensor.read_distance(),
        "d": 0,
        "d_window": [],
        "d_sum": 0,
        "raw_data": []
    }
}

x = 150 #threshold? may be better to determine state based on jumps between a further and closer distance
xt = 20 #another threshold that needs tuning
side_threshold = 255

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

    distance_state["raw_data"].append(new_distance)

    return distance_state["d_sum"]
    

# def scanning_mode(state, mode, phase, sensor):
#     d_sum = sensor_states[sensor]["d_sum"]
#     global timer, saved_timer, wall_counter

#     if mode == "block_finding":
#         if phase == "initialise":
#             sleep(2)
#             return "block_finding", None, False
#         elif d_sum <= minus_threshold:
#             timer = 0
#             return "block_finding", "obstruction", False
#         elif d_sum >= plus_threshold:
#             return "block_finding", "obstruction_end", False
#         elif phase == "obstruction_end" and timer <= xt:
#             wall_counter += 1
#             print("wall")
#             return "block_finding", None, False
#         elif phase == "obstruction" and timer > xt:
#              print("block found")
#              return "block_finding", None, False #change later
#         elif phase == "obstruction" and timer <= xt:
#             timer += 1
#             return "block_finding", "obstruction", False
    
#     if mode == "block_found":
#         if state == (0,1,1,0) and phase == None:
#             return "block_found", "advance", False
#         if state == (1,1,1,0) and phase == "advance":
#             return "block_found", "turning", False
#         if state == (1,1,1,1) and phase == "turning":
#             return "block_found", "approach", True
        
#     return mode, phase, False

def block_found(data):
    gap_threshold = 5
    valids_threshold = 3
    gap = 0
    valids = 0
    recent_data = data[-15:] if len(data) >= 15 else data
    for d in recent_data:
        if d <= side_threshold and gap <= gap_threshold:
            valids += 1
            gap = 0
        elif d <= side_threshold and gap > gap_threshold:
            valids = 1
            gap = 0
        else:
            gap += 1

    if valids >= valids_threshold:
        return True
    else:
        return False



def scanning_mode(state, mode, phase, sensor):
    if mode == "block_finding":
        if phase == "initialise":
            sleep(2)
            return "block_finding", None, False
        elif block_found(sensor_states[sensor]["raw_data"]):
            return "block_found", None, False #change later
    if mode == "block_found" and sensor == "left": #bays where scanning is on the left
        if state == (0,1,1,0) and phase == None:
            return "block_found", "advance", False
        if state == (1,1,1,0) and phase == "advance":
            return "block_found", "turning", False
        if state == (1,1,1,1) and phase == "turning":
            return "block_found", "approach", True
    elif mode == "block_found" and sensor == "right": #bays where scanning is on the right
        if state == (0,1,1,0) and phase == None:
            return "block_found", "advance", False
        if state == (0,1,1,1) and phase == "advance":
            return "block_found", "turning", False
        if state == (1,1,1,1) and phase == "turning":
            return "block_found", "approach", True
        
    return mode, phase, False


def scanning_actions(mode, phase, state, type): #type can be passed as sensor as they are both l/r
    if mode == "block_finding":
        if phase == "initialise":
            motor.set_left(-speed)
            motor.set_right(-speed)
        else:
            follow_line(state)
    elif mode == "block_found" and phase == "advance":
        follow_line(state)
    elif mode == "block_found" and phase == "turning":
        if type == "left":
            motor.set_left(-speed)
            motor.set_right(speed)
        elif type == "right":
            motor.set_left(speed)
            motor.set_right(-speed)
    elif mode == "block_found" and phase == "approach":
        motor.set_left(speed)
        motor.set_right(speed)
    
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
        new_error = alpha*new_error + (1-alpha)*new_error #needs changing

        update_error(new_error)
        base = speed #adjust
        

        if error != 0:
           
            last_dir = error
            # align_ticks = 0 
            centre_streak = 0

            kp = 15
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
    global error, last_error, last_dir, align_ticks, centre_streak, block_collected, block_lifted
    if (mode == "block_found" or mode == "collecting") and phase == "approach": #literally copied line following code because it is much easier than trying to navigate through to line following from this function
        follow_line(state)
    elif mode == "collecting" and phase == "lowering":
        motor.set_right(0)
        motor.set_left(0)
        if task.get_current_step()['scan_type'] == "lower":
            lowered = grabber.lift_down_bottom_rack()
        else:
            lowered = grabber.lift_down_top_rack()
        closed = grabber.grab_close()
        block_collected = closed and lowered
    elif mode == "collecting" and phase == "lifting":
        lifted = grabber.lift_up()
        block_lifted = lifted
    elif mode == "collecting" and phase == "reversing":
        motor.set_left(-speed)
        motor.set_right(-speed)
    elif mode == "turning" and phase == "turn_start":
        motor.set_left(-(speed+20))
        motor.set_right((speed+20))
    elif mode == "turning" and phase == "turning_end":
        print("we reset the motors")
        motor.set_left(0)
        motor.set_right(0)


def collection_mode(state, mode, phase, distance):
    global front_timer, reverse_timer, block_collected, block_lifted, turn_start_ms
    if mode == "block_found" and phase == "approach":
        front_timer = 0
        block_collected = False
        block_lifted = False
        return "collecting", "approach", False
    
    if mode == "collecting":
        if phase == "approach":
            if distance > front_threshold:
                return "collecting", "approach", False
            elif distance <= front_threshold:
                if front_timer < 4:
                    front_timer += 1
                    return "collecting", "approach", False
                elif front_timer >= 4:
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
                reverse_timer = 0 
                return "collecting", "reversing", False
            
        elif phase == "reversing":
            if reverse_timer <130:
                reverse_timer += 1 
                return "collecting", "reversing", False
            else:
                turn_start_ms = ticks_ms()
                return "turning", "turn_start", False
            
    elif mode == "turning" and phase == "turn_start":
        if turn_start_ms is not None:
            print(ticks_diff(ticks_ms(), turn_start_ms))
        if turn_start_ms is None:
            return "turning", "turn_start", False
        elif ticks_diff(ticks_ms(), turn_start_ms) >= turn_duration: #do we need two turning phases for this - maybe yes to rest motors 
            return "turning", "turn_end", False
        else:
            return "turning", "turn_start", False
    elif mode == "turning" and phase == "turn_end":
        print("we went back to line following")
        turn_start_ms = None
        return "LINE_FOLLOWING", None, True

    return mode, phase, False
        



def reset_scan_state():
    global sensor_states, scanning_done, front_timer, timer, wall_counter
    sensor_states = {
    "front": {
        "distance": frontsensor.read_distance(),
        "last_distance": frontsensor.read_distance(),
        "d": 0,
        "d_window": [],
        "d_sum": 0,
        "raw_data": []
    },
    "left": {
        "distance": leftsensor.read_distance(),
        "last_distance": leftsensor.read_distance(),
        "d": 0,
        "d_window": [],
        "d_sum": 0,
        "raw_data": []
    },
    "right": {
        "distance": rightsensor.read_distance(),
        "last_distance": rightsensor.read_distance(),
        "d": 0,
        "d_window": [],
        "d_sum": 0,
        "raw_data": []
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
    mode, phase, scanning_done = scanning_mode(state, mode, phase, sensor)
    scanning_actions(mode, phase, state, sensor)
    #print(f"distance: {sensor_states[sensor]['distance']}, d: {sensor_states[sensor]['d']}, mode: {mode}, phase: {phase}")

    return scanning_done
    

def collection_tick(state):
    global mode, phase, collection_done
    sensor = "front" 
    new_distance = frontsensor.read_distance()
    print(f"Front distance sensor: {new_distance}")
    mode, phase, collection_done = collection_mode(state, mode, phase, new_distance)
    print(mode, phase)
    collection_actions(mode, phase, state)

    return collection_done



