"""
LoRa Ping Sender for Raspberry Pi Pico
Sends "ping" message every 10 seconds using RFM95W
Uses wybiral/micropython-lora library (https://github.com/wybiral/micropython-lora)
Copy https://github.com/wybiral/micropython-lora/lora.py to lora.py
"""

import time
from machine import Pin, SPI
from lora import LoRa

# Pin definitions (matching your wiring)
# Pin 20 (GP15) -->  EN 
# Pin 21 (GP16) --> MISO
# Pin 22 (GP17) -->  CS 
# Pin 24 (GP18) --> SCK 
# Pin 25 (GP19) --> MOSI
# Pin 26 (GP20) --> RST 
# Pin 27 (GP21) -->  G0 
# Pin 29 (GP22) -->  G1 

LORA_EN = 15
LORA_MISO = 16
LORA_CS = 17
LORA_SCK = 18
LORA_MOSI = 19
LORA_RST = 20
LORA_G0 = 21  # DIO0 / RX pin
LORA_G1 = 22 # ??

# Configure pins
en = Pin(LORA_EN, Pin.OUT, value=1) # enable the radio (EN pin must be high)
cs = Pin(LORA_CS, Pin.OUT, value=1) # Start HIGH, enable the radio by default
rst = Pin(LORA_RST, Pin.OUT)
rx = Pin(LORA_G0, Pin.IN, Pin.PULL_DOWN)  # IRQ pin; pick PULL_DOWN or PULL_UP per wiring
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
# Pin 20 (GP15) -->  EN 
# Pin 21 (GP16) --> MISO
# Pin 22 (GP17) -->  CS 
# Pin 24 (GP18) --> SCK 
# Pin 25 (GP19) --> MOSI
# Pin 26 (GP20) --> RST 
# Pin 27 (GP21) -->  G0 
# Pin 29 (GP22) -->  G1 

# Initialize LoRa module
print("Initialize LoRa module")
lora = LoRa(spi, cs=cs, rx=rx, rst=rst, frequency=915.0)  # 915.0 MHz


# Optional: Configure LoRa parameters (defaults are usually fine)
# lora.setSpreadingFactor(7)  # 7-12, higher = longer range but slower
# lora.setTxPower(14)  # 2-20 dBm

# LED for visual feedback
led = Pin(25, Pin.OUT)

print("LoRa ping sender initialized")
print("Sending 'ping' every 10 seconds\n")

message_count = 0

while True:
    try:
        # Create message
        message_count += 1
        message = f"ping #{message_count}"
        
        # Send message (blocking call)
        print(f"Sending: {message}")
        lora.send(message)
        
        # Blink LED to indicate transmission
        led.value(1)
        time.sleep(0.1)
        led.value(0)
        
        print("Sent successfully\n")
        
        # Wait 10 seconds
        time.sleep(5)
        
    except Exception as e:
        print(f"Error: {e}")
        led.value(0)
        time.sleep(1)