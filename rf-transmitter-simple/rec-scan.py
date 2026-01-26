# 433MHz RF Receiver for Raspberry Pi Pico
# Listens for RC Switch protocol signals and prints them

from machine import Pin
import time

class RFReceiver:
    def __init__(self, pin_number):
        self.rx_pin = Pin(pin_number, Pin.IN)
        
        # RC Switch Protocol timings (in microseconds)
        self.protocols = {
            1: {'pulse_length': 350, 'sync': (1, 31), 'zero': (1, 3), 'one': (3, 1)},
            2: {'pulse_length': 650, 'sync': (1, 10), 'zero': (1, 2), 'one': (2, 1)},
            3: {'pulse_length': 100, 'sync': (30, 71), 'zero': (4, 11), 'one': (9, 6)},
            4: {'pulse_length': 380, 'sync': (1, 6), 'zero': (1, 3), 'one': (3, 1)},
            5: {'pulse_length': 500, 'sync': (6, 14), 'zero': (1, 2), 'one': (2, 1)},
        }
        
        self.tolerance = 0.3  # 30% tolerance
        self.min_pulse = 100  # Minimum pulse length in us
        self.max_pulse = 10000  # Maximum pulse length in us
        
    def measure_pulse(self, level, timeout_us=1000000):
        """Measure the duration of a pulse at the given level"""
        start = time.ticks_us()
        while self.rx_pin.value() == level:
            if time.ticks_diff(time.ticks_us(), start) > timeout_us:
                return 0
        return time.ticks_diff(time.ticks_us(), start)
    
    def is_sync(self, high_us, low_us, protocol):
        """Check if the pulses match a sync pattern"""
        p = self.protocols[protocol]
        pulse_len = p['pulse_length']
        sync = p['sync']
        
        expected_high = pulse_len * sync[0]
        expected_low = pulse_len * sync[1]
        
        tol_high = expected_high * self.tolerance
        tol_low = expected_low * self.tolerance
        
        return (abs(high_us - expected_high) < tol_high and 
                abs(low_us - expected_low) < tol_low)
    
    def decode_bit(self, high_us, low_us, protocol):
        """Decode a bit based on pulse timings"""
        p = self.protocols[protocol]
        pulse_len = p['pulse_length']
        
        # Check for '0' bit
        zero = p['zero']
        expected_high_0 = pulse_len * zero[0]
        expected_low_0 = pulse_len * zero[1]
        tol_high_0 = expected_high_0 * self.tolerance
        tol_low_0 = expected_low_0 * self.tolerance
        
        if (abs(high_us - expected_high_0) < tol_high_0 and 
            abs(low_us - expected_low_0) < tol_low_0):
            return '0'
        
        # Check for '1' bit
        one = p['one']
        expected_high_1 = pulse_len * one[0]
        expected_low_1 = pulse_len * one[1]
        tol_high_1 = expected_high_1 * self.tolerance
        tol_low_1 = expected_low_1 * self.tolerance
        
        if (abs(high_us - expected_high_1) < tol_high_1 and 
            abs(low_us - expected_low_1) < tol_low_1):
            return '1'
        
        return None
    
    def listen(self):
        """Listen for RF signals and decode them"""
        print("Listening for RF signals on GPIO{}...".format(self.rx_pin))
        print("Press Ctrl+C to stop\n")
        
        while True:
            # Wait for a signal to start (pin goes high)
            while self.rx_pin.value() == 0:
                time.sleep_ms(1)
            
            # Measure first pulse
            high_us = self.measure_pulse(1, timeout_us=50000)
            if high_us == 0 or high_us < self.min_pulse:
                continue
                
            low_us = self.measure_pulse(0, timeout_us=50000)
            if low_us == 0 or low_us < self.min_pulse:
                continue
            
            # Try to match sync pattern for each protocol
            for protocol_num in self.protocols:
                if self.is_sync(high_us, low_us, protocol_num):
                    # Found sync! Try to decode the data
                    code = ''
                    bit_count = 0
                    max_bits = 32  # Most codes are 24 bits, but support up to 32
                    
                    while bit_count < max_bits:
                        high_us = self.measure_pulse(1, timeout_us=10000)
                        if high_us == 0 or high_us < self.min_pulse:
                            break
                            
                        low_us = self.measure_pulse(0, timeout_us=10000)
                        if low_us == 0 or low_us < self.min_pulse:
                            break
                        
                        bit = self.decode_bit(high_us, low_us, protocol_num)
                        if bit is None:
                            break
                        
                        code += bit
                        bit_count += 1
                    
                    # Print if we got a valid code (at least 8 bits)
                    if len(code) >= 8:
                        print("=" * 50)
                        print(f"Received RF Signal!")
                        print(f"Protocol: {protocol_num}")
                        print(f"Code: {code}")
                        print(f"Length: {len(code)} bits")
                        print(f"Hex: 0x{int(code, 2):X}")
                        print("=" * 50)
                        print()
                    
                    break
            
            # Small delay to avoid overwhelming the CPU
            time.sleep_ms(10)

# Main program
def main():
    # Initialize receiver on GPIO15
    receiver = RFReceiver(pin_number=15)
    
    try:
        receiver.listen()
    except KeyboardInterrupt:
        print("\nStopped listening")


if __name__ == '__main__':
    main()