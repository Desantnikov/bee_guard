import sys

if sys.version_info.minor >= 11:
    from enum import StrEnum
else:
    from strenum import StrEnum


class PacketTypes(StrEnum):
    RAW_IMU = "RAW_IMU"
    MAVLINK_MSG_ID_HIGHRES_IMU = "MAVLINK_MSG_ID_HIGHRES_IMU"  # TODO: Check if real packet type
