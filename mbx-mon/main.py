"""
LoRa Ping Sender for Raspberry Pi Pico
Sends "ping" message every 10 seconds using RFM95W
Waits for ACK and blinks Green LED (GP12) on success or Red LED (GP13) on timeout
Uses wybiral/micropython-lora library (https://github.com/wybiral/micropython-lora)
Copy https://github.com/wybiral/micropython-lora/lora.py to lora.py
"""

import time
from machine import Pin, SPI
from lora import LoRa
from logging import get_logger, Logger
from mbxmon import MbxMon

# Logger
logger = get_logger()
logger.set_level(Logger.INFO)
logger.info("global","Start")

# Pin definitions (matching your wiring)
LORA_EN = 15
LORA_MISO = 16
LORA_CS = 17
LORA_SCK = 18
LORA_MOSI = 19
LORA_RST = 20
LORA_G0 = 21  # DIO0 / RX pin
LORA_G1 = 22

# Configure pins
en = Pin(LORA_EN, Pin.OUT, value=1)
cs = Pin(LORA_CS, Pin.OUT, value=1)
rst = Pin(LORA_RST, Pin.OUT)
rx = Pin(LORA_G0, Pin.IN, Pin.PULL_DOWN)

# LED pins
led_onboard = Pin(25, Pin.OUT)
led_red = Pin(12, Pin.OUT)
led_green = Pin(13, Pin.OUT)

# Reset
rst.value(0); time.sleep(0.1)
rst.value(1); time.sleep(0.1)


# Configure SPI bus
logger.info("global","Configure SPI bus")
spi = SPI(0,
          baudrate=1_000_000,
          polarity=0,
          phase=0,
          sck=Pin(LORA_SCK),
          mosi=Pin(LORA_MOSI),
          miso=Pin(LORA_MISO))

# Initialize LoRa module
logger.info("global","Initialize LoRa module")
lora = LoRa(spi, cs=cs, rx=rx, rst=rst, frequency=915.0)

# Configure LoRa parameters to match your hub
lora.set_spreading_factor(10)
lora.set_coding_rate(5)
lora.set_bandwidth(250000)
lora.set_preamble_length(8)
lora.set_sync_word(0x12)
lora.set_crc(True)

# Create MbxMon Instance
mbxmon = MbxMon(
  logger=logger,
  lora=lora,
  led_onboard=led_onboard,
  led_red=led_red,
  led_green=led_green)

mbxmon.monitor()
