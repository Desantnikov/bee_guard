import contextlib
import time
from typing import List

import pandas as pd
from pymavlink import mavutil

import datetime
from enums import MavlinkPacketTypes
from classes.logger_mixin import LoggerMixin
from constants import LOGS_FOLDER, MOCK_DATA_FOLDER


class DroneController(LoggerMixin):
    """
    https://www.ardusub.com/developers/pymavlink.html#autopilot-eg-pixhawk-connected-to-the-computer-via-serial
    """

    def __init__(
        self,
        serial_port: str,
        baudrate: int = 57600,
        default_exclude_fields: List[str] = None,
        do_reset_input_buffer: bool = True,
    ):
        super().__init__(serial_port, baudrate, default_exclude_fields, do_reset_input_buffer)

        self.serial_port = serial_port
        self.baudrate = baudrate

        self.connection = mavutil.mavlink_connection(device=self.serial_port, baud=self.baudrate, zero_time_base=True)
        self.connection.wait_heartbeat(blocking=True, timeout=15)
        self.logger.info("Connected to drone_controller")

        self.set_system_time()

        self.default_exclude_fields = default_exclude_fields
        self.do_reset_input_buffer = do_reset_input_buffer
        self.connection.setup_logfile(f"{LOGS_FOLDER}/mavlink_logs.log")

    def set_system_time(self):
        unix_time = int(time.time())
        time_usec = unix_time * 1000000  # convert to microseconds
        self.connection.mav.system_time_send(time_usec, unix_time)  # set system time

    def receive_packet_dict(self, packet_type: str = None, blocking: bool = True, exclude_fields: List[str] = None):
        packet = self.connection.recv_match(type=packet_type, blocking=blocking, timeout=30)

        # self.logger.info(f'Mav count: {cls.connection.mav_count}. Packet utime: {packet.time_usec}')

        packet_dict = packet.to_dict()

        # self.logger.info(f'Received packet\r\nutime: {packet.time_usec}; seq: {packet._header.seq}')

        if exclude_fields is not None:
            for field_name in exclude_fields:
                if field_name in packet_dict:
                    packet_dict.pop(field_name)

        return packet_dict

    def receive_multiple_packet_dicts(
        self, packet_type: str = None, packets_read_amount: int = 1, read_time: int = None
    ):
        """

        :param packet_type:  read only this packet type, ignore all other packets
        :param packets_read_amount: how many packets to read
        :param read_time: force stop reading after X seconds
        :return:
        """

        start_time = time.time()

        if self.do_reset_input_buffer:
            self.logger.info("Resetting input buffer")
            self.connection.port.reset_input_buffer()

        packet_dicts_batch = []

        for packets_counter in range(1, packets_read_amount + 1):
            packet_dicts_batch.append(
                self.receive_packet_dict(
                    packet_type=packet_type,
                    exclude_fields=self.default_exclude_fields,
                ),
            )
            if read_time is not None:
                time_elapsed = time.time() - start_time
                if time_elapsed > read_time:
                    self.logger.info(f"Time elapsed {time_elapsed} > read_time {read_time}, stop reading")
                    break

            if packets_counter % 10 == 0:
                self.logger.info(f"Received {packets_counter}th packet")
            # self.logger.info(f'Packet:\r\n{packet_dicts_batch[-1]}')

        total_time = time.time() - start_time
        self.logger.info(f"Total received packets: {len(packet_dicts_batch)}. Time: {total_time}")

        return packet_dicts_batch

    def request_message_interval(self, message_id: int, frequency_hz: float):
        """
        Request MAVLink message in a desired frequency,
        documentation for SET_MESSAGE_INTERVAL:
            https://mavlink.io/en/messages/common.html#MAV_CMD_SET_MESSAGE_INTERVAL

        Args:
            message_id (int): MAVLink message ID
            frequency_hz (float): Desired frequency in Hz
        """
        self.logger.info(f'Requesting message "{mavutil.mavlink.mavlink_map[message_id].msgname}" '
                         f'with id "{message_id}" '
                         f'update interval {frequency_hz}hz')

        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
            0,
            message_id,  # The MAVLink message ID
            1e6 / frequency_hz,
            # The interval between two messages in microseconds. Set to -1 to disable and 0 to request default rate.
            0,
            0,
            0,
            0,  # Unused parameters
            0,  # Target address of message stream (if message has target address fields).
            # 0: Flight-stack default (recommended), 1: address of requestor, 2: broadcast.
        )

    def request_system_time(self):
        self.logger.info("Get SYSTEM_TIME from drone")
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE,
            0,  # confirmation
            mavutil.mavlink.MAVLINK_MSG_ID_SYSTEM_TIME,  # message id to request
            0, 0, 0, 0, 0, 0  # unused parameters
        )
        system_time_packet = self.receive_packet_dict(packet_type=MavlinkPacketTypes.SYSTEM_TIME, blocking=True)
        self.logger.debug(f"Raw SYSTEM_TIME packet : {system_time_packet}")
        self.logger.info(f"System time: {datetime.datetime.fromtimestamp(int(system_time_packet['time_unix_usec'] / 1000000)).strftime("%Y-%m-%d %H-%M-%S")}")
        self.logger.info(f"Time from boot: {datetime.datetime.fromtimestamp(int(system_time_packet['time_boot_ms'] / 1000)).strftime("%Hhr %Mmin %Ssec")}")

    def clear_input_buffer(self):
        received = True
        while received:
            received = self.connection.recv_msg()

        self.logger.info("Input buffer cleared")


