import time
from pymavlink import mavutil
from example_packets_dataframe import EXAMPLE_DATAFRAME_INITIAL, EXAMPLE_DATAFRAME_ALARM
from mavlink import Mavlink
import threading
from analyzator import Analyzator
from audio import Audio
import pandas as pd


MAVLINK_SERIAL_PORT = 'COM11'
MAVLINK_SERIAL_BAUDRATE = 57600
PACKETS_TO_COLLECT_WITHOUT_AUDIO = 11
PACKETS_TO_COLLECT_WITH_AUDIO = 5
USE_EXAMPLE_PACKETS = True
RESET_INPUT_BUFFER = True
PACKET_TYPE_TO_ANALYZE = 'RAW_IMU'
PACKET_TYPE_UPDATE_RATE_TO_REQUEST = 5

INITIAL_AUDIO_FREQUENCY = 26900
AUDIO_FREQUENCY_LIMIT = 27400
AUDIO_FREQUENCY_STEP = 50
AUDIO_DURATION = 10000


pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.float_format', lambda x: '%.2f' % x)


if USE_EXAMPLE_PACKETS:
    no_audio_packets = EXAMPLE_DATAFRAME_INITIAL
else:
    mavlink = Mavlink(
        serial_port=MAVLINK_SERIAL_PORT,
        baudrate=MAVLINK_SERIAL_BAUDRATE,
        # to exclude when packet converted to dict
        default_exclude_fields=['mavpackettype', 'time_usec', 'id', 'xmag', 'ymag', 'zmag'],
        reset_input_buffer=RESET_INPUT_BUFFER,
    )
    mavlink.request_message_interval(message_id=mavutil.mavlink.MAVLINK_MSG_ID_RAW_IMU, frequency_hz=PACKET_TYPE_UPDATE_RATE_TO_REQUEST)
    
    no_audio_packets = mavlink.receive_multiple_packet_dicts(packet_type=PACKET_TYPE_TO_ANALYZE, packets_amount=PACKETS_TO_COLLECT_WITHOUT_AUDIO)

no_sound_packets_analyzator = Analyzator(packets=no_audio_packets)
no_sound_packets_analyzator.describe_packets()


def enable_audio_receive_packets_and_check(audio_frequency: int) -> pd.DataFrame:
    audio_duration = int((PACKETS_TO_COLLECT_WITH_AUDIO / PACKET_TYPE_UPDATE_RATE_TO_REQUEST) + 2) * 1000  # TODO: move to Audio class

    audio_thread = threading.Thread(target=Audio.play_sound, kwargs={'frequency': audio_frequency, 'duration': audio_duration})
    audio_thread.start()

    # time.sleep(1)  # audio does not play instantly
    if USE_EXAMPLE_PACKETS:
        audio_packets = EXAMPLE_DATAFRAME_ALARM
    else:

        audio_packets = mavlink.receive_multiple_packet_dicts(packet_type=PACKET_TYPE_TO_ANALYZE, packets_amount=PACKETS_TO_COLLECT_WITH_AUDIO)

    rows_with_anomalies = no_sound_packets_analyzator.check_anomaly(input_df=pd.DataFrame(audio_packets))
    audio_thread.join()
    return rows_with_anomalies


results = {}

current_audio_frequency = INITIAL_AUDIO_FREQUENCY
while current_audio_frequency <= AUDIO_FREQUENCY_LIMIT:
    anomalies = enable_audio_receive_packets_and_check(audio_frequency=current_audio_frequency)

    if not anomalies.empty:
        print(f'Found {len(anomalies)} anomalies for frequency: {current_audio_frequency}\r\n')
        results[current_audio_frequency] = anomalies

    current_audio_frequency += AUDIO_FREQUENCY_STEP

print(f'\r\n'
      f'Anomalies:\r\n'
      f'----------------------------------------------------------\r\n')

for frequency, anomalies_df in results.items():
    print(f'Frequency {frequency} anomalies:\r\n'
          f'{anomalies_df}\r\n')

print('SSSSSS')



