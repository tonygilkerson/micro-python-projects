import asyncio
from machine import Pin
from internal.bluetooth_scanner import BLEScanner

async def monitor_button(button: Pin, led: Pin, scanner: BLEScanner):
    """Monitor button and toggle LED """
    while True:
        if button.value() == 0:  # Button pressed (assuming pull-up, pressed = LOW)
            print("Button Press!")


            if led.value() == 1:
                led.value(0)
                print("Close cover (Turn off led)")
            
            elif led.value() == 0 and scanner.tracking:
                led.value(1)
                print("Open cover (Turn on LED)")

            elif led.value() == 0 and not scanner.tracking:
                print("Cant open when no device near!")
            
            else:
                print("no op")

            # Debounce - wait for button release
            while button.value() == 0:
                await asyncio.sleep_ms(10)
            # Wait a bit after release to debounce
            await asyncio.sleep_ms(50)

        await asyncio.sleep_ms(10)  # Check every 10ms

#
# main
#
async def main():
    
  door_led = Pin(15, Pin.OUT)
  door_led.off()
  door_btn = Pin(16, Pin.IN, Pin.PULL_UP)

  # Scanner task
  scanner = BLEScanner(mode="track", led_id="LED")
  asyncio.create_task(scanner.run())

  # Button task
  asyncio.create_task(monitor_button(door_btn,door_led,scanner))

  
  # Run forever
  while True:
      await asyncio.sleep_ms(1000)

# Run it
asyncio.run(main())
