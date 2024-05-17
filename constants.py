import pyaudio

from enums import MavlinkPacketTypes

AUDIO_FORMAT = pyaudio.paInt32
AUDIO_CHANNELS = 2
AUDIO_SAMPLING_RATE = 192000

MAVLINK_SERIAL_PORT = "COM11"
MAVLINK_SERIAL_BAUDRATE = 57600

PACKETS_TO_COLLECT_WITHOUT_AUDIO = 200
PACKETS_TO_COLLECT_WITH_AUDIO = 10
MOCK_DRONE_CONTROLLER = True
RESET_INPUT_BUFFER = False
PACKET_TYPE_TO_ANALYZE = MavlinkPacketTypes.RAW_IMU
PACKET_TYPE_UPDATE_RATE_TO_REQUEST = 10
INITIAL_AUDIO_FREQUENCY = 24000
AUDIO_FREQUENCY_LIMIT = 24200
AUDIO_FREQUENCY_STEP = 100
SHOW_PLOTS = True

TIME_COL_NAME = "time_usec"  # TODO: Move to enums
FREQUENCY_COL_NAME = "frequency"

LOGS_FOLDER = "logs"
MOCK_DATA_FOLDER = "mock_data"
COLLECTED_DATA_FOLDER = "collected_data"

LOG_FILE_NAME = "main.log"
