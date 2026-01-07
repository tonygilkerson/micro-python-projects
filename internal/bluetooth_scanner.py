from micropython import const
import bluetooth
import time
import asyncio
from machine import Pin
from internal.logging import Logger

# MicroPython does not have typing; provide a tiny fallback so annotations don't error in editors
Callable = object
Optional = object
Any = object

# Bluetooth Event Constants
_IRQ_SCAN_RESULT = const(5)  # Event triggered when a BLE device is found during scanning
_IRQ_SCAN_DONE = const(6)    # Event triggered when scanning stops

# Signal Strength and Timing Thresholds
# VERY_CLOSE_RSSI = const(-45)  # RSSI threshold to filter close devices
VERY_CLOSE_RSSI = const(-35)  # RSSI threshold to filter close devices
TIMEOUT_MS = const(5000)      # Time (ms) before assuming target device is out of range


class BLEScanner:
    """
    A Bluetooth Low Energy (BLE) scanner for the Raspberry Pi Pico W.

    This scanner operates in three modes:
    - 'discovery' mode: Scans for all nearby BLE devices and prints their MAC addresses.
    - 'track' mode: Continuously monitors for a specific MAC address and turns on an LED when detected.
    - 'track-apple' mode: Tracks any Apple device in close proximity (ignores MAC randomization).

    Attributes:
        mode (str): The scanning mode, either 'discovery', 'track'.
        led (str): Tracking LED to indicate device presence. ex, LED, GP15 etc.
        last_seen (int): Timestamp of when the target device was last detected.
        tracking (bool): True when an Apple device is in range.
    """

    logger: Logger
    mode: str
    led: Pin
    ble: bluetooth.BLE
    last_seen: int
    tracking: bool
    # tracking_handler: Optional[Callable[..., Any]]
    tracking_handler: Callable

    def __init__(self,
                 logger: Logger,
                 tracking_handler: Callable = None,
                 mode: str = "discovery",
                 led_id: str = "LED",
                 ) -> None:
        """
        Initializes the BLE scanner.

        Args:
            logger (Logger): Class for handling logging
            tracking_handler (function): Handler to call when tracking starts
            mode (str): The mode to run the scanner in ('discovery', 'track', or 'track-apple').
            led_id (str|int): Pin id or name for the LED (e.g. 'LED', 'GP15', 25).
        """
        # Logger
        self.logger = logger

        # Hardware setup: Onboard LED to indicate tracking status
        self.led = Pin(led_id, Pin.OUT)
        self.led.off()

        self.ble = bluetooth.BLE()  # Initialize BLE interface
        self.mode = mode
        self.last_seen = 0
        self.tracking = False # Currently not tracking a device
        self.tracking_handler = tracking_handler

    def bt_irq(self, event, data):
        """
        Bluetooth event handler, triggered on scan events.

        Args:
            event (int): The type of BLE event.
            data (tuple): Data associated with the event.
        """
        
        # Why this method is not async:
        # bt_irq: must be synchronous and IRQ-safe — it's called from the BLE/interrupt context. 
        # It cannot use await, must not block, must avoid heap allocation, locking or long work. 
        # If you need heavier work, defer it (e.g. with micropython.schedule() or by setting a preallocated flag) and do the real work in main context.

        if event == _IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data

            # Filter devices based on RSSI threshold (indicating proximity)
            if rssi >= VERY_CLOSE_RSSI:
                addr_str = ':'.join(['{:02x}'.format(b) for b in addr])
                
                # Parse advertising data to extract device info
                parsed = self.parse_adv_data(adv_data)

                if self.mode == "discovery":
                    device_name = parsed.get('name', 'Unknown')
                    
                    if 'manufacturer' in parsed:
                        mfg_hex = parsed['manufacturer'].hex()
                        if self.is_apple_device(parsed):
                            ts = time.ticks_ms()
                            self.logger.info("BLEScanner.bt_irq",f"[{ts}ms] Device: {device_name} | MAC: {addr_str} | RSSI: {rssi}dB | APPLE DEVICE")
                    if 'services' in parsed:
                        self.logger.info("BLEScanner.bt_irq",f"  Services: {bytes(parsed['services']).hex()}")
                
                elif self.mode == "track" and self.is_apple_device(parsed):
                    self.logger.info("BLEScanner.bt_irq",f"Start tracking, Apple device nearby! | MAC: {addr_str} | RSSI: {rssi}dB")
                    self.set_tracking(True)

    def set_tracking(self, tracking_state: bool):
        
        # Check if this it the start of tracking
        if not self.tracking and tracking_state:
            self.logger.info("BLEScanner.set_tracking","Start tracking, TODO call handler")
            if callable(self.tracking_handler):
              self.tracking_handler()

        # Set tracking state
        self.tracking = tracking_state

        if tracking_state:
          # DEVTODO this might change when i add the handler, I will prob turn on/off LEDs in handler
          self.led.on()  # Indicate device presence with LED
          self.last_seen = time.ticks_ms()  # Update last seen time
        else:
          self.led.off()
          self.last_seen = 0

    async def run(self):
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
        self.ble.active(True)
        self.ble.irq(self.bt_irq)
        self.logger.info("BLEScanner.run",f"Scanning for BLE devices in {self.mode} mode...")

        while True:
            # gap_scan is non-blocking on Pico W (events arrive via bt_irq)
            self.ble.gap_scan(1000, 30000, 30000, True)

            if self.mode == "track" and time.ticks_diff(time.ticks_ms(), self.last_seen) > TIMEOUT_MS:
                self.set_tracking(False)

            await asyncio.sleep_ms(100)  # Short non-blocking delay to avoid excessive CPU usage


    def is_apple_device(self, parsed_data):
        """
        Check if the parsed advertising data indicates an Apple device.
        Apple's company identifier is 0x004C (which appears as '4c00' in little-endian hex).
        
        Args:
            parsed_data (dict): Parsed advertising data from parse_adv_data().
        
        Returns:
            bool: True if this is an Apple device, False otherwise.
        """
        # Why this method is not async:
        #
        # is_apple_device: a tiny, immediate boolean check (pure computation). Making it async would only add overhead 
        # and require await at each call site for no benefit.

        if 'manufacturer' in parsed_data:
            mfg_data = parsed_data['manufacturer']
            # Check if manufacturer data starts with Apple's company ID (0x004C)
            if len(mfg_data) >= 2 and mfg_data[0] == 0x4C and mfg_data[1] == 0x00:
                return True
        return False

    # Add helper function to parse advertising data
    def parse_adv_data(self, adv_data):
        """
        Parse BLE advertising data to extract useful information.
        Returns: dict with 'name', 'manufacturer', 'services', etc.
        """
        ## Why this method is not async:
        #
        # parse_adv_data: pure CPU-bound parsing. It doesn't need to yield to the event loop, so 
        # keeping it def avoids coroutine overhead and extra allocations. 
        #
        # Also it's called from bt_irq (or from a scheduled handler) so making it async would not help,
        # you'd still need to call it synchronously in the IRQ-deferred handler.
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

