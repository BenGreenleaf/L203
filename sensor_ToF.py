from machine import Pin, I2C
from libs.VL53L0X.VL53L0X import VL53L0X
from libs.DFRobot_TMF8x01.DFRobot_TMF8x01 import DFRobot_TMF8701
from utime import sleep


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
            self.tmf_sensor = DFRobot_TMF8701(self.i2c_bus, address)
            self.tmf_sensor.begin()
            self.sensor_type = "TMF8x01"
            while(self.tmf_sensor.begin() != 0):
                print("   Initialisation failed")
                sleep(0.5)
            
            self.tmf_sensor.start_measurement(calib_m = self.tmf_sensor.eMODE_NO_CALIB, mode = self.tmf_sensor.eDISTANCE)

    # def __init__(self, i2c_id=0, sda_pin=8, scl_pin=9, address=0x29, sensor_type="auto"):
    #     self.i2c_bus = I2C(i2c_id, sda=Pin(sda_pin), scl=Pin(scl_pin))
    #     self.last_distance = None

    #     if sensor_type == "auto":
    #         if address == 0x29:
    #             sensor_type = "VL53L0X"
    #         elif address == 0x41:
    #             sensor_type = "TMF8x01"
    #         else:
    #             raise ValueError("Unknown sensor type for this address")

    #     self.sensor_type = sensor_type

    #     if self.sensor_type == "VL53L0X":
    #         self.vlx_sensor = VL53L0X(self.i2c_bus, address)
    #         self.vlx_sensor.set_Vcsel_pulse_period(self.vlx_sensor.vcsel_period_type[0], 18)
    #         self.vlx_sensor.set_Vcsel_pulse_period(self.vlx_sensor.vcsel_period_type[1], 14)
    #         self.vlx_sensor.start()

    #     elif self.sensor_type == "TMF8x01":
    #         self.tmf_sensor = DFRobot_TMF8701(self.i2c_bus, address)
    #         self.tmf_sensor.begin()

    def read_distance(self):
        if self.sensor_type == "VL53L0X":
            return self.vlx_sensor.read()
        elif self.sensor_type == "TMF8x01":
            if self.tmf_sensor.is_data_ready() == True:
                distance = self.tmf_sensor.get_distance_mm()
                self.last_distance = distance
                return distance
            else:
                self.last_distance = None
                print("no distance")
            return self.last_distance

    def stop(self):
        if self.sensor_type == "VL53L0X":
            self.vlx_sensor.stop()
        elif self.sensor_type == "TMF8x01":
            self.tmf_sensor.stop_measurement()