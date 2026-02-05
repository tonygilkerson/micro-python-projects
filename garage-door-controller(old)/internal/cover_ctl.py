import asyncio
import micropython
import time
from machine import Pin
from internal.logging import Logger
from internal.ha_api import HAClient
from config import GDO_RUN_ENTITY_ID

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
    ha_client: HAClient
    is_locked: bool
    od_cover_btn: Pin
    od_cover_led: Pin
    id_cover_btn: Pin
    lock_btn: Pin
    lock_led: Pin
    run_led: Pin
    cvr_open_led: Pin
    od_cover_btn_last_press_ms: int
    in_cover_btn_last_press_ms: int
    lock_btn_last_press_ms: int

    def __init__(self,
                 logger: Logger,
                 ha_client: HAClient,
                 od_cover_btn: Pin,
                 od_cover_led: Pin,
                 id_cover_btn: Pin,
                 lock_btn: Pin,
                 lock_led: Pin,
                 run_led: Pin,
                 cvr_open_led: Pin,
                 ) -> None:
        """
        Initializes the cover controller
        """
        # Logger
        self.logger = logger


        # HA Client
        self.ha_client = ha_client

        # Locked by default
        self.is_locked = True
        self.lock_led = lock_led
        self.lock_led.on()

        # Cover Open indicator (used during development)
        self.cvr_open_led = cvr_open_led

        # Cover LED
        self.od_cover_led = od_cover_led
        self.od_cover_led.off()

        # Run LED
        self.run_led = run_led
        self.run_led.on()

        # Outdoor Cover Button
        self.od_cover_btn = od_cover_btn
        self.od_cover_btn_last_press_ms = 0
        self.od_cover_btn.irq(handler=self.od_cover_btn_irq, trigger=Pin.IRQ_FALLING)

        # Indoor Cover Button
        self.id_cover_btn = id_cover_btn
        self.id_cover_btn_last_press_ms = 0
        self.id_cover_btn.irq(handler=self.id_cover_btn_irq, trigger=Pin.IRQ_FALLING)

        # Lock Button
        self.lock_btn = lock_btn
        self.lock_btn_last_press_ms = 0
        self.lock_btn.irq(handler=self.lock_btn_irq, trigger=Pin.IRQ_FALLING)


    def lock_btn_irq(self, pin):
        """IRQ-safe handler: schedule main-context work"""
        # pass small int (pin id) to scheduled handler
        micropython.schedule(self.lock_btn_handler, "LOCK_BTN")

    def lock_btn_handler(self, arg):
        """Outdoor Cover Button Handler. Runs when the lock button is pressed
        Runs in main context via micropython.schedule"""
        now = time.ticks_ms()
        # simple debounce: ignore presses within 500ms
        if time.ticks_diff(now, self.lock_btn_last_press_ms) < 500:
            return
        self.lock_btn_last_press_ms = now

        self.logger.info("CoverCtl.lock_btn_handler",f"👉 PRESS lock button pressed")

        if self.is_locked:
            self.logger.info("CoverCtl.lock_btn_handler","🕹️ TOGGLE set is_locked=False")
            self.is_locked = False
            self.lock_led.off()
        else:
            self.logger.info("CoverCtl.lock_btn_handler","🕹️ TOGGLE set is_locked=True")
            self.is_locked = True
            self.lock_led.on()
             
    def od_cover_btn_irq(self, pin):
        """IRQ-safe handler: schedule main-context work"""
        # pass small int (pin id) to scheduled handler
        micropython.schedule(self.od_cover_btn_handler, "OD_COVER_BTN")

    def od_cover_btn_handler(self, arg):
        """Outdoor Cover Button Handler. Runs when the outdoor cover button is pressed
        Runs in main context via micropython.schedule"""
        now = time.ticks_ms()
        # simple debounce: ignore presses within 500ms
        if time.ticks_diff(now, self.od_cover_btn_last_press_ms) < 500:
            return
        self.od_cover_btn_last_press_ms = now

        self.logger.info("CoverCtl.od_cover_btn_handler",f"👉 PRESS outdoor cover button pressed")

        if self.is_locked:
            self.logger.info("CoverCtl.od_cover_btn_handler","🔒 LOCKED outdoor cover is not enabled when door is locked")
        else:
            self.logger.info("CoverCtl.od_cover_btn_handler","🕹️ TOGGLE outdoor cover")
            self.toggle_cover()

    def id_cover_btn_irq(self, pin):
        """IRQ-safe handler: schedule main-context work"""
        # pass small int (pin id) to scheduled handler
        micropython.schedule(self.id_cover_btn_handler, "ID_COVER_BTN")

    def id_cover_btn_handler(self, arg):
        """Indoor Cover Button Handler. Runs when the indoor cover button is pressed
        Runs in main context via micropython.schedule"""
        now = time.ticks_ms()
        # simple debounce: ignore presses within 500ms
        if time.ticks_diff(now, self.id_cover_btn_last_press_ms) < 500:
            return
        self.od_cover_btn_last_press_ms = now

        self.logger.info("CoverCtl.id_cover_btn_handler",f"👉 PRESS indoor cover button pressed")
        self.logger.info("CoverCtl.od_cover_btn_handler","🕹️ TOGGLE indoor cover")
        self.toggle_cover() 
        

    def toggle_cover(self)->None:
        self.logger.info("CoverCtl.toggle_cover","Get state of entity_id: {GDO_RUN_ENTITY_ID}")
        
        is_open,err = self.ha_client.get_state(GDO_RUN_ENTITY_ID)

        if err:
            self.logger.info("CoverCtl.toggle_cover","Oops! Something went wrong, do nothing, err: {err}")
            return

        if is_open:
            self.logger.info("CoverCtl.toggle_cover","Send CLOSE to HA")
            self.cvr_open_led.off()
            self.ha_client.set_toggle_state(False)
        else:
            self.logger.info("CoverCtl.toggle_cover","Send OPEN to HA")
            self.cvr_open_led.on()
            self.ha_client.set_toggle_state(True)
        