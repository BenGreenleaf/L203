from machine import Pin, I2C

i2c = I2C(0, sda=Pin(8), scl=Pin(9))

print(i2c.scan())