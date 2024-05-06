import time

from pymavlink import mavutil

import constants
from constants import MAVLINK_SERIAL_PORT, MAVLINK_SERIAL_BAUDRATE, PACKETS_TO_COLLECT_WITHOUT_AUDIO, \
    PACKETS_TO_COLLECT_WITH_AUDIO, RESET_INPUT_BUFFER, PACKET_TYPE_TO_ANALYZE, PACKET_TYPE_UPDATE_RATE_TO_REQUEST, \
    INITIAL_AUDIO_FREQUENCY, AUDIO_FREQUENCY_LIMIT, AUDIO_FREQUENCY_STEP, USE_SAMPLE_PACKETS
from mavlink_wrapper import MavlinkWrapper, FakeMavlinkWrapper
from analyzer import Analyzer
from sound_controller import SoundController
import pandas as pd


# TODO: Move to config
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.float_format', lambda x: '%.2f' % x)

"""
Flow:
0. Select real or fake mavlink wrapper
1. Collect reference packets (sound disabled)
2. In thread - start sound with specific frequency
3. Read packets influenced (probably) by the audio playback
4. Wait until playback thread finished
5. Increase current frequency
5. GOTO [2]
"""




mavlink_wrapper_cls = MavlinkWrapper
if USE_SAMPLE_PACKETS:  # use fake wrapper returning sample data if enabled
    mavlink_wrapper_cls = FakeMavlinkWrapper


mavlink_wrapper = mavlink_wrapper_cls(
    serial_port=MAVLINK_SERIAL_PORT,
    baudrate=MAVLINK_SERIAL_BAUDRATE,
    default_exclude_fields=['mavpackettype', 'id', 'xmag', 'ymag', 'zmag'],  # TODO: Move to constants?
    do_reset_input_buffer=RESET_INPUT_BUFFER,
)
mavlink_wrapper.request_message_interval(  # set RAW_IMU message update frequency
    message_id=mavutil.mavlink.MAVLINK_MSG_ID_RAW_IMU,
    frequency_hz=PACKET_TYPE_UPDATE_RATE_TO_REQUEST,
)
reference_packet_dicts = mavlink_wrapper.receive_multiple_packet_dicts(  # read first X packets to use as a reference
    packet_type=PACKET_TYPE_TO_ANALYZE,
    packets_read_amount=PACKETS_TO_COLLECT_WITHOUT_AUDIO,
)

main_analyzer = Analyzer(packets_dicts=reference_packet_dicts)


current_audio_frequency = INITIAL_AUDIO_FREQUENCY
while current_audio_frequency <= AUDIO_FREQUENCY_LIMIT:
    print(f'Start {current_audio_frequency}Hz test:\r\n'
          f'---------------------------------------------')
    SoundController.playback_start_threaded(frequency=current_audio_frequency)  # audio playback in separate thread
    time.sleep(1)  # wait for playback to start

    packets_dicts = mavlink_wrapper.receive_multiple_packet_dicts(  # read X packets to use as a reference
        packet_type=PACKET_TYPE_TO_ANALYZE,
        packets_read_amount=PACKETS_TO_COLLECT_WITH_AUDIO,
    )
    main_analyzer.append_packets(packets_dicts=packets_dicts)

    while SoundController.playback_thread is not None:
        # print(f'Wait for playback to finish')
        time.sleep(1)

    current_audio_frequency += AUDIO_FREQUENCY_STEP


print(f'\r\n'
      f'Anomalies:\r\n'
      f'----------------------------------------------------------\r\n'
      f'{main_analyzer.describe_packets()}\r\n\r\n')

print(f'Z-Score outliners:\r\n{main_analyzer.calc_zscore_outliners()}')




# for frequency, anomalies_df in results.items():
#     print(f'Frequency {frequency} anomalies:\r\n'
#           f'{anomalies_df}\r\n')
#
breakpoint()
print('SSSSSS')



