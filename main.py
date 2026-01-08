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
ID_CVR_LED_ID: str   = "GP14"
OD_CVR_LED_ID: str   = "GP15"
OD_CVR_BTN_ID: str   = "GP16"
ID_CVR_BTN_ID: str   = "GP17"
LOCK_BTN_ID: str     = "GP18"

#
# main
#
async def main():
 

  # Logger
  logger = get_logger()
  logger.set_level(Logger.INFO)
  logger.info("main","Start")

  # Startup
  util.startup(
     logger=logger,
     cvr_open_led_id=CVR_OPEN_LED_ID,
     tracking_led_id=TRACKING_LED_ID,
     lock_led_id=LOCK_LED_ID,
     id_cvr_led_id=ID_CVR_LED_ID,
     od_cvr_led_id=OD_CVR_LED_ID
     )

  # Connect to WiFi
  ha = HAClient(logger=logger,led_id="GP14")
  while not ha.connect_wifi():
     logger.info("main","WiFi not connected!")
  logger.info("main","WiFi connected!")

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
