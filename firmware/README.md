# Firmware

## ESP32 USB serial stability test

[`esp32_boot_stability`](esp32_boot_stability/esp32_boot_stability.ino) is a
USB-only diagnostic sketch for the serial resets tracked in
[#3](https://github.com/Gandalf-Exploras/robozakai/issues/3).

The sketch builds with the [Espressif Arduino ESP32 core](https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html).
For the ESP32-D0WD-V3 with 4 MB of flash detected on COM3, the Arduino CLI
target is `esp32:esp32:esp32` (ESP32 Dev Module).

1. Connect the ESP32 to the PC over USB with the peripherals disconnected.
2. Open the sketch in Arduino IDE, select the verified board profile and serial
   port, and compile and upload the sketch. Uploading replaces the current sketch.
3. Open Serial Monitor at 115200 baud and press the board's reset button once.
   Alternatively, start the [Python serial reader](../software/README.md#read-serial-output)
   with `COM3 --seconds 40` (substitute the current port), then press reset.
4. Check for `ROBOZAK_BOOT` followed by `HEARTBEAT seq=1 uptime_ms=...`.
   Over at least 30 seconds, verify that the sequence increments by one and uptime
   advances by approximately 1000 ms per message. A second boot marker or a return
   to sequence 1 during the observation indicates a restart.

Record the board profile and the serial result in the issue.

## ESP32 Wi-Fi LAN diagnostic

[`robozak_wifi_lan`](robozak_wifi_lan/robozak_wifi_lan.ino) checks Wi-Fi
association, DHCP, and a TCP echo between the computer and the ESP32. The
[Python runner](../software/README.md#verify-esp32-wi-fi-lan) manages the upload,
repeated trials, and restoration of the USB diagnostic.

In the 2026-11-20 bench session, the board associated and obtained an IPv4
address in two of three attempts. Neither connected attempt returned the TCP
echo, even with the computer on the same SSID. Local TCP communication remains
unverified. The USB diagnostic passed after restoration.

Servo limits and movement sequencing should be implemented as deterministic control logic.
