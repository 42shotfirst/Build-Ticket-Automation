#!/usr/bin/env python3
"""
Module 6: Logging Utility
==========================
Centralized logging configuration.
"""

import logging
import os
from datetime import datetime
from typing import Optional


def setup_logger(
    name: str = 'build_ticket_automation',
    log_file: Optional[str] = None,
    level: str = 'INFO',
    console_output: bool = True
) -> logging.Logger:
    """
    Setup a logger with file and console handlers.

    Args:
        name: Logger name
        log_file: Path to log file (optional)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_output: Whether to output to console

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_file:
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def create_timestamped_log_file(base_name: str = 'automation', log_dir: str = 'logs') -> str:
    """
    Create a timestamped log file path.

    Args:
        base_name: Base name for the log file
        log_dir: Directory to store logs

    Returns:
        Full path to the log file
    """
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f"{base_name}_{timestamp}.log")
    return log_file
