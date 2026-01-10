import asyncio
import machine
import time
from machine import Pin
from internal.bluetooth_scanner import BLEScanner
from internal.logging import get_logger, Logger
from internal.cover_ctl import CoverCtl
from internal.ha_api import HAClient
import internal.util as util


#
# Pins
#
CVR_OPEN_LED_ID: str = "GP11"
TRACKING_LED_ID: str = "GP12"
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
 
  # Outs
  cvr_open_led = Pin(CVR_OPEN_LED_ID, Pin.OUT)
  tracking_led = Pin(TRACKING_LED_ID, Pin.OUT)
  lock_led = Pin(LOCK_LED_ID, Pin.OUT)
  run_led = Pin(RUN_LED_ID, Pin.OUT)
  od_cvr_led = Pin(OD_CVR_LED_ID, Pin.OUT)

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

  # Scanner
  # DEVTODO I need to update the scanner accept a call-back function, the call back function is the same function that 
  #         is called when you press the od_cover_button.
  logger.info("main","Create scanner")
  scanner = BLEScanner(
     logger=logger,
     tracking_handler=temp_handler,
     mode="track",
     led_id=TRACKING_LED_ID)
  asyncio.create_task(scanner.run())

  # Cover Control
  logger.info("main","Create cover controller")
  cover = CoverCtl(
     logger=logger,
     cover_btn_id=OD_CVR_BTN_ID,
     cover_led_id=OD_CVR_LED_ID,
     scanner=scanner)
  
  # Run forever
  while True:
      logger.debug("main",".")
      await asyncio.sleep_ms(1000)

def temp_handler():
   print("THIS IS A TEST")

# Run it
asyncio.run(main())
