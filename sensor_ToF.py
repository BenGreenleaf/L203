from machine import Pin, I2C
from libs.VL53L0X.VL53L0X import VL53L0X
from libs.DFRobot_TMF8x01.DFRobot_TMF8x01 import DFRobot_TMF8x01


class DistanceSensor:
    def __init__(self, i2c_id=0, sda_pin=8, scl_pin=9, address=41):
        self.i2c_bus = I2C(i2c_id, sda=Pin(sda_pin), scl=Pin(scl_pin))
        if address == 41:
            self.vlx_sensor = VL53L0X(self.i2c_bus, address)
            self.vlx_sensor.set_Vcsel_pulse_period(self.vlx_sensor.vcsel_period_type[0], 18)
            self.vlx_sensor.set_Vcsel_pulse_period(self.vlx_sensor.vcsel_period_type[1], 14)
            self.vlx_sensor.start()
            self.sensor_type = "VL53L0X"
        else:
            self.tmf_sensor = DFRobot_TMF8x01(self.i2c_bus, address, fw_fname=None)
            self.tmf_sensor.begin()
            self.sensor_type = "TMF8x01"

    def read_distance(self):
        if self.sensor_type == "VL53L0X":
            return self.vlx_sensor.read()
        elif self.sensor_type == "TMF8x01":
            if self.tmf_sensor.is_data_ready():
                return self.tmf_sensor.get_distance_mm()

    def stop(self):
        if self.sensor_type == "VL53L0X":
            self.vlx_sensor.stop()
        elif self.sensor_type == "TMF8x01":
            self.tmf_sensor.stop_measurement()