from machine import Pin, I2C
from libs.VL53L0X.VL53L0X import VL53L0X


class DistanceSensor:
    def __init__(self, i2c_id=0, sda_pin=8, scl_pin=9, address=41):
        self.i2c_bus = I2C(i2c_id, sda=Pin(sda_pin), scl=Pin(scl_pin))
        self.sensor = VL53L0X(self.i2c_bus, address)
        self.sensor.set_Vcsel_pulse_period(self.sensor.vcsel_period_type[0], 18)
        self.sensor.set_Vcsel_pulse_period(self.sensor.vcsel_period_type[1], 14)
        self.sensor.start()

    def read_distance(self):
        return self.sensor.read()

    def stop(self):
        self.sensor.stop()