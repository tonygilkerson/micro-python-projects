
import network
import urequests
import time
from machine import Pin
from config import WIFI_SSID, WIFI_PASSWORD, HA_URL, HA_TOKEN

class HAClient:
  """Home Assistant Client"""
    
  def connect_wifi(self) -> bool:
      """Connect to WiFi network"""
      wlan = network.WLAN(network.STA_IF)
      wlan.active(True)
      
      if not wlan.isconnected():
          print("Connecting to WiFi...")
          wlan.connect(WIFI_SSID, WIFI_PASSWORD)
          
          timeout = 10
          while not wlan.isconnected() and timeout > 0:
              print(".", end="")
              time.sleep(1)
              timeout -= 1
          
          if wlan.isconnected():
              print(f"\n✓ WiFi connected!")
              print(f"IP Address: {wlan.ifconfig()[0]}")
              return True
          else:
              print("\n✗ WiFi connection failed")
              return False
      else:
          print(f"✓ Already connected: {wlan.ifconfig()[0]}")
          return True

  def get_state(self, entity_id):
      """Get the state of any Home Assistant entity"""
      url = f"{HA_URL}/api/states/{entity_id}"
      headers = {
          "Authorization": f"Bearer {HA_TOKEN}",
          "Content-Type": "application/json"
      }
      
      try:
          print(f"\n📡 Getting state of: {entity_id}")
          response = urequests.get(url, headers=headers, timeout=5)
          
          # Print raw response body
          print(f"Raw Response Body: {response.text}")

          if response.status_code == 200:
              data = response.json()
              print(f"✓ State: {data['state']}")
              print(f"  Attributes: {data.get('attributes', {})}")
              response.close()
              return data
          else:
              print(f"✗ Error: HTTP {response.status_code}")
              response.close()
              return None
              
      except Exception as e:
          print(f"✗ Exception: {e}")
          return None

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
          print(f"\n📱 Sending notification: {title}")
          response = urequests.post(url, headers=headers, json=payload, timeout=5)
          
          if response.status_code == 200:
              print(f"✓ Notification sent!")
              response.close()
              return True
          else:
              print(f"✗ Error: HTTP {response.status_code}")
              response.close()
              return False
              
      except Exception as e:
          print(f"✗ Exception: {e}")
          return False

