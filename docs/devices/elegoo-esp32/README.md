# ELEGOO ESP32 development board

## Identification

| Item | Status |
| --- | --- |
| Manufacturer | ELEGOO, as reported by the owner |
| Board family | ESP32, as reported by the owner |
| Exact board and module model | Not yet confirmed; inspect the board and its markings in a photograph |
| Wireless | Wi-Fi and Bluetooth, as reported on the packaging; exact capabilities depend on the module |
| Arduino IDE | Compatibility reported on the packaging; board profile not yet confirmed |

The owner supplied the [Amazon product link](https://www.amazon.it/dp/B0D8T5XD3P) and the following listing details. The page was not directly accessible during research; these are product claims, not yet verified against the physical boards.

| Listing detail | Value |
| --- | --- |
| Product model | EL-SM-012 |
| ASIN | B0D8T5XD3P |
| Package contents | Three ESP-WROOM-32 development boards with USB-C |
| USB-to-serial chip | CP2102 |
| Reported software support | Arduino, MicroPython, NodeMCU |
| Wi-Fi modes | AP, STA, AP+STA |
| Storage capacity | 4 MB, according to the listing |
| Other listing fields | Two processors; Linux; LPDDR4 RAM; 802.11a/b/g/n. These fields require verification and may be inaccurate. |

Confirm the actual module and board markings from the owner's photograph.

For comparison, the [ESP-WROOM-32 datasheet](https://documentation.espressif.com/esp32-wroom-32_datasheet_en.html) describes one dual-core processor, 4 MB SPI flash, 520 KB internal SRAM, and 2.4 GHz 802.11b/g/n Wi-Fi. It does not establish the identity of the particular physical boards. Do not assume LPDDR4, 802.11a, or Linux support from the listing fields.

## Manufacturer resources

- [Local Espressif ESP32 development kits manual](esp-dev-kits-en-master-esp32.pdf): the ESP32-DevKitC V4 guide begins on PDF page 6. The manual covers multiple ESP32 development boards, not only this one.
- The owner compared the board with the photograph in [Espressif's ESP32-DevKitC V4 guide](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html) and reported a match. The pictured board appears to have USB-C, although the guide text describes Micro-USB. The pictured module is labeled ESP32-WROOM-32E; the exact marking on the owner's board remains to be checked. Verify the physical board's pin labels before wiring.
- [ELEGOO ESP32 introductory guide](https://wiki.elegoo.com/en/oshw-getting-started-%26-kits/first-look-esp32) and [tutorial index](https://wiki.elegoo.com/en/oshw-getting-started-%26-kits) cover an ELEGOO ESP32 starter kit; verify the board matches before following board-specific wiring or settings. The pages did not expose readable text to the research tool.
- [ELEGOO download center](https://www.elegoo.com/pages/download) lists tutorial resources under STEM Kits. No manual specific to EL-SM-012 was confirmed there.

## Connection observed on the project PC

- Windows identifies a Silicon Labs CP210x USB-to-UART bridge on **COM3**.
- The owner confirmed that COM3 disappears when the board is disconnected and returns when it is reconnected. Port numbers can change.
- Serial output was readable at **115200 baud** during a 10-second observation on 2026-11-19.

## Serial observation

The board repeatedly printed boot messages including `rst:0x10 (RTCWDT_RTC_RESET)` during the observation. The same pattern appeared during a second four-second observation after the owner disconnected and reconnected the board. This suggests repeated resets, but their cause is not established. The firmware currently installed and its expected behavior are unknown. Opening a serial port can reset some boards, so these observations alone do not establish what happens while the port is closed.

The owner then connected a second board; a five-second observation on COM3 showed the same repeated boot messages. Both tests used the same connection setup. This does not establish that either board is defective.

Espressif documents `RTCWDT_RTC_RESET` as an RTC watchdog reset; the watchdog can operate during startup and help recover from a lockup, including one associated with unstable power. The message alone does not identify the cause. See the [ESP-IDF fatal errors guide](https://docs.espressif.com/projects/esp-idf/en/release-v5.2/esp32/api-guides/fatal-errors.html#rtc-watchdog-timeout) and [watchdog overview](https://docs.espressif.com/projects/esp-techpedia/en/latest/esp-friends/advanced-development/system/watchdog.html).

## To confirm

- Photograph the board and record the markings on its module and PCB.
- Identify the exact board profile, processor, memory, connectors, and power requirements.
- Determine whether the firmware is factory-installed or was previously changed.
- Investigate the repeated resets before using the board for robot control.
