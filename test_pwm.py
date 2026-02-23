from machine import Pin, PWM
from utime import sleep

# Safer range than full 0..180 to avoid hard end-stop current spikes
MIN_ANGLE = 10
MAX_ANGLE = 170
STEP = 2
MOVE_DELAY = 0.12  # slower movement = less current spikes

def angle_to_u16(angle):
    # Typical servo pulse range: 500us..2500us at 50Hz
    min_us = 500
    max_us = 2500
    pulse_us = min_us + (max_us - min_us) * angle / 180
    period_us = 20000  # 20ms = 50Hz
    return int(pulse_us * 65535 / period_us)

def test_pwm():
    pwm = PWM(Pin(15))
    pwm.freq(50)

    angle = MIN_ANGLE
    direction = 1

    try:
        while True:
            u16 = angle_to_u16(angle)
            pwm.duty_u16(u16)
            print(f"angle={angle}, u16={u16}, dir={direction}")

            angle += direction * STEP
            if angle >= MAX_ANGLE:
                angle = MAX_ANGLE
                direction = -0.001
            elif angle <= MIN_ANGLE:
                angle = MIN_ANGLE
                direction = 0.001

            sleep(MOVE_DELAY)
    finally:
        # Leave servo in a neutral-safe state on stop
        pwm.duty_u16(angle_to_u16(90))
        sleep(0.2)
        pwm.deinit()

if __name__ == "__main__":
    test_pwm()
