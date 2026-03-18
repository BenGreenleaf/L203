from machine import I2C, Pin
from sensor_ToF import DistanceSensor
import line_sensor_control as sensors
from utime import sleep, ticks_ms, ticks_diff
import motor_control_functions as motor
import grabber_control as grabber
import task_control as task
import resistance_identifier as res

frontsensor = DistanceSensor(0, 8, 9, 65)
leftsensor = DistanceSensor(1, 2, 3, 41)
rightsensor = DistanceSensor(0, 8, 9, 41) #need to find ids for each of these sensors
mode = "block_finding" #change back to block finding
phase = "initialise" #change back to initialise
grabber.grab_open()
grabber.lift_up()


speed = 60
timer = 0
wall_counter = 0
saved_timer = 0
window_size = 7
plus_threshold = 100
minus_threshold = -100 #need to tune these
scanning_done = False
collection_done = False
front_threshold = 150
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
spin_duration = 1600
turn_duration = 1100
turn_delay = 0
delay_start_ms = None
kp = 15
kd = 5
last_outer = 0
node_addition = 0
initialise_start_ms = None
initial_spin_duration = 2590 #  needs tuning
colour = None

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

green_led = Pin(10, Pin.OUT)


x = 150 #threshold? may be better to determine state based on jumps between a further and closer distance
xt = 20 #another threshold that needs tuning
side_threshold = 258

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
    valids_threshold = 4
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
        #green_led.value(1)
        return True
    else:
        #green_led.value(0)
        return False



