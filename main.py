from operator import contains
from typing import Container
from crsf_parser import CRSFParser, PacketValidationStatus
from serial import Serial

from crsf_parser.payloads import PacketsTypes
from crsf_parser.handling import crsf_build_frame


def print_frame(frame: Container, status: PacketValidationStatus) -> None:
    print(
        f"""PRINT FRAME
    {status}
    {frame}
    """
    )


BAUDRATES = [19200, 57600, 76800, 115200  ]

crsf_parser = CRSFParser(print_frame)
n = 10
v = 1

# EofChar = 0x0
# ErrorChar = 0x0
# BreakChar = 0x0
# EventChar = 0x0
# XonChar = 0x11
# XoffChar = 0x13

# 57600
# actual: 77; type: 4
# actual: 3; type: 42

with Serial("COM7", 57600) as ser:
    input = bytearray()
    while True:
        if n == 0:
            n = 10
            frame = crsf_build_frame(
                PacketsTypes.BATTERY_SENSOR,
                {"voltage": v, "current": 1, "capacity": 100, "remaining": 100},
            )
            v += 1
            ser.write(frame)
        n = n - 1
        values = ser.read(100)

        input.extend(values)
        crsf_parser.parse_stream(input)

        print(f'Pasers data: {crsf_parser.get_stats()};\r\n')
        # print(f'VALUES: {values};')