import logging

from constants import LOGS_FOLDER


class FindFontFilter(logging.Filter):
    def filter(self, record):
        # Ignore matplotlibs "findfont" logs
        return "matplotlib" not in record.getMessage()


def setup_logger(log_file_name, log_level):
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Create a file handler and set log_level to write logs to file
    file_handler = logging.FileHandler(f"{LOGS_FOLDER}/{log_file_name}")
    file_handler.setLevel(log_level)

    # Create a stream handler and set log_level to write logs to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # Create a formatter and set the format for the handlers
    formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    matplotlib_logger = logging.getLogger("matplotlib")
    # matplotlib_logger.setLevel(logging.WARNING
    # Add filter to ignore findfont logs from matplotlib
    matplotlib_logger.addFilter(FindFontFilter())
    return logger