def scanning_mode(state, mode, phase, sensor):
    global turn_start_ms, delay_start_ms, correction_speed, kp, kd, wall_counter, last_outer, node_addition, initialise_start_ms
    inner = (state[1], state[2])
    outerleft = state[0]
    outerright = state[3]
    if mode == "block_finding":
        if phase == "initialise":
            if initialise_start_ms is None:
                initialise_start_ms = ticks_ms()
                turn_start_ms = None
                correction_speed = 8
                kd = 5
                wall_counter = 0
                return "block_finding", "initialise", False
            elif ticks_diff(ticks_ms(), initialise_start_ms) < 700:
                return "block_finding", "initialise", False
            elif state in [(1,1,1,1), (1,1,0,1), (1,0,1,1)]:
                turn_start_ms = ticks_ms()
                return "block_finding", "initial_turn", False
        elif phase == "initial_turn":
            if turn_start_ms is not None:
                if ticks_diff(ticks_ms(), turn_start_ms) >= initial_spin_duration: 
                    turn_start_ms = None
                    wall_counter = 0
                    last_outer = 0
                    sensor_states[sensor]["raw_data"] = []
                    sensor_states[sensor]["d_window"] = []
                    sensor_states[sensor]["d_sum"] = 0
                    return "block_finding", None, False
                else:
                    return "block_finding", "initial_turn", False
            
        elif phase == None and not block_found(sensor_states[sensor]["raw_data"]):
            if sensor == "right":
                if last_outer == 0 and outerright == 1:
                    wall_counter += 1
                    print("wall, right")
                last_outer = outerright
            elif sensor == "left":
                if last_outer == 0 and outerleft == 1:
                    wall_counter += 1
                    print("wall, left")
                last_outer = outerleft
            return "block_finding", None, False
        elif block_found(sensor_states[sensor]["raw_data"]):
            wall_counter += 1
            print("wall, block")
            return "block_found", "advance", False #change later
    if mode == "block_found" and sensor == "left": #bays where scanning is on the left
        if phase == "advance":
            if state in [(1,1,1,0), (1,0,1,0), (1,1,0,0)]:
                delay_start_ms = None
                return "block_found", "reverse", False
            else:
                return "block_found", "advance", False
        elif mode == "block_found" and phase == "reverse":
            if delay_start_ms is None:
                delay_start_ms = ticks_ms()
            elif ticks_diff(ticks_ms(), delay_start_ms) >= turn_delay:
                return "block_found", "turning", False
            else: 
                return "block_found", "reverse", False
        elif mode == "block_found" and phase == "turning": #had state = 1110
                if turn_start_ms is not None:
                    print(ticks_diff(ticks_ms(), turn_start_ms))
                if turn_start_ms is None:
                    correction_speed = 30
                    kd = 15
                    turn_start_ms = ticks_ms()
                    return "block_found", "turning", False
                elif ticks_diff(ticks_ms(), turn_start_ms) >= turn_duration: 
                    turn_start_ms = None
                    return "block_found", "seek_line", False
        elif mode == "block_found" and phase == "seek_line":
                turn_start_ms = None
                if inner == (1,1):
                    node_addition = wall_counter - 1
                    return "block_found", "approach", True
                elif inner == (1,0):
                    return "block_found", "correct_left", False
                elif inner == (0,1):
                    return "block_found", "correct_right", False
                else:
                    return "block_found", "seek_line", False
        elif mode == "block_found" and phase == "correct_left":
            if inner == (1,1):
                node_addition = wall_counter - 1
                return "block_found", "approach", True
            elif inner == (1,0):
                return "block_found", "correct_left", False
            elif inner == (0,1):
                return "block_found", "correct_right", False
            else:
                return "block_found", "seek_line", False
        elif mode == "block_found" and phase == "correct_right":
            if inner == (1,1):
                node_addition = wall_counter -1
                return "block_found", "approach", True
            elif inner == (0,1):
                return "block_found", "correct_right", False
            elif inner == (1,0):
                return "block_found", "correct_left", False
            else:
                return "block_found", "seek_line", False
            

  
    elif mode == "block_found" and sensor == "right": #bays where scanning is on the right
        if phase == "advance":
            if state in [(0,1,1,1), (0,1,0,1), (0,0,1,1)]:
                delay_start_ms = None
                return "block_found", "reverse", False
            else:
                return "block_found", "advance", False
        elif mode == "block_found" and phase == "reverse":
            if delay_start_ms is None:
                delay_start_ms = ticks_ms()
            elif ticks_diff(ticks_ms(), delay_start_ms) >= turn_delay:
                return "block_found", "turning", False
            else: 
                return "block_found", "reverse", False
        elif mode == "block_found" and phase == "turning": #had state = 1110
                if turn_start_ms is not None:
                    print(ticks_diff(ticks_ms(), turn_start_ms))
                if turn_start_ms is None:
                    correction_speed = 30
                    kd = 15
                    turn_start_ms = ticks_ms()
                    return "block_found", "turning", False
                elif ticks_diff(ticks_ms(), turn_start_ms) >= turn_duration: 
                    turn_start_ms = None
                    return "block_found", "seek_line", False
        elif mode == "block_found" and phase == "seek_line":
                turn_start_ms = None
                if inner == (1,1):
                    node_addition = wall_counter -1
                    return "block_found", "approach", True
                elif inner == (1,0):
                    return "block_found", "correct_left", False
                elif inner == (0,1):
                    return "block_found", "correct_right", False
                else:
                    return "block_found", "seek_line", False  
        elif mode == "block_found" and phase == "correct_left":
            if inner == (1,1):
                node_addition = wall_counter -1
                return "block_found", "approach", True
            elif inner == (1,0):
                return "block_found", "correct_left", False
            elif inner == (0,1):
                return "block_found", "correct_right", False
            else:
                return "block_found", "seek_line", False

        elif mode == "block_found" and phase == "correct_right":
            if inner == (1,1):
                node_addition = wall_counter- 1
                return "block_found", "approach", True
            elif inner == (0,1):
                return "block_found", "correct_right", False
            elif inner == (1,0):
                return "block_found", "correct_left", False
            else:
                return "block_found", "seek_line", False
    return mode, phase, False


def scanning_actions(mode, phase, state, type): #type can be passed as sensor as they are both l/r
    global kp
    if mode == "block_finding":
        if phase == "initialise":
            follow_line(state)
        elif phase == "initial_turn":
            motor.set_left(-speed)
            motor.set_right(speed)
        else:
            follow_line(state)
    elif mode == "block_found" and phase == "advance":
        follow_line(state)
    elif mode == 'block_found' and phase == "reverse":
        motor.set_left(-speed)
        motor.set_right(-speed)
    elif mode == "block_found" and (phase == "turning" or phase == "seek_line"):
            if type == "left":
                motor.set_left(-speed)
                motor.set_right(speed)
            elif type == "right":
                motor.set_left(speed)
                motor.set_right(-speed)
    elif mode == "block_found" and phase == "correct_right":
        motor.set_left(speed)
        motor.set_right(-speed)
    elif mode == "block_found" and phase == "correct_left":
        motor.set_left(-speed)
        motor.set_right(speed)
    elif mode == "block_found" and phase == "approach":
        motor.set_left(speed)
        motor.set_right(speed)
        follow_line(state)
    
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
        

        if error != 0 and align_ticks == 0:
           
            last_dir = error
            # align_ticks = 0 
            centre_streak = 0

            print("normal line following")
            correction = kp * error + kd * (error - last_error)
            motor.set_left(int(base - correction))
            motor.set_right(int(base + correction))


        else:
            centre_streak += 1
            if centre_streak == 1 and last_dir != 0:
                print("centre streak mode")
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
    




