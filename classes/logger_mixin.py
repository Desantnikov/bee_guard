import logging


class LoggerMixin:
    logger = logging.getLogger(__qualname__)

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug(f"Initializing {self.__class__.__name__}")
