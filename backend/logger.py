"""Centralized logging configuration for the application."""

import logging
import sys
from pathlib import Path

from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger

LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Create root logger
logger = logging.getLogger("bismar")
logger.setLevel(logging.DEBUG)

# Remove any existing handlers
logger.handlers = []

# JSON File Handler (for structured logging)
json_file_handler = RotatingFileHandler(
    LOG_DIR / "app.log",
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5
)
json_formatter = jsonlogger.JsonFormatter(
    "%(timestamp)s %(level)s %(name)s %(message)s"
)
json_file_handler.setFormatter(json_formatter)
logger.addHandler(json_file_handler)

# Console Handler (human-readable)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# Error File Handler
error_file_handler = RotatingFileHandler(
    LOG_DIR / "error.log",
    maxBytes=10 * 1024 * 1024,
    backupCount=5
)
error_file_handler.setLevel(logging.ERROR)
error_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
)
error_file_handler.setFormatter(error_formatter)
logger.addHandler(error_file_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(f"bismar.{name}")