def collection_actions(mode, phase, state, sensor):
    global error, last_error, last_dir, align_ticks, centre_streak, block_collected, block_lifted
    if (mode == "block_found" or mode == "collecting") and phase == "approach": #literally copied line following code because it is much easier than trying to navigate through to line following from this function
        follow_line(state)
    elif mode == "collecting" and phase == "lowering":
        motor.set_right(0)
        motor.set_left(0)
        print("motors 0")
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
    elif mode == "turning" and phase == "turn_end":
        print("we reset the motors")
        motor.set_left(0)
        motor.set_right(0)
    elif mode == "finishing" and phase == "approaching":
        follow_line(state)


    elif mode == "finishing_turn":
        if sensor == "right":
            turn_speed = 53
            if phase == "reverse":
                motor.set_left(int(-0.7*speed))
                motor.set_right(int(-0.7*speed))
            elif phase == "turning_start":
                motor.set_left(turn_speed)
                motor.set_right(-1.2*turn_speed)
            elif phase == "turning_end":
                motor.set_left(turn_speed)
                motor.set_right(-turn_speed) #could even adjust the speed of these values if the curve is too large or too small
            elif phase == "exiting":
                motor.set_left(speed)
                motor.set_right(speed)
        elif sensor == "left":
            turn_speed = 53
            if phase == "reverse":
                motor.set_left(int(-0.7*speed))
                motor.set_right(int(-0.7*speed))
            elif phase == "turning_start":
                motor.set_left(-1.2*turn_speed)
                motor.set_right(turn_speed)
            elif phase == "turning_end": #phases look identical but need to separate them as states are contained within each that need to be interpreted differenty
                motor.set_left(-1.05*turn_speed)
                motor.set_right(turn_speed)
            elif phase == "sensing":
                motor.set_left(0)
                motor.set_right(0)
            elif phase == "exiting":
                motor.set_left(speed)
                motor.set_right(speed)

