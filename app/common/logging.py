import logging
import os

from app.common.enums import LoggingLevel


def init_logger(logger_name: str, logger_level: LoggingLevel):
    class CustomFormatter(logging.Formatter):
        """Logging Formatter to add colors and count warning / errors"""

        white = "\x1b[38;1m"
        grey = "\x1b[38;21m"
        yellow = "\x1b[33;21m"
        red = "\x1b[31;21m"
        bold_red = "\x1b[31;1m"
        reset = "\x1b[0m"
        format_str = "%(asctime)s | %(name)s | %(levelname)s | (%(filename)s:%(lineno)d)]: %(message)s "

        FORMATS = {
            logging.DEBUG: grey + format_str + reset,
            logging.INFO: white + format_str + reset,
            logging.WARNING: yellow + format_str + reset,
            logging.ERROR: red + format_str + reset,
            logging.CRITICAL: bold_red + format_str + reset,
        }

        def format(self, record):
            log_fmt = self.FORMATS.get(record.levelno)
            formatter = logging.Formatter(log_fmt)
            return formatter.format(record)

    logger = logging.getLogger(logger_name)

    console = logging.StreamHandler()
    console.setLevel(logger_level)
    console.setFormatter(CustomFormatter())

    logger.addHandler(console)
    logger.setLevel(logger_level)
    logger.propagate = False

    loggers = [
        logging.getLogger("sqlalchemy"),
        logging.getLogger("sqlalchemy.engine"),
        logging.getLogger("sqlalchemy.engine.Engine"),
        logging.getLogger("sqlalchemy.pool"),
        logging.getLogger("sqlalchemy.dialects"),
        logging.getLogger("sqlalchemy.orm"),
    ]
    for sqla_logger in loggers:
        for hdlr in sqla_logger.handlers:
            sqla_logger.removeHandler(hdlr)
        sqla_logger.addHandler(console)
        sqla_logger.propagate = False

    return logger


logger = init_logger(logger_name="common_log", logger_level=LoggingLevel[os.getenv("LOGGING_LEVEL", "INFO")])
