
import logging
import os
from logging.handlers import RotatingFileHandler
from .config import LOG_DIR, LOG_FILE

def get_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    """Return a named logger writing to console and rotating file."""
    os.makedirs(LOG_DIR, exist_ok=True)
    log_path  = os.path.join(LOG_DIR, LOG_FILE)
    fmt       = "%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s"
    formatter = logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")
    logger    = logging.getLogger(name)
    logger.setLevel(level)
    if logger.handlers:
        return logger   # avoid duplicate handlers on re-import
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    fh = RotatingFileHandler(log_path, maxBytes=5*1024*1024, backupCount=3)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger
