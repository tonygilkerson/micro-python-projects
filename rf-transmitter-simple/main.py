from machine import Pin
import time

class RFTransmitter:
    def __init__(self, pin_number):
        self.tx_pin = Pin(pin_number, Pin.OUT)
        self.pulse_length = 350  # Protocol 1 timing in microseconds
    
    def transmit(self, high_pulses, low_pulses):
        self.tx_pin.value(1)
        time.sleep_us(self.pulse_length * high_pulses)
        self.tx_pin.value(0)
        time.sleep_us(self.pulse_length * low_pulses)
    
    def send_sync(self):
        self.transmit(1, 31)  # Sync signal for protocol 1
    
    def send_bit(self, bit):
        if bit == '1':
            self.transmit(3, 1)  # High: 3 pulses high, 1 pulse low
        else:
            self.transmit(1, 3)  # Low: 1 pulse high, 3 pulses low
    
    def send_code(self, code, repeat=5):
        for _ in range(repeat):
            self.send_sync()
            for bit in code:
                self.send_bit(bit)
            time.sleep_ms(10)

# Print to console
print("Start!")

# Onboard LED on Pico is GPIO25
led = Pin(25, Pin.OUT)

# Initialize 
rf = RFTransmitter(15)  # GPIO15
code = '001100110011001100110011'

while True:
    
    print("Sending RF code...")
    rf.send_code(code, repeat=5)
    led.on()
    time.sleep(3)

    led.off()
    time.sleep(3)
