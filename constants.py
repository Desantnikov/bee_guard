import pyaudio

from enums import MavlinkPacketTypes

AUDIO_FORMAT = pyaudio.paFloat32
AUDIO_CHANNELS = 2
AUDIO_SAMPLING_RATE = 192000

MAVLINK_SERIAL_PORT = "COM9"
MAVLINK_SERIAL_BAUDRATE = 921600

PACKETS_TO_COLLECT_WITHOUT_AUDIO = 50
PACKETS_TO_COLLECT_WITH_AUDIO = 50
MOCK_DRONE_CONTROLLER = False
RESET_INPUT_BUFFER = True
PACKET_TYPE_TO_ANALYZE = MavlinkPacketTypes.RAW_IMU  #
PACKET_TYPE_UPDATE_RATE_TO_REQUEST = 10
INITIAL_AUDIO_FREQUENCY = 5000
AUDIO_FREQUENCY_LIMIT = 5050
AUDIO_FREQUENCY_STEP = 10
SHOW_PLOTS = True

TIME_SINCE_BOOT_COL_NAME = "time_usec"  # TODO: Move to enums
TIME_ELAPSED_COL_NAME = "time_elapsed"
FREQUENCY_COL_NAME = "frequency"

LOGS_FOLDER = "logs"
MOCK_DATA_FOLDER = "mock_data"
COLLECTED_DATA_FOLDER = "collected_data"

LOG_FILE_NAME = "main.log"
