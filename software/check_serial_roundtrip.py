"""Verify command and response over the ESP32 USB serial connection."""

import argparse
import sys
import time

import serial


def exchange(connection, command, expected):
    started = time.monotonic()
    connection.write(command + b"\n")
    while (remaining := 1.0 - (time.monotonic() - started)) > 0:
        connection.timeout = remaining
        line = connection.readline()
        elapsed = time.monotonic() - started
        if not line.endswith(b"\n") or elapsed > 1.0:
            break
        reply = line.rstrip(b"\r\n")
        if reply == expected:
            print(f"{command.decode()} -> {reply.decode()} ({elapsed * 1000:.1f} ms)")
            return elapsed
        if reply == b"ERR" or reply.startswith(b"PONG "):
            raise RuntimeError(f"{command!r}: expected {expected!r}, received {reply!r}")
    raise RuntimeError(f"{command!r}: no {expected!r} within one second")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("port", help="Serial port, for example COM3")
    args = parser.parse_args()

    try:
        with serial.Serial(baudrate=115200, write_timeout=1) as connection:
            connection.dtr = False
            connection.rts = False
            connection.port = args.port
            connection.open()
            time.sleep(2)
            connection.reset_input_buffer()
            latencies = []
            for request_id in range(1, 21):
                identifier = str(request_id).encode("ascii")
                latencies.append(exchange(connection, b"PING " + identifier, b"PONG " + identifier))
            exchange(connection, b"UNKNOWN", b"ERR")
    except (serial.SerialException, RuntimeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print(f"PASS: {len(latencies)} matching replies, slowest {max(latencies) * 1000:.1f} ms, and one ERR")
    return 0


if __name__ == "__main__":
    sys.exit(main())
