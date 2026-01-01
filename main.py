import asyncio
from machine import Pin
from internal.bluetooth_scanner import BLEScanner
from internal.cover_ctl import CoverCtl

#
# main
#
async def main():
 
  # Scanner
  scanner = BLEScanner(mode="track", led_id="GP14")
  asyncio.create_task(scanner.run())

  # Cover Control
  cover = CoverCtl(
     cover_btn_id="GP16",
     cover_led_id="GP15",
     scanner=scanner)
  
  # Run forever
  while True:
      await asyncio.sleep_ms(1000)

# Run it
asyncio.run(main())
