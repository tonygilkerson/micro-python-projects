from micropython import const
import bluetooth
import time
from machine import Pin

# Hardware setup: Onboard LED to indicate tracking status
led = Pin("LED", Pin.OUT)

# Bluetooth Event Constants
_IRQ_SCAN_RESULT = const(5)  # Event triggered when a BLE device is found during scanning
_IRQ_SCAN_DONE = const(6)    # Event triggered when scanning stops

# Signal Strength and Timing Thresholds
VERY_CLOSE_RSSI = const(-40)  # RSSI threshold to filter close devices
TIMEOUT_MS = const(500)       # Time (ms) before assuming target device is out of range


class BLEScanner:
    """
    A Bluetooth Low Energy (BLE) scanner for the Raspberry Pi Pico W.

    This scanner operates in three modes:
    - 'discovery' mode: Scans for all nearby BLE devices and prints their MAC addresses.
    - 'track' mode: Continuously monitors for a specific MAC address and turns on an LED when detected.
    - 'track-apple' mode: Tracks any Apple device in close proximity (ignores MAC randomization).

    Attributes:
        mode (str): The scanning mode, either 'discovery', 'track', or 'track-apple'.
        target_mac (str, optional): The MAC address of the target device in 'track' mode.
        last_seen (int): Timestamp of when the target device was last detected.
    """

    def __init__(self, mode="discovery", target_mac=None):
        """
        Initializes the BLE scanner.

        Args:
            mode (str): The mode to run the scanner in ('discovery', 'track', or 'track-apple').
            target_mac (str, optional): The MAC address to track in 'track' mode.
        """
        self.ble = bluetooth.BLE()  # Initialize BLE interface
        self.mode = mode
        self.target_mac = target_mac
        self.last_seen = 0  # Track last detection time for tracking mode

    def bt_irq(self, event, data):
        """
        Bluetooth event handler, triggered on scan events.

        Args:
            event (int): The type of BLE event.
            data (tuple): Data associated with the event.
        """
        if event == _IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data

            # Filter devices based on RSSI threshold (indicating proximity)
            if rssi >= VERY_CLOSE_RSSI:
                addr_str = ':'.join(['{:02x}'.format(b) for b in addr])
                
                # Parse advertising data to extract device info
                parsed = parse_adv_data(adv_data)

                if self.mode == "discovery":
                    device_name = parsed.get('name', 'Unknown')
                    print(f"Device: {device_name} | MAC: {addr_str} | RSSI: {rssi}dB")
                    if 'manufacturer' in parsed:
                        mfg_hex = parsed['manufacturer'].hex()
                        print(f"  Manufacturer: {mfg_hex}")
                        if is_apple_device(parsed):
                            print(f"  -> APPLE DEVICE")
                    if 'services' in parsed:
                        print(f"  Services: {bytes(parsed['services']).hex()}")
                    print()  # Blank line for readability

                elif self.mode == "track" and addr_str == self.target_mac:
                    print(f"Target device found nearby! RSSI: {rssi}dB")
                    led.on()  # Indicate device presence with LED
                    self.last_seen = time.ticks_ms()  # Update last seen time
                
                elif self.mode == "track-apple" and is_apple_device(parsed):
                    print(f"Apple device nearby! MAC: {addr_str} | RSSI: {rssi}dB")
                    led.on()  # Indicate device presence with LED
                    self.last_seen = time.ticks_ms()  # Update last seen time

    def run(self):
        """
        Starts the BLE scanning process in the selected mode.
        Continuously scans for BLE devices and processes results based on mode.

        Scanning parameters:
        - duration_ms (int): Scans for 1 second per cycle.
        - interval_us (int): Time between scan cycles (30ms).
        - window_us (int): Active scan time within each cycle (30ms).
        - active (bool): Uses active scanning to request additional scan data.

        These values ensure:
        - Scanning does not **block other operations** in the loop.
        - The scan is **responsive** while allowing the CPU time to process other tasks.
        - Devices can be detected **frequently** while avoiding power starvation.
        """
        self.ble.active(True)  # Enable BLE
        self.ble.irq(self.bt_irq)  # Register event handler

        print(f"Scanning for BLE devices in {self.mode} mode...")

        while True:
            # Start a BLE scan with a 1-second duration, scanning every 30ms
            # This prevents the loop from being blocked by scanning for too long.
            self.ble.gap_scan(1000, 30000, 30000, True)

            # In track mode, turn off LED if device is not detected for a while
            if self.mode == "track" and time.ticks_diff(time.ticks_ms(), self.last_seen) > TIMEOUT_MS:
                led.off()

            time.sleep_ms(100)  # Short delay to avoid excessive CPU usage and allow other operations

def is_apple_device(parsed_data):
    """
    Check if the parsed advertising data indicates an Apple device.
    Apple's company identifier is 0x004C (which appears as '4c00' in little-endian hex).
    
    Args:
        parsed_data (dict): Parsed advertising data from parse_adv_data().
    
    Returns:
        bool: True if this is an Apple device, False otherwise.
    """
    if 'manufacturer' in parsed_data:
        mfg_data = parsed_data['manufacturer']
        # Check if manufacturer data starts with Apple's company ID (0x004C)
        if len(mfg_data) >= 2 and mfg_data[0] == 0x4C and mfg_data[1] == 0x00:
            return True
    return False

# Add helper function to parse advertising data
def parse_adv_data(adv_data):
    """
    Parse BLE advertising data to extract useful information.
    Returns: dict with 'name', 'manufacturer', 'services', etc.
    """
    result = {}
    i = 0
    while i < len(adv_data):
        length = adv_data[i]
        if length == 0:
            break
        
        ad_type = adv_data[i + 1]
        data = adv_data[i + 2:i + 1 + length]
        
        # Complete or shortened local name
        if ad_type in (0x08, 0x09):
            try:
                result['name'] = bytes(data).decode('utf-8')
            except:
                pass
        
        # Manufacturer specific data
        elif ad_type == 0xFF:
            result['manufacturer'] = bytes(data)
        
        # Service UUIDs
        elif ad_type in (0x02, 0x03):  # 16-bit UUIDs
            result['services'] = data
        
        i += 1 + length
    
    return result

if __name__ == "__main__":
    try:
        # Start in discovery mode to find MAC addresses of nearby devices
        scanner = BLEScanner(mode="discovery")

        # To track a specific device (replace with discovered MAC address)
        # scanner = BLEScanner(mode="track", target_mac="aa:bb:cc:dd:ee:ff")
        
        # To track ANY Apple device in close proximity (works with MAC randomization)
        # scanner = BLEScanner(mode="track-apple")

        scanner.run()

    except KeyboardInterrupt:
        led.off()  # Ensure LED is off on exit
        scanner.ble.active(False)  # Disable BLE
        print("\nScanning stopped")
