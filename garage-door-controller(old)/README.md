# Garage Door Controller

A garage door controller

## Initial Setup

To initialize the project:

* clone parent project `micro-python-projects`
* open this sub-dir as a VSCode project `code garage-door-controller`
* right-click at the root in the vs code explorer
* open the command palette (shift+apple+p) search for  **Initialize MicroPico Project**
* This will add
  * `.vscode` folder
  * `.micropico` file
* Remove `visualstudioexptteam.vscodeintellicode` from the `.vscode/extensions.json` file just created.  It is no longer supported.
* Shared files

```sh
cd internal
ln -s ../../shared/logging.py logging.py
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
