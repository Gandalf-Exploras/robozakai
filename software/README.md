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
