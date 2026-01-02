import logging


def get_custom_logger(logger_path: str) -> logging.Logger:
    stream_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(logger_path)

    format = (
        "### %(asctime)s [%(levelname)s] %(filename)s - line %(lineno)d:: %(message)s"
    )
    stream_handler.setFormatter(logging.Formatter(format))
    file_handler.setFormatter(logging.Formatter(format))

    logger = logging.getLogger("logger")
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)

    return logger
