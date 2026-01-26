from machine import Pin
import time

# Try with pull-up
rx_pin = Pin(15, Pin.IN, Pin.PULL_UP)
led = Pin(25, Pin.OUT)

print("Testing with PULL-UP resistor...")
led.value(1)

last_value = rx_pin.value()
print(f"Initial state: {last_value}")

try:
    while True:
        current_value = rx_pin.value()
        if current_value != last_value:
            print(f"Changed to: {current_value}")
            last_value = current_value
        time.sleep_us(10)
except KeyboardInterrupt:
    led.value(0)
    