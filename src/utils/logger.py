"""
Logging Utility
Handles application logging with rotation
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Maximum log file size: 5MB
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5MB in bytes
BACKUP_COUNT = 3  # Keep 3 backup files


def setup_logger(name: str = "AppLauncher", log_file: str = None) -> logging.Logger:
    """
    Set up application logger with rotation
    
    Args:
        name: Logger name
        log_file: Path to log file (default: logs/app.log)
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    if log_file is None:
        log_dir = Path(__file__).parent.parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "app.log"
    else:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Rotating file handler (rotates when file exceeds 5MB, keeps 3 backups)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler (only warnings and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger


# Global logger instance
logger = setup_logger()
