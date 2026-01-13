import time
from machine import Pin, PWM
from internal.ha_api import HAClient
from internal.logging import Logger
from config import GDO_RUN_ENTITY_ID

def status(logger: Logger,
           cvr_open_led: Pin,
           tracking_led: Pin,
           lock_led: Pin,
           run_led: Pin,
           od_cvr_led: Pin) -> None:

  logger.debug("util.status",f"cvr_open_led: {cvr_open_led.value()}")
  logger.debug("util.status",f"tracking_led: {tracking_led.value()}")
  logger.debug("util.status",f"lock_led: {lock_led.value()}")
  logger.debug("util.status",f"run_led: {run_led.value()}")
  logger.debug("util.status",f"od_cvr_led: {od_cvr_led.value()}")
  logger.debug("util.status","---------------------------------------------------")

def wink(led: Pin) -> None:
  led.on()
  time.sleep(0.2)
  led.off()

def connect_wifi(
    ha_client: HAClient, 
    led: Pin, 
    pwm: PWM) -> None:

  # Try to connect
  if ha_client.connect_wifi():
    pwm.deinit()
    led.off()
  else:
    raise Exception("Unable to connect to WiFi!") 

def connect_ha(ha_client: HAClient, led: Pin, pwm: PWM) -> None:

  data, err = ha_client.get_state(entity_id=GDO_RUN_ENTITY_ID)
  

  if err is not None:
    raise Exception(f"Unable to connect to HA entity: {GDO_RUN_ENTITY_ID} error: {err}")
  else:
    pwm.deinit()
    led.off()

def stop_pwm(pwm: PWM, pin: Pin) -> None:
  # Best-effort: deinit PWM, reconfigure pin as output and drive it low
  try:
    pwm.deinit()
  except Exception:
    pass
  try:
    pin.init(Pin.OUT)
  except Exception:
    pass
  pin.off()

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

  logger.info("startup","Connecting to WiFi...")
  pwm1 = PWM(od_cvr_led)
  pwm1.init(freq=10,duty_u16=32768) # ~50% duty (0..65535)
  connect_wifi(ha_client, od_cvr_led, pwm1)
  logger.info("startup","Connected to WiFi...")

  logger.info("startup","Connecting to HA...")
  pwm2 = PWM(run_led)
  pwm2.init(freq=10,duty_u16=32768) # ~50% duty (0..65535)
  connect_ha(ha_client, run_led, pwm2)
  logger.info("startup","Connected to HA!")

  # Ensure PWMs are stopped and pins driven low
  logger.info("startup","Turn off od_cvr_led")
  stop_pwm(pwm1, od_cvr_led)
  logger.info("startup","Turn off run_led")
  stop_pwm(pwm2, run_led)

  # All off
  logger.info("startup","🧨 ALL Off")
  cvr_open_led.off()
  tracking_led.off()
  lock_led.off()
  run_led.off()
  od_cvr_led.off()

  logger.info("startup","🎉 Startup complete")
  return True
