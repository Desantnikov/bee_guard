import sys

if sys.version_info.minor >= 11:
    from enum import StrEnum
else:
    from strenum import StrEnum


class MavlinkPacketTypes(StrEnum):
    RAW_IMU = "RAW_IMU"
    MAVLINK_MSG_ID_HIGHRES_IMU = "MAVLINK_MSG_ID_HIGHRES_IMU"  # TODO: Check if real packet type


class PositionFieldNames(StrEnum):
    @classmethod
    def members(cls):
        return list(cls.__members__.items())

    X_ACC = "xacc"
    Y_ACC = "yacc"
    Z_ACC = "zacc"

    X_GYRO = "xgyro"
    Y_GYRO = "ygyro"
    Z_GYRO = "zgyro"

    TEMPERATURE = "temperature"
