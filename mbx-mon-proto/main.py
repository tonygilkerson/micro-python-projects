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

# Pin definitions (matching your wiring)
LORA_EN = 15
LORA_MISO = 16
LORA_CS = 17
LORA_SCK = 18
LORA_MOSI = 19
LORA_RST = 20
LORA_G0 = 21  # DIO0 / RX pin
LORA_G1 = 22

# ACK timeout in seconds
ACK_TIMEOUT = 3.0

# Global variable to store received message
received_message = None

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
print("Setup spi")
spi = SPI(0,
          baudrate=1_000_000,
          polarity=0,
          phase=0,
          sck=Pin(LORA_SCK),
          mosi=Pin(LORA_MOSI),
          miso=Pin(LORA_MISO))

# Initialize LoRa module
print("Initialize LoRa module")
lora = LoRa(spi, cs=cs, rx=rx, rst=rst, frequency=915.0)

# Configure LoRa parameters to match your hub
lora.set_spreading_factor(10)
lora.set_coding_rate(5)
lora.set_bandwidth(250000)
lora.set_preamble_length(8)
lora.set_sync_word(0x12)
lora.set_crc(True)

def on_receive(payload):
    """Callback function when LoRa packet is received"""
    global received_message
    try:
        received_message = payload.decode('utf-8', 'ignore')
        print(f"Received: {received_message}")
    except Exception as e:
        print(f"Decode error: {e}")

def blink_led(led, times=3, duration=0.2):
    """Blink an LED a specified number of times"""
    for _ in range(times):
        led.value(1)
        time.sleep(duration)
        led.value(0)
        time.sleep(duration)

def wait_for_ack(timeout=ACK_TIMEOUT):
    """
    Wait for ACK message with timeout
    Returns True if ACK received, False if timeout
    """
    global received_message
    
    print(f"Waiting for ACK (timeout: {timeout}s)...")
    
    # Clear any previous message
    received_message = None
    
    start_time = time.time()
    
    while (time.time() - start_time) < timeout:
        # Check if we received a message via the callback
        if received_message is not None:
            # Check if it's an ACK message
            if "ACK" in received_message:
                print("✓ ACK received!")
                received_message = None
                return True
            else:
                # Not an ACK, clear and keep waiting
                received_message = None
        
        time.sleep(0.01)
    
    print("✗ ACK timeout")
    return False

print("LoRa ping sender initialized")
print("Sending 'ping' every few seconds\n")

message_count = 0

# Turn off all LEDs at start
led_onboard.value(0)
led_green.value(0)
led_red.value(0)

while True:
    try:
        # Create message
        message_count += 1
        message = f"ping #{message_count}"
        
        # Send message
        print(f"Sending: {message}")
        lora.send(message)
        print("Sent successfully")
        
        # IMMEDIATELY enable RX mode and callback after send completes
        lora.on_recv(on_receive)
        lora.recv()
        
        # Blink onboard LED to indicate transmission
        led_onboard.value(1)
        time.sleep(0.1)
        led_onboard.value(0)
        
        # Wait for ACK
        if wait_for_ack():
            blink_led(led_green, times=3, duration=0.2)
        else:
            blink_led(led_red, times=3, duration=0.2)
        
        print()
        time.sleep(5)
        
    except Exception as e:
        print(f"Error: {e}")
        led_onboard.value(0)
        led_green.value(0)
        led_red.value(0)
        time.sleep(1)