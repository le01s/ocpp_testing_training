import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = "logs"
Path(LOG_DIR).mkdir(exist_ok=True)

LOG_FORMAT = "[%(asctime)s] [%(name)s] [%(levelname)s] [%(message)s]"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging():
    logger = logging.getLogger("ocpp")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    file_handler = RotatingFileHandler(
        filename=os.path.join(LOG_DIR, "ocpp_server.log"),
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    websockets_logger = logging.getLogger("websockets")
    websockets_logger.setLevel(logging.INFO)
    websockets_logger.addHandler(console_handler)
    websockets_logger.addHandler(file_handler)

    return logger


logger = setup_logging()
