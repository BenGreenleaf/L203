from machine import Pin, ADC, PWM
from stdlib.asyncio import sleep_ms
from utime import sleep

left_dir = 4
left_pwm = 5

right_dir = 6
right_pwm = 7 

l_dir = Pin(left_dir, Pin.OUT)
l_pwm = PWM(Pin(left_pwm)); l_pwm.freq(1000)
r_dir = Pin(right_dir, Pin.OUT)
r_pwm = PWM(Pin(right_pwm)); r_pwm.freq(1000)

def _duty_from_pct(pct):
    if pct < 0: pct = 0
    if pct > 100: pct = 100
    return int(65535 * pct / 100)

# very basic speed setting functions to be reused

def set_left(speed):  # speed input needs to be from - 100 to 100
    if speed >= 0:
        l_dir.value(0)
        l_pwm.duty_u16(_duty_from_pct(speed))
    else:
        l_dir.value(1)
        l_pwm.duty_u16(_duty_from_pct(-speed))


def set_right(speed):
    if speed >= 0:
        r_dir.value(0)
        r_pwm.duty_u16(_duty_from_pct(speed))
    else:
        r_dir.value(1)
        r_pwm.duty_u16(_duty_from_pct(-speed))


# some other event based functions to be used/modified when we need them


def stop():
    set_left(0)
    set_right(0)

def ramp_to(left_target, right_target, step = 5, dt_ms =20): #to reduce dramatic increases in speed - may need to change these parameters after we test
    global current_left, current_right

    while current_left != left_target or current_right != right_target: #approaches the target speed gradually
        if current_left < left_target:
            current_left = min(current_left + step, left_target)
        elif current_left > left_target:
            current_left = max(current_left - step, left_target)

        if current_right < right_target:
            current_right = min(current_right + step, right_target)
        elif current_right > right_target:
            current_right = max(current_right - step, right_target)

        set_left(current_left)
        set_right(current_right)
        sleep(dt_ms / 1000.0)


# note to self kind of - these all need to be tested because a turn or speedin/slowing involving the ramp could result in overturning or going beyond the line so should determine the optimum duration once the line deterctor detects the line etc.

def forward(speed):
        ramp_to(speed, speed)

def backward(speed):
        ramp_to(-speed, -speed)

def decellerate():
    ramp_to(0, 0)

