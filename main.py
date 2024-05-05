from pymavlink import mavutil
import time
from typing import List
import pprint
from example_packets_dataframe import EXAMPLE_DATAFRAME
from mavlink import Mavlink
import threading
from analyzator import Analyzator
from audio import Audio
import pandas as pd

MAVLINK_SERIAL_PORT = 'COM11'
MAVLINK_SERIAL_BAUDRATE = 57600
PACKETS_TO_COLLECT_WITHOUT_AUDIO = 15
USE_EXAMPLE_PACKETS = True


pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.float_format', lambda x: '%.2f' % x)


mavlink = Mavlink(
    serial_port=MAVLINK_SERIAL_PORT,
    baudrate=MAVLINK_SERIAL_BAUDRATE,
    # to exclude when packet converted to dict
    default_exclude_fields=['mavpackettype', 'time_usec', 'id'],
)

if USE_EXAMPLE_PACKETS:
    no_audio_packets = EXAMPLE_DATAFRAME
else:
    no_audio_packets = mavlink.receive_multiple_packet_dicts(packet_type="RAW_IMU", packets_amount=PACKETS_TO_COLLECT_WITHOUT_AUDIO)


print(f'Made {PACKETS_TO_COLLECT_WITHOUT_AUDIO} iterations, analysis')

no_sound_packets_analyzator = Analyzator(packets=no_audio_packets)
no_sound_packets_analyzator.describe_packets()


print('WITH SOUND')



audio_thread = threading.Thread(target=Audio.play_sound, kwargs={'frequency': 28000, 'duration': 10000})
audio_thread.start()


audio_packets = mavlink.receive_multiple_packet_dicts(packet_type="RAW_IMU", packets_amount=10)

rows_with_anomalies = no_sound_packets_analyzator.check_anomaly(input_df=pd.DataFrame(audio_packets))

print(f'Anomalies:\r\n\r\n{rows_with_anomalies}')
print('a')
