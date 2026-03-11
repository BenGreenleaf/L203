from machine import Pin, I2C

i2c1 = I2C(0, sda=Pin(8), scl=Pin(9))
i2c2 = I2C(1, sda=Pin(2), scl=Pin(3))

print(i2c1.scan())
print(i2c2.scan())