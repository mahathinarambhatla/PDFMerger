"""Logging utilities for the PDF Merger backend.

This module configures a file+console logger used across the app.

Exports:
    logger (logging.Logger): App logger instance.
"""

import logging
import os

# Create logs directory if it doesn't exist
log_directory = "logs"
os.makedirs(log_directory, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(log_directory, "app.log")),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)