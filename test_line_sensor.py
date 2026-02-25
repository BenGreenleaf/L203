from machine import Pin
from utime import sleep

# --- Line Sensor Test ---
def test_line_sensor():
    """
    Test three digital line sensors connected to GPIO pins GP26, GP27, and GP28.
    Output: LOW (0) for black, HIGH (1) for white.
    """
    sensor_pins = [26, 27, 28]  # GP26, GP27, GP28
    sensors = [Pin(pin, Pin.IN) for pin in sensor_pins]
    print("Line sensor test started. Place sensors above black/white surfaces.")
    print("Reading sensors on GP26, GP27, GP28...")
    while True:
        values = [sensor.value() for sensor in sensors]
        print(f"Sensor values: {values}")
        sleep(0.2)

if __name__ == "__main__":
    test_line_sensor()
