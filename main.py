import datetime
import logging

import pandas as pd
from pymavlink import mavutil

from classes.analyzer import Analyzer
from classes.drone_controller import DroneController, MockedDroneController
from classes.sound_controller import SoundController
from constants import (
    AUDIO_FREQUENCY_LIMIT,
    AUDIO_FREQUENCY_STEP,
    COLLECTED_DATA_FOLDER,
    INITIAL_AUDIO_FREQUENCY,
    LOG_FILE_NAME,
    MAVLINK_SERIAL_BAUDRATE,
    MAVLINK_SERIAL_PORT,
    PACKET_TYPE_TO_ANALYZE,
    PACKET_TYPE_UPDATE_RATE_TO_REQUEST,
    PACKETS_TO_COLLECT_WITH_AUDIO,
    PACKETS_TO_COLLECT_WITHOUT_AUDIO,
    RESET_INPUT_BUFFER,
    SHOW_PLOTS,
    USE_SAMPLE_PACKETS,
)
from logger_setup import setup_logger

"""
TODO: 
    make packets collecting and sound playback time equal
    handle drone-pc communication breakdown (currently no read timeout, so waits for new packets forever)
    adjust drawing plots
    
    add logging
    create new "<start_time>_mavlink_logs.log" file for each run
    remove parent try/except
     
    add config class
    move logger setup to config
    move pandas settings to config
    move saving inside analyzer class
    refactor importing StrEnum
    use mock drone data if script launched with "--mock" parameter 
    
    migrate to poetry
    
"""


# TODO: Move to config
pd.set_option("display.max_colwidth", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.expand_frame_repr", False)
pd.set_option("display.float_format", lambda x: f"{x:.2f}")

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
# ---------- logger ---------------


setup_logger(log_file_name=LOG_FILE_NAME, log_level=logging.DEBUG)  # TODO: Move to setup
# ----------------------------------

logger = logging.getLogger("main")

try:

    logger.info("TEST")

    drone_controller_cls = DroneController
    if USE_SAMPLE_PACKETS:  # use fake wrapper returning sample data if enabled
        drone_controller_cls = MockedDroneController

    drone_controller = drone_controller_cls(
        serial_port=MAVLINK_SERIAL_PORT,
        baudrate=MAVLINK_SERIAL_BAUDRATE,
        default_exclude_fields=["mavpackettype", "id", "xmag", "ymag", "zmag"],  # TODO: Move to constants?
        do_reset_input_buffer=RESET_INPUT_BUFFER,
    )

    # set RAW_IMU message update frequency
    drone_controller.request_message_interval(
        message_id=mavutil.mavlink.MAVLINK_MSG_ID_RAW_IMU,
        frequency_hz=PACKET_TYPE_UPDATE_RATE_TO_REQUEST,
    )

    # read first X packets without sound enabled to use as a reference data
    reference_packet_dicts = drone_controller.receive_multiple_packet_dicts(
        packet_type=PACKET_TYPE_TO_ANALYZE,
        packets_read_amount=PACKETS_TO_COLLECT_WITHOUT_AUDIO,
    )

    analyzer = Analyzer(packets_dicts=reference_packet_dicts)
    sound_controller = SoundController()

    current_audio_frequency = INITIAL_AUDIO_FREQUENCY
    while current_audio_frequency <= AUDIO_FREQUENCY_LIMIT:
        drone_controller.clear_input_buffer()  # clear all input packets before iteration

        logger.info(f"\r\n\r\nStart {current_audio_frequency}Hz test:\r\n---------------------------------------------")
        sound_controller.playback_start_threaded(frequency=current_audio_frequency)  # audio playback in separate thread

        packets_dicts = drone_controller.receive_multiple_packet_dicts(  # read X packets to use as a reference
            packet_type=PACKET_TYPE_TO_ANALYZE,
            packets_read_amount=PACKETS_TO_COLLECT_WITH_AUDIO,
        )
        analyzer.append_packets(packets_dicts=packets_dicts)
        analyzer.update_frequency_col(frequency=current_audio_frequency)

        sound_controller.playback_thread.join()

        logger.info(f"Stop {current_audio_frequency}Hz test ---------------------------")
        current_audio_frequency += AUDIO_FREQUENCY_STEP

    logger.info(
        f"----------------------------------------------\r\n"
        f"Audio tests finished, tested frequencies {INITIAL_AUDIO_FREQUENCY}Hz - {AUDIO_FREQUENCY_LIMIT}Hz; "
        f"Step {AUDIO_FREQUENCY_STEP}\r\n"
        f"----------------------------------------------\r\n"
    )

    logger.info(
        f"\r\n"
        f"Anomalies:\r\n"
        f"----------------------------------------------------------\r\n"
        f"{analyzer.describe_packets()}"
    )

    logger.info(
        f"\r\n"
        f"Z-Score outliners:\r\n"
        f"----------------------------------------------------------\r\n"
        f"{analyzer.calc_zscore_outliners()}"
    )

    if SHOW_PLOTS:
        analyzer.show_plot()

    saved_file_name = datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S")  # TODO: Move saving to analyzer class
    analyzer.packets_df.to_csv(f"./{COLLECTED_DATA_FOLDER}/{saved_file_name}.csv")

    logger.info("FINISH")

except Exception:
    logger.exception(msg="Exception", exc_info=True)
    breakpoint()
