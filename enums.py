import sys

if sys.version_info.minor >= 11:
    from enum import StrEnum
else:
    from strenum import StrEnum


class MavlinkPacketTypes(StrEnum):
    RAW_IMU = "RAW_IMU"  # raw data from default position sensor (first)
    SCALED_IMU = "SCALED_IMU"  # raw data from first sensor
    SCALED_IMU2 = "SCALED_IMU2"  # raw data from second sensor

    SYSTEM_TIME = "SYSTEM_TIME"


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
