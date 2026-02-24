from machine import ADC, Pin
import time

adc = ADC(26)     # GP26
VREF = 3.3

while True:
    raw = adc.read_u16()
    voltage = raw * VREF / 65535

    distance_cm = (voltage / VREF) * 500

    print("Voltage:", round(voltage,3),
          " Distance:", int(distance_cm), "cm")

    time.sleep(0.1)