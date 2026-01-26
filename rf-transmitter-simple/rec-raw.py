# Simple RF receiver that prints raw pulse timings
from machine import Pin
import time

rx_pin = Pin(15, Pin.IN)
led = Pin(25, Pin.OUT)

def measure_pulse(level, timeout_us=100000):
    """Measure pulse duration"""
    start = time.ticks_us()
    while rx_pin.value() == level:
        if time.ticks_diff(time.ticks_us(), start) > timeout_us:
            return 0
    return time.ticks_diff(time.ticks_us(), start)

print("Listening for RF signals on GPIO15...")
print("Raw pulse timings will be displayed")
print("Press Ctrl+C to stop\n")

led.value(1)  # LED on to show we're running

try:
    pulse_buffer = []
    
    while True:
        # Wait for signal
        while rx_pin.value() == 0:
            time.sleep_us(100)
        
        # Capture a sequence of pulses
        for i in range(100):  # Capture up to 100 pulses
            high = measure_pulse(1, 10000)
            if high == 0:
                break
            low = measure_pulse(0, 10000)
            if low == 0:
                break
            
            pulse_buffer.append((high, low))
        
        # Print if we captured something
        if len(pulse_buffer) > 5:
            print("=" * 50)
            print(f"Captured {len(pulse_buffer)} pulse pairs:")
            for i, (h, l) in enumerate(pulse_buffer):
                print(f"  {i}: HIGH={h}us, LOW={l}us")
            print("=" * 50)
            print()
        
        pulse_buffer.clear()
        time.sleep_ms(100)
        
except KeyboardInterrupt:
    print("\nStopped")
    led.value(0)