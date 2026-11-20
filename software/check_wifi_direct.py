"""Check 20 TCP round trips over a temporary ESP32 access point on Windows."""

import argparse
import ctypes
from ctypes import wintypes
from pathlib import Path
import re
import secrets
import socket
import subprocess
import sys
import time
import uuid

import serial


SSID = "RoboZakBench-9B62"
TARGET = ("192.168.47.1", 38473)
BOARD = "esp32:esp32:esp32"


class ConnectionParameters(ctypes.Structure):
    _fields_ = [
        ("mode", ctypes.c_int), ("profile", wintypes.LPCWSTR),
        ("ssid", ctypes.c_void_p), ("bssid_list", ctypes.c_void_p),
        ("bss_type", ctypes.c_int), ("flags", wintypes.DWORD),
    ]


def interface():
    output = subprocess.check_output(["netsh", "wlan", "show", "interfaces"],
                                     text=True, errors="replace")
    names = re.findall(r"^\s*(?:Name|Nome)\s*:\s*(.+)$", output, re.MULTILINE)
    guids = re.findall(r"^\s*GUID\s*:\s*([0-9a-f-]{36})", output, re.I | re.MULTILINE)
    ssids = re.findall(r"^\s*SSID\s*:\s*(.+)$", output, re.MULTILINE)
    profiles = re.findall(r"^\s*(?:Profile|Profilo)\s*:\s*(.+)$", output, re.MULTILINE)
    if len(guids) != 1 or len(names) != 1:
        raise RuntimeError("Expected one Windows Wi-Fi interface.")
    return (names[0].strip(), uuid.UUID(guids[0]), ssids[0].strip() if ssids else None,
            profiles[0].strip() if profiles else None)


def connect_temporary(guid, key):
    wlan = ctypes.WinDLL("wlanapi")
    wlan.WlanOpenHandle.argtypes = [
        wintypes.DWORD, ctypes.c_void_p, ctypes.POINTER(wintypes.DWORD),
        ctypes.POINTER(wintypes.HANDLE),
    ]
    wlan.WlanConnect.argtypes = [
        wintypes.HANDLE, ctypes.c_void_p, ctypes.POINTER(ConnectionParameters),
        ctypes.c_void_p,
    ]
    wlan.WlanCloseHandle.argtypes = [wintypes.HANDLE, ctypes.c_void_p]
    handle = wintypes.HANDLE()
    version = wintypes.DWORD()
    result = wlan.WlanOpenHandle(2, None, ctypes.byref(version), ctypes.byref(handle))
    if result:
        raise RuntimeError(f"WlanOpenHandle returned {result}.")
    try:
        profile = f"""<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
        <name>{SSID}</name><SSIDConfig><SSID><name>{SSID}</name></SSID></SSIDConfig>
        <connectionType>ESS</connectionType><connectionMode>manual</connectionMode>
        <MSM><security><authEncryption><authentication>WPA2PSK</authentication>
        <encryption>AES</encryption><useOneX>false</useOneX></authEncryption>
        <sharedKey><keyType>passPhrase</keyType><protected>false</protected>
        <keyMaterial>{key.decode("ascii")}</keyMaterial></sharedKey></security></MSM>
        </WLANProfile>"""
        parameters = ConnectionParameters(1, profile, None, None, 1, 0)
        interface_id = (ctypes.c_ubyte * 16).from_buffer_copy(guid.bytes_le)
        result = wlan.WlanConnect(handle, interface_id, ctypes.byref(parameters), None)
        if result:
            raise RuntimeError(f"WlanConnect returned {result}.")
        return wlan, handle
    except BaseException:
        wlan.WlanCloseHandle(handle, None)
        raise


def wait_ap(port, key):
    port.write(key)
    deadline = time.monotonic() + 12
    while time.monotonic() < deadline:
        line = port.readline().strip()
        if line == b"AP_READY":
            print("ESP32 protected access point started.", flush=True)
            return
        if line == b"AP_FAILED":
            break
    raise RuntimeError("The ESP32 did not start the access point.")


def tcp_test():
    deadline = time.monotonic() + 45
    client = None
    while time.monotonic() < deadline:
        if interface()[2] == SSID:
            try:
                client = socket.create_connection(TARGET, timeout=1)
                break
            except OSError:
                pass
        time.sleep(1)
    if client is None:
        raise RuntimeError(f"TCP server unreachable. Windows SSID is {interface()[2]!r}.")
    with client, client.makefile("rb") as response:
        durations = []
        for identifier in range(1, 21):
            started = time.monotonic()
            client.sendall(f"PING {identifier}\n".encode("ascii"))
            reply = response.readline(64).strip()
            elapsed = time.monotonic() - started
            if reply != f"PONG {identifier}".encode("ascii") or elapsed > 1:
                raise RuntimeError(f"TCP reply {identifier} failed validation.")
            durations.append(elapsed)
        print(f"TCP PASS: 20 matching replies, slowest {max(durations)*1000:.1f} ms.", flush=True)


def restore_wifi(name, previous, profile):
    if interface()[2] != previous:
        subprocess.run(["netsh", "wlan", "connect", f"name={profile}", f"ssid={previous}",
                        f"interface={name}"],
                       check=True, stdout=subprocess.DEVNULL)
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        if interface()[2] == previous:
            print("Windows original Wi-Fi restored.", flush=True)
            return
        time.sleep(1)
    raise RuntimeError("Windows did not return to its original Wi-Fi network.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("port", help="ESP32 serial port, for example COM3")
    parser.add_argument("--preflight", action="store_true", help="Check the current Wi-Fi profile only")
    args = parser.parse_args()
    if sys.platform != "win32":
        parser.error("this check requires Windows")
    name, guid, previous, profile = interface()
    if not previous or previous == SSID or not profile:
        raise RuntimeError("Connect to a saved Wi-Fi profile before starting the test.")
    if args.preflight:
        print("Windows interface and original Wi-Fi verified.")
        return
    firmware = Path(__file__).resolve().parents[1] / "firmware"
    diagnostic = str(firmware / "robozak_direct_ap")
    baseline = str(firmware / "esp32_boot_stability")
    for sketch in (diagnostic, baseline):
        subprocess.run(["arduino-cli", "compile", "--fqbn", BOARD, sketch], check=True)

    upload = ["arduino-cli", "upload", "--port", args.port, "--fqbn",
              f"{BOARD}:UploadSpeed=115200"]
    wlan_connection = None
    try:
        print("Uploading the direct Wi-Fi diagnostic.", flush=True)
        subprocess.run(upload + [diagnostic], check=True, stdout=subprocess.DEVNULL)
        with serial.Serial(baudrate=115200, timeout=0.25, write_timeout=2) as port:
            port.dtr = False
            port.rts = False
            port.port = args.port
            port.open()
            time.sleep(2)
            port.reset_input_buffer()
            key = secrets.token_hex(8).encode("ascii")
            wait_ap(port, key)
            wlan_connection = connect_temporary(guid, key)
            del key
            tcp_test()
    finally:
        try:
            if wlan_connection:
                wlan, handle = wlan_connection
                wlan.WlanCloseHandle(handle, None)
                restore_wifi(name, previous, profile)
        finally:
            subprocess.run(upload + [baseline], check=True,
                           stdout=subprocess.DEVNULL)
            usb_check = Path(__file__).with_name("check_serial_roundtrip.py").resolve()
            subprocess.run([sys.executable, "-B", str(usb_check), args.port],
                           check=True, stdout=subprocess.DEVNULL)
            print("USB firmware restored and 20 round trips verified.", flush=True)


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        raise SystemExit(f"FAIL: {error}") from None
