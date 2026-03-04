from machine import I2C, Pin
import time

VL53_ADDR = 0x29

SYSRANGE_START = 0x00
SYSTEM_INTERRUPT_CLEAR = 0x0B
RESULT_INTERRUPT_STATUS = 0x13
RESULT_RANGE_STATUS = 0x14


class VL53L0X:

    def __init__(self, i2c, addr=VL53_ADDR):
        self.i2c = i2c
        self.addr = addr

        if self.addr not in self.i2c.scan():
            raise OSError("VL53L0X not found at address 0x29")

        self.stop_var = self._boot_sequence()

    def _write_u8(self, reg, val):
        self.i2c.writeto_mem(self.addr, reg, bytes([val & 0xFF]))

    def _read_u8(self, reg):
        return self.i2c.readfrom_mem(self.addr, reg, 1)[0]

    def _read_u16(self, reg):
        data = self.i2c.readfrom_mem(self.addr, reg, 2)
        return (data[0] << 8) | data[1]

    def _boot_sequence(self):
        self._write_u8(0x80, 0x01)
        self._write_u8(0xFF, 0x01)
        self._write_u8(0x00, 0x00)
        stop_var = self._read_u8(0x91)
        self._write_u8(0x00, 0x01)
        self._write_u8(0xFF, 0x00)
        self._write_u8(0x80, 0x00)
        return stop_var

    def read_mm(self, timeout_ms=200):
  
        self._write_u8(0x80, 0x01)
        self._write_u8(0xFF, 0x01)
        self._write_u8(0x00, 0x00)
        self._write_u8(0x91, self.stop_var)
        self._write_u8(0x00, 0x01)
        self._write_u8(0xFF, 0x00)
        self._write_u8(0x80, 0x00)

        self._write_u8(SYSRANGE_START, 0x01)

        start_time = time.ticks_ms()

        while (self._read_u8(SYSRANGE_START) & 0x01) != 0:
            if time.ticks_diff(time.ticks_ms(), start_time) > timeout_ms:
                raise OSError("VL53 start timeout")

        while (self._read_u8(RESULT_INTERRUPT_STATUS) & 0x07) == 0:
            if time.ticks_diff(time.ticks_ms(), start_time) > timeout_ms:
                raise OSError("VL53 range timeout")

        distance_mm = self._read_u16(RESULT_RANGE_STATUS + 10)

        self._write_u8(SYSTEM_INTERRUPT_CLEAR, 0x01)

        return distance_mm

