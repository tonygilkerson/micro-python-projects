import asyncio
from machine import Pin
from internal.bluetooth_scanner import BLEScanner

cover_btn: Pin
cover_led: Pin
scanner: BLEScanner

class CoverCtl:
    """
    Used to control the opening and closing of a garage door

    Toto:
    - 'something': yack yack yack

    Attributes:
        foo (str): todo foo
        bar (str): todo bar
    """

    def __init__(self, 
                 scanner: BLEScanner,
                 cover_btn_id: str = "GP16",
                 cover_led_id: str = "GP15",
                 ) -> None:
        """
        Initializes the cover controller

        Args:
            cover_btn_id(int): The pin ID to use for the cover button. Is used to open/close the cover.
            cover_led_id(int): The pin ID to use for the cover LED. Is used to indicate if the cover is open or closed.
        """
        # 
        # Cover LED
        #
        self.cover_led = Pin(cover_led_id, Pin.OUT)
        self.cover_led.off()
        
        #
        # Cover Button
        #
        self.cover_btn = Pin(cover_btn_id, Pin.IN, Pin.PULL_UP)

        #
        # Bluetooth Scanner
        #
        self.scanner = scanner

    async def run(self) -> None:
        """Monitor button that controls the cover"""
        while True:
            if self.cover_btn.value() == 0:  # Button pressed (assuming pull-up, pressed = LOW)
                print("Button Press!")
                
                if self.cover_led.value() == 1:
                    self.cover_led.value(0)
                    print("Close cover (Turn off led)")
                
                elif self.cover_led.value() == 0 and self.scanner.tracking:
                    self.cover_led.value(1)
                    print("Open cover (Turn on LED)")

                elif self.cover_led.value() == 0 and not self.scanner.tracking:
                    print("Cant open when no device in range!")
                
                else:
                    print("no op")

                # Debounce - wait for button release
                while self.cover_btn.value() == 0:
                    await asyncio.sleep_ms(10)
                # Wait a bit after release to debounce
                await asyncio.sleep_ms(50)

            await asyncio.sleep_ms(10)  # Check every 10ms
