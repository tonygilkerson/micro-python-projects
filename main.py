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
  logger.info("main","Create scanner")
  scanner = BLEScanner(
     logger=logger,
     mode="track",
     led_id="GP14")
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

# Run it
asyncio.run(main())
