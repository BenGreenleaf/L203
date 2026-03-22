import path_finding as path
from line_sensor_control import read_sensors
memory = 0  #stores the last node visited
stage = 0
action = "go_deposit_TEST"

sequence = [
    {"name": "go_collect_1", "type": "NAVIGATE", "goal": 8}, #potentially slightly excessive but i want the names of the states for debugging if necessary
    {"name": "scan_1",      "type": "SCAN", "scan_type": "lower"},
    {"name": "go_deposit_1","type": "NAVIGATE", "goal": None},
    {"name": "deposit_1",   "type": "DEPOSIT"},
    {"name": "go_collect_2","type": "NAVIGATE", "goal": 38},
    {"name": "scan_2",      "type": "SCAN", "scan_type": "lower"},
    {"name": "go_deposit_2","type": "NAVIGATE", "goal": None},
    {"name": "deposit_2",   "type": "DEPOSIT"},
    {"name": "go_collect_3","type": "NAVIGATE", "goal": 18},
    {"name": "scan_3",      "type": "SCAN", "scan_type": "upper"},
    {"name": "go_deposit_3","type": "NAVIGATE", "goal": None},
    {"name": "deposit_3",   "type": "DEPOSIT"},
    {"name": "go_collect_4","type": "NAVIGATE", "goal": 26},
    {"name": "scan_4",      "type": "SCAN", "scan_type": "upper"},
    {"name": "go_deposit_4","type": "NAVIGATE", "goal": None},
    {"name": "deposit_4",   "type": "DEPOSIT"},
    {"name": "go_collect_1", "type": "NAVIGATE", "goal": 8}, #potentially slightly excessive but i want the names of the states for debugging if necessary
    {"name": "scan_1",      "type": "SCAN", "scan_type": "lower"},
    {"name": "go_deposit_1","type": "NAVIGATE", "goal": None},
    {"name": "deposit_1",   "type": "DEPOSIT"},
    {"name": "go_collect_2","type": "NAVIGATE", "goal": 39},
    {"name": "scan_2",      "type": "SCAN", "scan_type": "lower"},
    {"name": "go_deposit_2","type": "NAVIGATE", "goal": None},
    {"name": "deposit_2",   "type": "DEPOSIT"},
    {"name": "go_collect_3","type": "NAVIGATE", "goal": 18},
    {"name": "scan_3",      "type": "SCAN", "scan_type": "upper"},
    {"name": "go_deposit_3","type": "NAVIGATE", "goal": None},
    {"name": "deposit_3",   "type": "DEPOSIT"},
    {"name": "go_collect_4","type": "NAVIGATE", "goal": 26},
    {"name": "scan_4",      "type": "SCAN", "scan_type": "upper"},
    {"name": "go_deposit_4","type": "NAVIGATE", "goal": None},
    {"name": "deposit_4",   "type": "DEPOSIT"},
    {"name": "return",      "type": "NAVIGATE", "goal": 1}
]

def get_current_step():
    return sequence[stage]

def get_previous_step():
    return sequence[stage-1]


def advance_stage():
    global stage
    if stage < len(sequence) - 1:
        stage += 1

def get_current_goal():
    current = sequence[stage]
    if current["type"] == "NAVIGATE":
        return current["goal"]
    return None 


def set_next_deposit_goal(goal):
    for i in range(stage + 1, len(sequence)):
        step = sequence[i]
        if step["type"] == "NAVIGATE" and step["name"].startswith("go_deposit"):
            step["goal"] = goal
            break






#need to create the hard coded sequence for the task

# sequence: go to first right bay (0), enter loading bay sequence (2). return to block deposit (3). go to left bay (4), return to block deposit (5), upstairs right (6), return (7), upstairs right (8), return (9), go back to start(10).

