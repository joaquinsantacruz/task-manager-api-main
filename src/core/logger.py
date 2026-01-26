"""
Logging configuration for the application.

This module provides centralized logging setup with:
- Console output with colored formatting
- File output with rotation
- Different log levels for different environments
- Structured logging format
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from src.core.config import settings

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Custom log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(name: str) -> logging.Logger:
    """
    Set up a logger with console and file handlers.
    
    Args:
        name: Name of the logger (usually __name__ of the module)
    
    Returns:
        Configured logger instance
    
    Features:
        - Console handler with colored output (if supported)
        - Rotating file handler (10MB max, 5 backup files)
        - Different log levels based on environment
        - Structured format with timestamp, logger name, level, and message
    
    Example:
        >>> logger = setup_logger(__name__)
        >>> logger.info("Application started")
        >>> logger.error("An error occurred", exc_info=True)
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Set log level based on environment
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    logger.setLevel(log_level)
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File Handler with rotation
    file_handler = RotatingFileHandler(
        LOGS_DIR / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Error File Handler (only errors and above)
    error_handler = RotatingFileHandler(
        LOGS_DIR / "error.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d",
        DATE_FORMAT
    )
    error_handler.setFormatter(error_formatter)
    logger.addHandler(error_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger instance.
    
    This is a convenience function that wraps setup_logger.
    
    Args:
        name: Name of the logger (usually __name__ of the module)
    
    Returns:
        Configured logger instance
    
    Example:
        >>> from src.core.logger import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("User logged in", extra={"user_id": 123})
    """
    return setup_logger(name)
