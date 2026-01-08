import asyncio
from machine import Pin
from internal.bluetooth_scanner import BLEScanner
from internal.logging import Logger
import micropython
import time

class CoverCtl:
    """
    Used to control the opening and closing of a garage door

    Toto:
    - 'something': yack yack yack

    Attributes:
        foo (str): todo foo
        bar (str): todo bar
    """
    logger: Logger
    cover_btn: Pin
    cover_led: Pin
    scanner: BLEScanner
    _cover_btn_last_press_ms: int


    def __init__(self,
                 logger: Logger,
                 scanner: BLEScanner,
                 cover_btn_id: str,
                 cover_led_id: str,
                 ) -> None:
        """
        Initializes the cover controller

        Args:
            cover_btn_id(int): The pin ID to use for the cover button. Is used to open/close the cover.
            cover_led_id(int): The pin ID to use for the cover LED. Is used to indicate if the cover is open or closed.
        """
        # Logger
        self.logger = logger

        # Scanner
        self.scanner = scanner

        # Cover LED
        self.cover_led = Pin(cover_led_id, Pin.OUT)
        self.cover_led.off()

        # Cover Button
        self.cover_btn = Pin(cover_btn_id, Pin.IN, Pin.PULL_UP)
        self._cover_btn_last_press_ms = 0
        self.cover_btn.irq(handler=self.cover_irq, trigger=Pin.IRQ_FALLING)

    def cover_irq(self, pin):
        """IRQ-safe handler: schedule main-context work"""
        # pass small int (pin id) to scheduled handler
        micropython.schedule(self.cover_btn_handler, "msg-not-used")

    def cover_btn_handler(self, arg):
        """Cover Button Handler. Runs when the cover button is pressed
        Runs in main context via micropython.schedule"""
        now = time.ticks_ms()
        # simple debounce: ignore presses within 300ms
        if time.ticks_diff(now, self._cover_btn_last_press_ms) < 300:
            return
        self._cover_btn_last_press_ms = now

        self.logger.info("CoverCtl.cover_btn_handler",f"Button pressed!, is scan: {self.scanner.tracking}, is open: {self.cover_led.value()}")

        if self.cover_led.value() == 1:
            self.cover_led.value(0)
            self.logger.info("CoverCtl.cover_btn_handler","Close cover (Turn off led)")
        
        elif self.cover_led.value() == 0 and self.scanner.tracking:
            self.cover_led.value(1)
            self.logger.info("CoverCtl.cover_btn_handler","Open cover (Turn on LED)")

        elif self.cover_led.value() == 0 and not self.scanner.tracking:
            self.logger.info("CoverCtl.cover_btn_handler","Cant open when no device in range!")
        
        else:
            self.logger.info("CoverCtl.cover_btn_handler","no op")
        self.logger.info("CoverCtl.cover_btn_handler","-------------------------------------------------------------------------------")
