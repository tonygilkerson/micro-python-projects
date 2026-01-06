import asyncio
from machine import Pin
from internal.bluetooth_scanner import BLEScanner
from internal.logging import get_logger, Logger
from internal.cover_ctl import CoverCtl

#
# main
#
async def main():
 
  # Logger
  logger = get_logger()
  logger.set_level(Logger.INFO)
  logger.info("main","Start")

  # Scanner
  # DEVTODO I need to update the scanner accept a call-back function, the call back function is the same function that 
  #         is called when you press the od_cover_button.
  logger.info("main","Create scanner")
  scanner = BLEScanner(
     logger=logger,
     tracking_handler=temp_handler,
     mode="track",
     led_id="GP12")
  asyncio.create_task(scanner.run())

  # Cover Control
  logger.info("main","Create cover controller")
  cover = CoverCtl(
     logger=logger,
     cover_btn_id="GP16",
     cover_led_id="GP15",
     scanner=scanner)
  
  # Run forever
  while True:
      logger.debug("main",".")
      await asyncio.sleep_ms(1000)

def temp_handler():
   print("THIS IS A TEST")

# Run it
asyncio.run(main())
