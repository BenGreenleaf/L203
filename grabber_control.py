from machine import Pin, PWM
from utime import sleep

# Safer range than full 0..180 to avoid hard end-stop current spikes
MIN_ANGLE = 10
MAX_ANGLE = 170
step = 2
move_delay = 0.08
lift_angle = 60
grab_angle = 28

lift = PWM(Pin(13))
lift.freq(50)

grab = PWM(Pin(15))
grab.freq(50)

def angle_to_u16(angle):
    # Typical servo pulse range: 500us..2500us at 50Hz
    min_us = 500
    max_us = 2500
    pulse_us = min_us + (max_us - min_us) * angle / 180
    period_us = 20000  # 20ms = 50Hz
    return int(pulse_us * 65535 / period_us)

def print_servo_angles():
    print("Lift angle:", lift_angle)
    print("Grab angle:", grab_angle)

def move_servo(servo, current_angle, target_angle):
    if target_angle < current_angle:
        direction = -1 * step
    else:
        direction = step

    for a in range(current_angle, target_angle, direction):
        servo.duty_u16(angle_to_u16(a))
        sleep(move_delay)
    servo.duty_u16(angle_to_u16(target_angle))
    return target_angle


def lift_up():
    global lift_angle
    lift_angle = move_servo(lift, lift_angle, 60) #140
    return True

def lift_down_bottom_rack():
    global lift_angle
    lift_angle = move_servo(lift, lift_angle, 72)
    return True

def lift_down_top_rack():
    global lift_angle
    lift_angle = move_servo(lift, lift_angle, 80)
    return True

def grab_close():
    global grab_angle
    grab_angle = move_servo(grab, grab_angle, 45)
    return True

def grab_open():
    global grab_angle
    grab_angle = move_servo(grab, grab_angle, 28)
    return True

if __name__ == "__main__":
    print("Testing grabber control...")
    print_servo_angles()
    sleep(1)

