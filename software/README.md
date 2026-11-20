# Computer software

This directory is reserved for the Python application running on a computer. Its responsibilities may include communication, a user interface, and optional AI features.

The communication protocol and dependencies will be chosen once the controller is defined.

## List serial ports (Windows)

With Python installed, run from the repository root:

```powershell
py software/list_serial_ports.py
```

The script uses the Python standard library and lists port names without opening them or sending data. A listed port is not proof that a particular board is connected; compare the list before and after connecting the board if needed.

## Read serial output

Create a virtual environment and install the serial dependency once:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r software/requirements.txt
```

Then listen for 10 seconds (replace `COM3` with the board's port):

```powershell
.\.venv\Scripts\python.exe software/read_serial.py COM3
```

The default is 115200 baud; use `--baud` and `--seconds` to change the settings. The script does not send serial data. Opening a serial port can reset some boards, and a quiet port does not necessarily indicate a fault: the firmware may not print anything or may use a different baud rate.

## Verify ESP32 serial commands

Upload the [ESP32 diagnostic sketch](../firmware/README.md#esp32-usb-serial-stability-test)
and close any serial monitor using the board's port. With the same virtual
environment, run the following command, substituting the current port for `COM3`.

```powershell
.\.venv\Scripts\python.exe software/check_serial_roundtrip.py COM3
```

The client sends 20 sequential `PING <id>` commands at 115200 baud and checks
that each matching `PONG <id>` arrives within one second. It also checks that
`UNKNOWN` returns `ERR`. The firmware accepts ASCII decimal IDs, one command per
line, with LF or CRLF endings. Heartbeats share the same serial connection.

## Verify ESP32 Wi-Fi LAN

Connect the PC to the target Wi-Fi network, close any serial monitor, and run
from the repository root using Arduino CLI, the Espressif ESP32 core, and pySerial.

```powershell
.\.venv\Scripts\python.exe software/check_wifi_lan.py COM3 'YOUR_SSID'
```

Enter the passphrase at the hidden prompt, or add `--secret-reference` with an
`op://` reference to use the 1Password CLI. The session reads the passphrase
once and reuses it in memory for all attempts. The ESP32 uses volatile Wi-Fi
configuration. `--count` defaults to 3. The runner temporarily uploads the LAN
diagnostic, then restores the repository's USB diagnostic and verifies it.
