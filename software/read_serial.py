"""Read serial output for a limited time without sending data."""

import argparse
import sys
import time

import serial


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("port", help="Serial port, for example COM3")
    parser.add_argument("--baud", type=int, default=115200, help="Baud rate (default: 115200)")
    parser.add_argument("--seconds", type=float, default=10, help="Read duration (default: 10 seconds)")
    args = parser.parse_args()
    if args.baud <= 0 or args.seconds <= 0:
        parser.error("baud and seconds must be positive")

    try:
        connection = serial.Serial(port=None, baudrate=args.baud, timeout=0.2)
        connection.dtr = False
        connection.rts = False
        connection.port = args.port
        connection.open()
        with connection:
            print(f"Listening on {args.port} at {args.baud} baud for {args.seconds:g} seconds...")
            deadline = time.monotonic() + args.seconds
            received = False
            while time.monotonic() < deadline:
                data = connection.read(connection.in_waiting or 1)
                if data:
                    received = True
                    print(data.decode("utf-8", errors="replace"), end="", flush=True)
            print("\nDone." if received else "No data received.")
    except serial.SerialException as error:
        print(f"Serial error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
