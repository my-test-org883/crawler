import logging
import os
from logging.handlers import RotatingFileHandler
from config import LEVEL_DEBUG


def configure(location="", log_size_mb=500):
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if LEVEL_DEBUG else logging.INFO)

    log_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(filename)s -"
        "  %(funcName)s (%(lineno)d) - %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )

    log_file = os.path.join(location, "log_file.log")
    if not os.path.isfile(log_file):
        os.makedirs(location, exist_ok=True)
        open(log_file, "w").close()

    file_handler = RotatingFileHandler(
        log_file,
        mode="a",
        maxBytes=log_size_mb * 1024 * 1024,
        backupCount=2,
        encoding=None,
        delay=0,
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(log_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(log_formatter)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
