from pymavlink import mavutil

from typing import List


class Mavlink:
    # https://www.ardusub.com/developers/pymavlink.html#autopilot-eg-pixhawk-connected-to-the-computer-via-serial
    def __init__(self, serial_port: str, baudrate: int = 57600, default_exclude_fields: List[str] = None):
        self.connection = mavutil.mavlink_connection(serial_port, baud=baudrate)
        self.connection.wait_heartbeat(blocking=True, timeout=15)
        print(f'Connected to mavlink')

        self.default_exclude_fields = default_exclude_fields

    def receive_packet_dict(self, packet_type: str = None, blocking: bool = True, exclude_fields: List[str] = None):
        packet_dict = self.connection.recv_match(type=packet_type, blocking=blocking).to_dict()

        if exclude_fields is not None:
            for field_name in exclude_fields:
                packet_dict.pop(field_name)

        return packet_dict

    def receive_multiple_packet_dicts(self, packet_type: str = None, packets_amount: int = 0):
        packet_dicts_batch = []

        for packets_counter in range(packets_amount):
            packet_dicts_batch.append(
                self.receive_packet_dict(
                    packet_type=packet_type,
                    exclude_fields=self.default_exclude_fields,
                ),
            )

            # if packets_counter % 10 == 0:
            print(f'Received {packets_counter} packets')

        return packet_dicts_batch
