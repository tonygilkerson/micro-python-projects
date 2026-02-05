import asyncio
from machine import Pin

# Global variable for blink period
led1_period_ms = 900

async def blink(led):
    """Blink LED using global period variable"""
    global led1_period_ms
    while True:
        led.on()
        await asyncio.sleep_ms(5)
        led.off()
        await asyncio.sleep_ms(led1_period_ms)

async def monitor_button(button, led):
    """Monitor button and toggle LED period between 1500 and 300"""
    global led1_period_ms
    while True:
        if button.value() == 0:  # Button pressed (assuming pull-up, pressed = LOW)
            # Toggle between 1500 and 300
            if led1_period_ms == 1500:
                led1_period_ms = 300
                print(f"Button pressed! Period changed to {led1_period_ms}ms")
            else:
                led1_period_ms = 1500
                print(f"Button pressed! Period changed to {led1_period_ms}ms")
            
            # Debounce - wait for button release
            while button.value() == 0:
                await asyncio.sleep_ms(10)
            # Wait a bit after release to debounce
            await asyncio.sleep_ms(50)
        await asyncio.sleep_ms(10)  # Check every 10ms

async def main():
    # Onboard LED
    led1 = Pin("LED", Pin.OUT)
    
    # External LED on GPIO 15 (connect LED + resistor to this pin)
    led2 = Pin(15, Pin.OUT)
    
    # Button on GPIO 16 with internal pull-up resistor
    # Press button connects pin to GND (LOW when pressed)
    button = Pin(16, Pin.IN, Pin.PULL_UP)
    
    # Start blinking tasks
    asyncio.create_task(blink(led1))  # Uses global led1_period_ms
    asyncio.create_task(blink(led2))  # Also uses global (shares same period)
    
    # Start button monitoring task
    asyncio.create_task(monitor_button(button, led2))
    
    # Run forever
    while True:
        await asyncio.sleep_ms(1000)

# Run it
asyncio.run(main())