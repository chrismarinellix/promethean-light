"""Detailed logging for debugging"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(name: str = "prometheus", log_dir: Path = None) -> logging.Logger:
    """Setup detailed file and console logging"""

    if log_dir is None:
        log_dir = Path.home() / ".mydata" / "logs"

    log_dir.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Remove existing handlers
    logger.handlers.clear()

    # File handler - detailed logs
    log_file = log_dir / f"prometheus_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler - important messages only
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    logger.info(f"Logging initialized. Log file: {log_file}")

    return logger


# Global logger instance
_logger = None


def get_logger() -> logging.Logger:
    """Get or create the global logger"""
    global _logger
    if _logger is None:
        _logger = setup_logger()
    return _logger