def collection_mode(state, mode, phase, distance, sensor):
    global front_timer, reverse_timer, block_collected, block_lifted, turn_start_ms, colour
    
    if mode == "block_found" and phase == "approach":
        front_timer = 0
        turn_start_ms = None
        block_collected = False
        block_lifted = False
        return "collecting", "approach", False
    
    if mode == "collecting":
        if phase == "approach":
            if distance > front_threshold:
                return "collecting", "approach", False
            elif distance <= front_threshold:
                print("threshold reached")
                # if front_timer < 2:
                #     print("front timer adding")
                #     front_timer += 1
                #     return "collecting", "approach", False
                # elif front_timer >= 2:
                #     print("stopping now")
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
            if reverse_timer <70:
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
        elif ticks_diff(ticks_ms(), turn_start_ms) >= spin_duration: #do we need two turning phases for this - maybe yes to rest motors 
            return "turning", "turn_end", False
        else:
            return "turning", "turn_start", False
        
    elif mode == "turning" and phase == "turn_end":
        turn_start_ms = None
        return "finishing", "approaching", False
    
    elif mode == "finishing" and phase == "approaching": #need to add left version
        if state == (1,0,0,1):
            return "finishing_turn", "reverse", False
        else:
            return "finishing", "approaching", False
        
    elif mode == "finishing_turn":
        if sensor == "right":
            if phase == "reverse": 
                if state in [(1,1,1,1), (0,1,1,1), (0,0,1,1)]:
                    return "finishing_turn", "turning_start", False
                else: 
                    return "finishing_turn", "reverse", False
            elif phase == "turning_start":
                if state in [(0,1,1,0), (0,0,1,0)]:
                    return "finishing_turn", "turning_end", False
                else:
                    return "finishing_turn", "turning_start", False
            elif phase == "turning_end":
                if state in [(0,1,1,1),(0,1,0,1)]:
                    sleep(0.35)
                    return "finishing_turn", "sensing", False
                else:
                    return "finishing_turn", "turning_end", False
            elif phase == "exiting":
                if state in [(0,1,1,0), (0,0,1,0), (0,1,0,0)]:
                    return "LINE_FOLLOWING", None, True #does it need to be none
                else:
                    return "finishing_turn", "exiting", False
            elif phase == "sensing":
                colour = res.identify()
                if colour == "RED":
                    print("red identified")
                    task.set_next_deposit_goal(6)
                elif colour == "BLUE": #set node and positioning as east if in lower right, west if in lower left (loading bay will leave the robot facing outward)
                    print("blue identified")
                    task.set_next_deposit_goal(44)
                elif colour == "GREEN":
                    print("green identified")
                    task.set_next_deposit_goal(43)
                elif colour == "YELLOW":
                    print("yellow identified")
                    task.set_next_deposit_goal(4)
                elif colour == None:
                    print("none")
                else:
                    print("error")
                return "finishing_turn", "exiting", False
        elif sensor == "left":
            if phase == "reverse": 
                if state in  [(1,1,1,0), (1,1,0,0), (1,1,1,1)]:
                    return "finishing_turn", "turning_start", False
                else: 
                    return "finishing_turn", "reverse", False
            elif phase == "turning_start":
                if state in [(0,1,1,0), (0,1,0,0)]:
                    return "finishing_turn", "turning_end", False
                else:
                    return "finishing_turn", "turning_start", False
            elif phase == "turning_end":
                if state == (1,1,1,0):
                    sleep(0.65)
                    colour = None
                    return "finishing_turn", "sensing", False
                else:
                    return "finishing_turn", "turning_end", False

            elif phase == "sensing":
                colour = res.identify()
                if colour == "RED":
                    print("red identified")
                    task.set_next_deposit_goal(6)
                elif colour == "BLUE": #set node and positioning as east if in lower right, west if in lower left (loading bay will leave the robot facing outward)
                    print("blue identified")
                    task.set_next_deposit_goal(44)
                elif colour == "GREEN":
                    print("green identified")
                    task.set_next_deposit_goal(43)
                elif colour == "YELLOW":
                    print("yellow identified")
                    task.set_next_deposit_goal(4)
                elif colour == None:
                    print("none")
                else:
                    print("error")
                return "finishing_turn", "exiting", False
            elif phase == "exiting":
                if state in [(0,1,1,0), (0,0,1,0)]:
                    return "LINE_FOLLOWING", None, True
                else:
                    return "finishing_turn", "exiting", False
                



    return mode, phase, False
        



def reset_scan_state():
    global sensor_states, scanning_done, front_timer, timer, wall_counter, mode, phase, collection_done, block_collected, block_lifted, front_timer, correction_speed, kp, node_addition, wall_counter, delay_start_ms, initialise_start_ms, turn_start_ms, last_outer, kd, error, last_error, centre_streak, align_ticks, last_dir, reverse_timer, colour
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
    mode = "block_finding"
    phase = "initialise"
    collection_done = False
    block_collected = False
    block_lifted = False
    correction_speed = 8
    kp = 15
    node_addition = 0
    wall_counter = 0
    delay_start_ms = None
    initialise_start_ms = None
    turn_start_ms = None
    last_outer = 0
    kd = 5
    error = 0
    last_error = 0
    centre_streak = 0
    align_ticks = 0
    last_dir = 0
    reverse_timer = 0
    colour = None







def scanning_tick(state, sensor):
    global mode, phase, scanning_done
    if sensor == "left":
        new_distance = leftsensor.read_distance()
    elif sensor == "right":
        new_distance = rightsensor.read_distance()
    print(sensor)
    d_sum = update_distance(sensor, new_distance)
    mode, phase, scanning_done = scanning_mode(state, mode, phase, sensor)
    scanning_actions(mode, phase, state, sensor)
    print(f"distance: {sensor_states[sensor]['distance']}, new_distance: {new_distance} d: {sensor_states[sensor]['d']}, mode: {mode}, phase: {phase}")

    return scanning_done
    

def collection_tick(state, sensor):
    global mode, phase, collection_done
    new_distance = frontsensor.read_distance()
    #print(f"Front distance sensor: {new_distance}")
    mode, phase, collection_done = collection_mode(state, mode, phase, new_distance, sensor)
    #print(mode, phase)
    print(new_distance)
    collection_actions(mode, phase, state, sensor)

    return collection_done



