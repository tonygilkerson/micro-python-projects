"""
Simple Home Assistant API Test Script for Raspberry Pi Pico W

This script demonstrates how to:
1. Connect to WiFi
2. Call Home Assistant REST API
3. Get entity states
4. Turn on/off switches
5. Send custom data
"""

import network
import urequests
import time
from machine import Pin
from config import WIFI_SSID, WIFI_PASSWORD, HA_URL, HA_TOKEN

# ============================================
# WiFi Connection
# ============================================
def connect_wifi():
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

# ============================================
# Home Assistant API Functions
# ============================================


def get_ha_state(entity_id):
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


def turn_on_entity(entity_id):
    """Turn on a switch, light, or other entity"""
    domain = entity_id.split('.')[0]
    
    url = f"{HA_URL}/api/services/{domain}/turn_on"
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"entity_id": entity_id}
    
    try:
        print(f"\n🔛 Turning ON: {entity_id}")
        response = urequests.post(url, headers=headers, json=payload, timeout=5)
        
        if response.status_code == 200:
            print(f"✓ Success!")
            response.close()
            return True
        else:
            print(f"✗ Error: HTTP {response.status_code}")
            response.close()
            return False
            
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False


def turn_off_entity(entity_id):
    """Turn off a switch, light, or other entity"""
    domain = entity_id.split('.')[0]
    
    url = f"{HA_URL}/api/services/{domain}/turn_off"
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"entity_id": entity_id}
    
    try:
        print(f"\n🔴 Turning OFF: {entity_id}")
        response = urequests.post(url, headers=headers, json=payload, timeout=5)
        
        if response.status_code == 200:
            print(f"✓ Success!")
            response.close()
            return True
        else:
            print(f"✗ Error: HTTP {response.status_code}")
            response.close()
            return False
            
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False


def send_notification(title, message):
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


# ============================================
# Test Menu
# ============================================
if __name__ == "__main__":
    print("\n" + "="*50)
    print("Home Assistant API Test Script")
    print("="*50)
    
    # Connect to WiFi first
    if not connect_wifi():
        print("\n✗ Cannot proceed without WiFi")
    else:
        # Blink LED to show ready
        led = Pin("LED", Pin.OUT)
        for _ in range(3):
            led.on()
            time.sleep(0.2)
            led.off()
            time.sleep(0.2)
        
        print("\n✓ Ready! Uncomment test functions below:\n")
        
        # UNCOMMENT TO TEST:
        get_ha_state("device_tracker.aeg_iphone_xs_lts_hand_me_down")
        # turn_on_entity("light.living_room")
        # send_notification("Test", "Hello from Pico!")