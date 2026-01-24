# Garage Door Controller

A garage door controller

## Ref

* [raspberry-pi-pico-python-sdk](https://datasheets.raspberrypi.com/pico/raspberry-pi-pico-python-sdk.pdf)
* [pico-micropython-examples](https://github.com/raspberrypi/pico-micropython-examples)
* [micropython rp2 ref](https://docs.micropython.org/en/latest/rp2/quickref.html)

## Initial Setup

```sh
# Install Extension
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension paulober.pico-w-go
```

To initialize the project:

* clone this repo
* right-click at the root in the vs code explorer
* select **Initialize MicroPico Project**
* This will add
  * `.vscode` folder
  * `.micropico` file

### MicroPython remote control

```sh
pip3 install mpremote # one-time-task

# Make sure this is in your path and comes before the MacOS installed python
/Users/tonygilkerson/Library/Python/3.9/bin

# Example usage
mpremote ls                       # List files on Pico
mpremote cp myfile.py :myfile.py  # Copy file TO Pico
mpremote cp :main.py ./main.py    # Copy file FROM Pico to local
mpremote run blink.py             # Run a Python file without copying
mpremote repl                     # Connect to REPL
mpremote mount .                  # Mount Pico filesystem (access like local folder)
mpremote reset                    # Reset Pico
mpremote soft-reset               # Soft reset (reload code)

# Execute Python command
mpremote exec "import os; print(os.listdir())"

# Terminal
ls /dev/tty.usb*                  # hopefully there is just one, use it below
minicom -b 115200 -o -D /dev/tty.usbmodem1101
```

## Deploy

```sh
#mpremote fs cp main.py :main.py
mpremote fs mkdir /internal
mpremote fs cp config.py :config.py
mpremote fs cp internal/bluetooth_scanner.py :internal/bluetooth_scanner.py
mpremote fs cp internal/__init__.py :/internal/__init__.py
mpremote reset
```
