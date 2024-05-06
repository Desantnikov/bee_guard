import time
from pymavlink import mavutil

from typing import List



class Mavlink:
    # https://www.ardusub.com/developers/pymavlink.html#autopilot-eg-pixhawk-connected-to-the-computer-via-serial
    def __init__(self, serial_port: str, baudrate: int = 57600, default_exclude_fields: List[str] = None, reset_input_buffer: bool = True):
        self.connection = mavutil.mavlink_connection(serial_port, baud=baudrate)
        self.connection.wait_heartbeat(blocking=True, timeout=15)
        print(f'Connected to mavlink')

        self.default_exclude_fields = default_exclude_fields
        self.RESET_INPUT_BUFFER = reset_input_buffer

    def receive_packet_dict(self, packet_type: str = None, blocking: bool = True, exclude_fields: List[str] = None):
        packet = self.connection.recv_match(type=packet_type, blocking=blocking)

        # print(f'Mav count: {self.connection.mav_count}. Packet utime: {packet.time_usec}')

        packet_dict = packet.to_dict()

        # print(f'Received packet\r\nutime: {packet.time_usec}; seq: {packet._header.seq}')

        if exclude_fields is not None:
            for field_name in exclude_fields:
                if field_name in packet_dict.keys():
                    packet_dict.pop(field_name)

        return packet_dict

    def receive_multiple_packet_dicts(self, packet_type: str = None, packets_amount: int = 0):
        start_time = time.time()

        if self.RESET_INPUT_BUFFER:
            print(f'\r\nResetting input buffer')
            self.connection.port.reset_input_buffer()

        packet_dicts_batch = []

        for packets_counter in range(1, packets_amount+1):
            packet_dicts_batch.append(
                self.receive_packet_dict(
                    packet_type=packet_type,
                    exclude_fields=self.default_exclude_fields,
                ),
            )

            if packets_counter % 10 == 0:
                print(f'Received {packets_counter}th packet')
            # print(f'Packet:\r\n{packet_dicts_batch[-1]}')

        total_time = time.time() - start_time
        print(f'Total received packets: {len(packet_dicts_batch)}. Time: {total_time}')

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
        self.connection.mav.command_long_send(
            self.connection.target_system, self.connection.target_component,
            mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0,
            message_id,  # The MAVLink message ID
            1e6 / frequency_hz,
            # The interval between two messages in microseconds. Set to -1 to disable and 0 to request default rate.
            0, 0, 0, 0,  # Unused parameters
            0,
            # Target address of message stream (if message has target address fields). 0: Flight-stack default (recommended), 1: address of requestor, 2: broadcast.
        )