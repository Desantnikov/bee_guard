from enum import StrEnum


class PacketTypes(StrEnum):
    RAW_IMU = "RAW_IMU"
    MAVLINK_MSG_ID_HIGHRES_IMU = "MAVLINK_MSG_ID_HIGHRES_IMU"  # TODO: Check if real packet type
