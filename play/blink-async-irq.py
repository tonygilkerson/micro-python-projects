import asyncio
import micropython
import time
from machine import Pin

# Global variable for blink period
led1_period_ms = 100

async def blink(led):
    """Blink LED using global period variable"""
    global led1_period_ms
    while True:
        led.on()
        await asyncio.sleep_ms(5)
        led.off()
        await asyncio.sleep_ms(led1_period_ms)

# replaced monitor_button with IRQ + scheduled handler

# debounce timestamp
_last_press_ms = 0

def scheduled_button_handler(arg):
    """Runs in main context via micropython.schedule"""
    global led1_period_ms, _last_press_ms
    now = time.ticks_ms()
    # simple debounce: ignore presses within 200ms
    if time.ticks_diff(now, _last_press_ms) < 300:
        return
    _last_press_ms = now

    # toggle between 1500 and 300
    print(f"Before {led1_period_ms}")
    if led1_period_ms == 2000:
        led1_period_ms = 100
    else:
        led1_period_ms = 2000
    print(f"After {led1_period_ms}")
    print(f"Button pressed! Got message {arg}, Period changed to {led1_period_ms}")

def irq_minimal(pin):
    """IRQ-safe handler: schedule main-context work"""
    # pass small int (pin id) to scheduled handler
    micropython.schedule(scheduled_button_handler, "foo")

async def main():
    # Onboard LED
    led1 = Pin("LED", Pin.OUT)

    # External LED on GPIO 15 (connect LED + resistor to this pin)
    led2 = Pin(15, Pin.OUT)
    
    # Button on GPIO 16 with internal pull-up resistor
    # Press button connects pin to GND (LOW when pressed)
    button = Pin(16, Pin.IN, Pin.PULL_UP)
  
    
    # attach IRQ instead of polling task
    button.irq(handler=irq_minimal, trigger=Pin.IRQ_FALLING)
    
    # Start blinking tasks
    asyncio.create_task(blink(led1))  # Uses global led1_period_ms
    asyncio.create_task(blink(led2))  # Also uses global (shares same period)
    
    # Run forever
    while True:
        await asyncio.sleep_ms(1000)

# Run it
asyncio.run(main())