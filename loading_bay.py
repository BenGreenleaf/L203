from machine import I2C, Pin
from sensor_ToF import VL53L0X
import line_sensor_control as sensors

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)

tof = VL53L0X(i2c)

x = 0 #threshold? may be better to determine state based on jumps between a further and closer distance

def update_mode(state, mode, phase):
    if state == (1,1,1,0) and distance < x:
        return "BLOCK_FOUND", "turning"
    else



while True:
    state = sensors.read_sensors()
    distance = tof.read_mm()





print(distance)