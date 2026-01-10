import time
from machine import Pin, PWM
from internal.ha_api import HAClient
from internal.logging import Logger
from config import GDO_RUN_ENTITY_ID

def startup(
		logger: Logger,
    ha_client: HAClient,
		cvr_open_led: Pin,
		tracking_led: Pin,
		lock_led: Pin,
		run_led: Pin,
		od_cvr_led: Pin,) -> bool:
	
  logger.info("startup","System starting...")

  # All off
  cvr_open_led.off()
  tracking_led.off()
  lock_led.off()
  run_led.off()
  od_cvr_led.off()

  logger.info("startup","Cover Open LED")
  wink(cvr_open_led)

  logger.info("startup","Tracking LED")
  wink(tracking_led)

  logger.info("startup","Lock LED")
  wink(lock_led)

  logger.info("startup","Run LED")
  wink(run_led)

  logger.info("startup","Outdoor Cover LED")
  wink(od_cvr_led)

  logger.info("startup","Connecting to HA...")
  connect(ha_client, run_led)
  logger.info("startup","Connected to HA!")

  # All off
  cvr_open_led.off()
  tracking_led.off()
  lock_led.off()
  run_led.off()
  od_cvr_led.off()

  logger.info("startup","🎉 Startup complete")
  return True

def wink(led: Pin) -> None:
  led.on()
  time.sleep(0.2)
  led.off()

def connect(ha_client: HAClient, led: Pin) -> None:

  # Start off with blinking led
  led.off() # Set initial condition 
  pwm = PWM(led)
  pwm.init(freq=10,duty_u16=32768) # ~50% duty (0..65535)

  # Try to connect
  if ha_client.connect_wifi():
    pwm.deinit()
    led.off()
  else:
    raise Exception("Unable to connect to WiFi!") 

  # Show a slight pause in the blink before we continue
  pwm.deinit()
  led.off()
  time.sleep(1)

  data, err = ha_client.get_state(entity_id=GDO_RUN_ENTITY_ID)
  if data:
    pwm.deinit()
    led.off()
  else:
    raise Exception(f"Unable to connect to HA entity: {GDO_RUN_ENTITY_ID}")
