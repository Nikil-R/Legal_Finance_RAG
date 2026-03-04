import logging
import sys


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Return a configured logger with a standard format.

    Args:
        name:  Logger name (typically __name__ of the calling module).
        level: Logging level string, e.g. "DEBUG", "INFO", "WARNING".

    Returns:
        A configured logging.Logger instance.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False
    return logger
