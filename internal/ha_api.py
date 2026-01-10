
import network
import urequests
import time
from machine import Pin
from internal.logging import Logger
from config import WIFI_SSID, HA_URL
from config_private import WIFI_PASSWORD, HA_TOKEN

class HAClient:
  """Home Assistant Client"""
  led: Pin
  logger: Logger

  def __init__(self,logger: Logger,) -> None:
      # Logger
      self.logger = logger

  def connect_wifi(self) -> bool:
      """Connect to WiFi network"""
      wlan = network.WLAN(network.STA_IF)
      wlan.active(True)
      
      if not wlan.isconnected():
          self.logger.info("HAClient.connect_wifi","Connecting to WiFi...")
          wlan.connect(WIFI_SSID, WIFI_PASSWORD)
          
          timeout = 10
          while not wlan.isconnected() and timeout > 0:
              time.sleep(1)
              timeout -= 1
          
          if wlan.isconnected():
              self.logger.info("HAClient.connect_wifi","✓ WiFi connected!")
              self.logger.info("HAClient.connect_wifi",f"IP Address: {wlan.ifconfig()[0]}")
              return True
          else:
              self.logger.info("HAClient.connect_wifi","✗ WiFi connection failed")
              return False
      else:
          self.logger.info("HAClient.connect_wifi",f"✓ Already connected: {wlan.ifconfig()[0]}")
          return True

  def get_state(self, entity_id) -> tuple:
    """Get the state of any Home Assistant entity.

    Returns a tuple (data, err). On success `data` is the parsed
    JSON response and `err` is None. On failure `data` is None and
    `err` is an Exception describing the failure.
    """
    url = f"{HA_URL}/api/states/{entity_id}"
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        self.logger.info("HAClient.get_state",f"📡 Getting state of: {entity_id}")
        response = urequests.get(url, headers=headers, timeout=5)
        
        # Print raw response body
        self.logger.debug("HAClient.get_state",f"Raw Response Body: {response.text}")

        if response.status_code == 200:
            data = response.json()
            self.logger.info("HAClient.get_state",f"✓ State: {data['state']}")
            self.logger.info("HAClient.get_state",f"  Attributes: {data.get('attributes', {})}")
            response.close()
            return data, None
        else:
            err = Exception(f"HTTP {response.status_code}")
            self.logger.info("HAClient.get_state",f"✗ Error: {err}")
            response.close()
            return None, err
            
    except Exception as e:
        self.logger.info("HAClient.get_state",f"✗ Exception: {e}")
        return None, e

  def send_notification(self,title, message):
      """Send a notification to the Home Assistant mobile app"""
      url = f"{HA_URL}/api/services/notify/notify"
      headers = {
          "Authorization": f"Bearer {HA_TOKEN}",
          "Content-Type": "application/json"
      }
      payload = {
          "title": title,
          "message": message
      }
      
      try:
          self.logger.info("HAClient.send_notification",f"📱 Sending notification: {title}")
          response = urequests.post(url, headers=headers, json=payload, timeout=5)
          
          if response.status_code == 200:
              self.logger.info("HAClient.send_notification",f"✓ Notification sent!")
              response.close()
              return True
          else:
              self.logger.info("HAClient.send_notification",f"✗ Error: HTTP {response.status_code}")
              response.close()
              return False
              
      except Exception as e:
          self.logger.info("HAClient.send_notification",f"✗ Exception: {e}")
          return False

