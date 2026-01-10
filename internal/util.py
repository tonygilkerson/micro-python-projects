import time
from machine import Pin
from internal.ha_api import HAClient
from internal.logging import Logger

def startup(
		logger: Logger,
    ha_client: HAClient,
		cvr_open_led_id: str,
		tracking_led_id: str,
		lock_led_id: str,
		id_cvr_led_id: str,
		od_cvr_led_id: str,
		
		) -> bool:
	
  logger.info("startup","System startup")

  # Outs
  cvr_open_led = Pin(cvr_open_led_id, Pin.OUT)
  tracking_led = Pin(tracking_led_id, Pin.OUT)
  lock_led = Pin(lock_led_id, Pin.OUT)
  id_cvr_led = Pin(id_cvr_led_id, Pin.OUT)
  od_cvr_led = Pin(od_cvr_led_id, Pin.OUT)

  # All off
  cvr_open_led.off()
  tracking_led.off()
  lock_led.off()
  id_cvr_led.off()
  od_cvr_led.off()

  logger.info("startup","Cover Open LED")
  cvr_open_led.on()
  time.sleep(1)
  cvr_open_led.off()

  logger.info("startup","Tracking LED")
  tracking_led.on()
  time.sleep(1)
  tracking_led.off()

  logger.info("startup","Lock LED")
  lock_led.on()
  time.sleep(1)
  lock_led.off()

  logger.info("startup","Indoor Cover LED")
  id_cvr_led.on()
  time.sleep(1)
  id_cvr_led.off()

  logger.info("startup","Outdoor Cover LED")
  od_cvr_led.on()
  time.sleep(1)
  od_cvr_led.off()


  logger.info("startup","Connecting to WiFi...")
  while not ha_client.connect_wifi():
     logger.info("startup","WiFi not connected!")
  logger.info("startup","WiFi connected!")

  # All off
  cvr_open_led.off()
  tracking_led.off()
  lock_led.off()
  id_cvr_led.off()
  od_cvr_led.off()

  return True