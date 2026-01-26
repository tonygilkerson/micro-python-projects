# Test if GPIO15 ever changes state
from machine import Pin
import time

rx_pin = Pin(15, Pin.IN)
led = Pin(25, Pin.OUT)

print("Monitoring GPIO15 for ANY changes...")
print("Press doorbell button repeatedly\n")

led.value(1)

last_value = rx_pin.value()
change_count = 0

try:
    while True:
        current_value = rx_pin.value()
        
        if current_value != last_value:
            change_count += 1
            print(f"GPIO15 changed to: {current_value} (change #{change_count})")
            last_value = current_value
        
        time.sleep_us(10)  # Very fast polling
        
except KeyboardInterrupt:
    print(f"\nTotal changes detected: {change_count}")
    led.value(0)