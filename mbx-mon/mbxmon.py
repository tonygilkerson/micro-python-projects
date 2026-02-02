from logging import Logger
from lora import LoRa
from machine import Pin
import time

class MbxMon:
  """
  MbxMon - Mailbox Monitor class used to monitor the mailbox out by the street
  """

  logger: Logger
  led_onboard: Pin
  led_red: Pin
  led_green: Pin


  def __init__(self, 
               lora: LoRa,
               logger: Logger,
               led_onboard: Pin,
               led_red: Pin,
               led_green: Pin,
               ) -> None:
    """
    Initializes the MbxMon
    """
    self.logger = logger
    self.lora = lora
    self.led_onboard = led_onboard
    self.led_red = led_red
    self.led_green = led_green

  def blink_led(self, led: Pin, times=3, duration=0.2):
      """Blink an LED a specified number of times"""
      for _ in range(times):
          led.value(1)
          time.sleep(duration)
          led.value(0)
          time.sleep(duration)

  def monitor(self) -> None:
 
    self.logger.info("MbxMon.monitor","Start monitoring")
    self.logger.info("MbxMon.monitor","Sending 'ping' every few seconds")

    message_count = 0

    # Turn off all LEDs at start
    self.led_onboard.value(0)
    self.led_green.value(0)
    self.led_red.value(0)

    while True:
      try:

        # Create message
        message_count += 1
        message = f"ping #{message_count}"
        
        # Send message
        self.logger.info("global",f"✉️ Sending: {message}")

        self.lora.send(message)
        self.logger.info("global","✅ Sent successfully")

        # Blink onboard LED to indicate transmission
        self.blink_led(self.led_onboard)

        self.logger.info("global","💤 ZZZzzz...")
        time.sleep(5)

      except Exception as e:
          self.logger.info("MbxMon.monitor",f"Error: {e}")
          # blink_led(led_red)