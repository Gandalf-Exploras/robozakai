"""Run repeated RoboZak LAN checks with one in-memory credential lookup."""

import argparse
import ipaddress
from getpass import getpass
from pathlib import Path
import socket
import subprocess
import sys
import time

import serial


def wifi_key(reference):
    if reference is None:
        if not sys.stdin.isatty():
            raise RuntimeError("Use an interactive terminal or an op:// reference.")
        return getpass("Wi-Fi passphrase: ").encode("utf-8")
    result = subprocess.run(
        ["op", "read", reference],
        capture_output=True, timeout=100,
    )
    if result.returncode:
        raise RuntimeError("1Password could not read the secret reference.")
    return result.stdout.rstrip(b"\r\n")


def round_trip(port, packet):
    # Reset to interrupt any previous test and release the listening socket.
    port.rts = True
    time.sleep(0.15)
    port.reset_input_buffer()
    port.rts = False
    time.sleep(2)
    port.write(packet)
    deadline = time.monotonic() + 42
    passed = False
    while time.monotonic() < deadline:
        reply = port.readline().strip()
        if reply.startswith(b"READY "):
            address = str(ipaddress.IPv4Address(reply.split()[1].decode("ascii")))
            print("Wi-Fi association and DHCP: PASS", flush=True)
            try:
                with socket.create_connection((address, 38473), timeout=8) as client:
                    client.sendall(b"ROBOZAK_LAN_PING\n")
                    with client.makefile("rb") as response:
                        passed = response.readline(64) == b"ROBOZAK_LAN_PONG\n"
            except OSError:
                pass
            print("PC to ESP32 TCP: " + ("PASS" if passed else "no expected reply"), flush=True)
        elif reply in (b"GATEWAY_TCP_OK", b"GATEWAY_TCP_NO_REPLY"):
            print("ESP32 to gateway TCP: " +
                  ("PASS" if reply == b"GATEWAY_TCP_OK" else "no reply on test ports"), flush=True)
            return passed
        elif reply in (b"CONNECT_FAILED", b"INVALID_INPUT"):
            print("ESP32 could not connect to the network.", flush=True)
            return False
    print("No complete test result received.", flush=True)
    return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("port")
    parser.add_argument("ssid")
    parser.add_argument("--count", type=int, default=3)
    parser.add_argument("--secret-reference", help="Optional 1Password op:// reference")
    args = parser.parse_args()
    if not 1 <= args.count <= 20:
        parser.error("--count must be between 1 and 20")

    ssid = args.ssid.encode("utf-8")
    if not 1 <= len(ssid) <= 32 or b"\0" in ssid:
        parser.error("SSID must contain 1 to 32 UTF-8 bytes without NUL")
    if args.secret_reference and not args.secret_reference.startswith("op://"):
        parser.error("--secret-reference must be an op:// reference")
    firmware = Path(__file__).resolve().parents[1] / "firmware"
    diagnostic = str(firmware / "robozak_wifi_lan")
    baseline = str(firmware / "esp32_boot_stability")
    profile = "esp32:esp32:esp32"
    for sketch in (diagnostic, baseline):
        subprocess.run(["arduino-cli", "compile", "--fqbn", profile, sketch], check=True)

    key = wifi_key(args.secret_reference)
    if not 8 <= len(key) <= 64 or b"\n" in key or b"\0" in key:
        parser.error("expected a Wi-Fi passphrase of 8 to 64 bytes")
    packet = bytearray((len(ssid), len(key)))
    packet.extend(ssid)
    packet.extend(key)
    del key
    upload = ["arduino-cli", "upload", "--port", args.port, "--fqbn",
              f"{profile}:UploadSpeed=115200"]
    try:
        subprocess.run(upload + [diagnostic], check=True, stdout=subprocess.DEVNULL)
        with serial.Serial(baudrate=115200, timeout=0.3, write_timeout=2) as port:
            port.dtr = False
            port.rts = False
            port.port = args.port
            port.open()
            results = [round_trip(port, packet) for _ in range(args.count)]
        return 0 if all(results) else 1
    finally:
        packet[:] = bytes(len(packet))
        subprocess.run(upload + [baseline], check=True, stdout=subprocess.DEVNULL)
        usb_check = Path(__file__).with_name("check_serial_roundtrip.py").resolve()
        subprocess.run([sys.executable, "-B", str(usb_check), args.port],
                       check=True, stdout=subprocess.DEVNULL)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.SubprocessError, ValueError) as error:
        print(f"Session failed: {error}", file=sys.stderr)
        raise SystemExit(2)
