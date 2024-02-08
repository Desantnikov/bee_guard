from pymavlink import mavutil
import time

# https://www.ardusub.com/developers/pymavlink.html#autopilot-eg-pixhawk-connected-to-the-computer-via-serial

master = mavutil.mavlink_connection("COM7", baud=57600)

print('MASTER')

# master.wait_heartbeat()

# Get some information !

prev_packets = {}
while True:
    try:
        new_packet = master.recv_match().to_dict()

        new_packet.pop("time_boot_ms", None)
        new_packet.pop("yaw", None)

        packet_type = new_packet['mavpackettype']

        previous_packet = prev_packets.get(packet_type)
        if previous_packet == new_packet:
            print("SAME")
            continue

        else:
            print(f'\r\nPREVIOUS: {previous_packet}\r\nNEW: {new_packet}')
            prev_packets[packet_type] = new_packet

        # print(new_packet)

    except Exception as e:
        print(f'\r\nEXCEPTION: {e}\r\n')

    time.sleep(0.1)
