import asyncio
import machine
import time
from machine import Pin
from internal.logging import get_logger, Logger
from internal.cover_ctl import CoverCtl
from internal.ha_api import HAClient
import internal.util as util


#
# Pins
#
CVR_OPEN_LED_ID: str = "GP11"
TRACKING_LED_ID: str = "GP12" # DEVTODO - remove
LOCK_LED_ID: str     = "GP13"
RUN_LED_ID: str      = "GP14"
OD_CVR_LED_ID: str   = "GP15"

OD_CVR_BTN_ID: str   = "GP16"
ID_CVR_BTN_ID: str   = "GP17"
LOCK_BTN_ID: str     = "GP18"

#
# main
#
async def main():
 
  # LEDs
  cvr_open_led = Pin(CVR_OPEN_LED_ID, Pin.OUT)
  tracking_led = Pin(TRACKING_LED_ID, Pin.OUT)
  lock_led = Pin(LOCK_LED_ID, Pin.OUT)
  run_led = Pin(RUN_LED_ID, Pin.OUT)
  od_cvr_led = Pin(OD_CVR_LED_ID, Pin.OUT)

  # Buttons
  od_cover_btn = Pin(OD_CVR_BTN_ID, Pin.IN, Pin.PULL_UP)
  id_cover_btn = Pin(ID_CVR_BTN_ID, Pin.IN, Pin.PULL_UP)
  lock_btn = Pin(LOCK_BTN_ID, Pin.IN, Pin.PULL_UP)

  # Logger
  logger = get_logger()
  logger.set_level(Logger.INFO)
  logger.info("main","Start")

  # Create HA Client
  ha_client = HAClient(logger=logger)

  # Startup
  util.startup(
     logger=logger,
     ha_client=ha_client,
     cvr_open_led=cvr_open_led,
     tracking_led=tracking_led,
     lock_led=lock_led,
     run_led=run_led,
     od_cvr_led=od_cvr_led
     )

  # Cover Control
  logger.info("main","Create cover controller")
  cover = CoverCtl(
     logger=logger,
     ha_client=ha_client,
     od_cover_btn=od_cover_btn,
     od_cover_led=od_cvr_led,
     id_cover_btn=id_cover_btn,
     lock_btn=lock_btn,
     lock_led=lock_led,
     run_led=run_led,
     cvr_open_led=cvr_open_led)
  
  # Run forever
  while True:
      logger.debug("main",".",end="")
      util.status(logger=logger,
                  cvr_open_led=cvr_open_led,
                  tracking_led=tracking_led,
                  lock_led=lock_led,
                  run_led=run_led,
                  od_cvr_led=od_cvr_led)
      await asyncio.sleep_ms(1000)

def temp_handler():
   print("THIS IS A TEST")

# Run it
asyncio.run(main())
