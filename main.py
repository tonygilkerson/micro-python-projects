from internal.bluetooth_scanner import BLEScanner





scanner = BLEScanner(mode="discovery", led_id="LED")
scanner.run()