class MockedDroneController(DroneController):
    def __init__(self, *args, **kwargs):
        with contextlib.suppress(Exception):
            super().__init__(*args, **kwargs)  # to initialize logger

        reference_packet_dicts = self._read_sample_data("100_RAW_IMU_reference_packets.csv").to_dict()
        influenced_packet_dicts = self._read_sample_data("10_RAW_IMU_anomaly_packets.csv").to_dict()

        # pop one by one when `receive_multiple_packet_dicts` executed
        self.packets_batches_queue = [reference_packet_dicts] + [influenced_packet_dicts for _ in range(50)]

    @staticmethod
    def _read_sample_data(filename):
        return pd.read_csv(f"{MOCK_DATA_FOLDER}/{filename}")

    def receive_multiple_packet_dicts(self, *args, **kwargs):
        self.logger.info("Return fake packet dicts")

        return self.packets_batches_queue.pop(0)

    def request_message_interval(self, *args, **kwargs):
        pass

    def clear_input_buffer(self):
        pass


if __name__ == "__main__":
    drone_controller = DroneController(
        serial_port='COM9',
        baudrate=921600,
        # default_exclude_fields=["mavpackettype", "id", "xmag", "ymag", "zmag"],  # TODO: Move to constants?
        do_reset_input_buffer=True,
    )
    from enums import MavlinkPacketTypes
    import pprint


    # # set RAW_IMU message update frequency
    # drone_controller.request_message_interval(
    #     message_id=mavutil.mavlink.MAVLINK_MSG_ID_SCALED_IMU,
    #     frequency_hz=1,
    # )
    # # set RAW_IMU message update frequency
    # drone_controller.request_message_interval(
    #     message_id=mavutil.mavlink.MAVLINK_MSG_ID_SCALED_IMU2,
    #     frequency_hz=1,
    # )
    # set RAW_IMU message update frequency
    drone_controller.request_message_interval(
        message_id=mavutil.mavlink.MAVLINK_MSG_ID_HIGHRES_IMU,
        frequency_hz=1,
    )



    while True:
        print('Wait for packet')
        # packet = drone_controller.receive_multiple_packet_dicts(packet_type=MavlinkPacketTypes.RAW_IMU, packets_read_amount=20)

        packet_imu_1 = drone_controller.receive_packet_dict(
                    # packet_type=MavlinkPacketTypes.HIGHRES_IMU,
                    # exclude_fields=["mavpackettype", "id", "xmag", "ymag", "zmag"],
                )
        pprint.pprint(packet_imu_1)
        # print(packet)