"""List Windows serial ports without opening or communicating with them."""

import sys


def list_ports():
    if sys.platform != "win32":
        raise RuntimeError("This first version supports Windows only.")

    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DEVICEMAP\SERIALCOMM") as key:
            ports = []
            for index in range(winreg.QueryInfoKey(key)[1]):
                _, port, _ = winreg.EnumValue(key, index)
                ports.append(port)
            return sorted(set(ports))
    except FileNotFoundError:
        return []


def main():
    try:
        ports = list_ports()
    except (OSError, RuntimeError) as error:
        print(f"Could not list serial ports: {error}", file=sys.stderr)
        return 1

    if not ports:
        print("No serial ports found.")
    else:
        print("Available serial ports:")
        for port in ports:
            print(f"  {port}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
