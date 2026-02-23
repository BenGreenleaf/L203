from machine import I2C, Pin
import time

# pin20=SCL(GP15), pin19=SDA(GP14), pin18=GND, pin36=3V3
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)

VL53_ADDR = 0x29
SYSRANGE_START = 0x00
SYSTEM_INTERRUPT_CLEAR = 0x0B
RESULT_INTERRUPT_STATUS = 0x13
RESULT_RANGE_STATUS = 0x14


def write_u8(reg, val):
    i2c.writeto_mem(VL53_ADDR, reg, bytes([val & 0xFF]))


def read_u8(reg):
    return i2c.readfrom_mem(VL53_ADDR, reg, 1)[0]


def read_u16(reg):
    data = i2c.readfrom_mem(VL53_ADDR, reg, 2)
    return (data[0] << 8) | data[1]


def boot_sequence():
    write_u8(0x80, 0x01)
    write_u8(0xFF, 0x01)
    write_u8(0x00, 0x00)
    stop_var = read_u8(0x91)
    write_u8(0x00, 0x01)
    write_u8(0xFF, 0x00)
    write_u8(0x80, 0x00)
    return stop_var


def single_read_mm(stop_var, timeout_ms=200):
    write_u8(0x80, 0x01)
    write_u8(0xFF, 0x01)
    write_u8(0x00, 0x00)
    write_u8(0x91, stop_var)
    write_u8(0x00, 0x01)
    write_u8(0xFF, 0x00)
    write_u8(0x80, 0x00)
    write_u8(SYSRANGE_START, 0x01)

    t0 = time.ticks_ms()
    while (read_u8(SYSRANGE_START) & 0x01) != 0:
        if time.ticks_diff(time.ticks_ms(), t0) > timeout_ms:
            raise OSError("start timeout")
        time.sleep_ms(1)

    t0 = time.ticks_ms()
    while (read_u8(RESULT_INTERRUPT_STATUS) & 0x07) == 0:
        if time.ticks_diff(time.ticks_ms(), t0) > timeout_ms:
            raise OSError("range timeout")
        time.sleep_ms(1)

    distance_mm = read_u16(RESULT_RANGE_STATUS + 10)
    write_u8(SYSTEM_INTERRUPT_CLEAR, 0x01)
    return distance_mm


print("I2C scan:", [hex(x) for x in i2c.scan()])
if VL53_ADDR not in i2c.scan():
    raise OSError("VL53L0X not found at 0x29")

print("VL53 model id:", hex(read_u8(0xC0)))
stop_var = boot_sequence()

while True:
    distance_mm = single_read_mm(stop_var)
    distance_cm = distance_mm / 10.0
    print("Distance:", distance_mm, "mm", " Distance:", round(distance_cm, 1), "cm")
    time.sleep(0.1)
