"""Uploaded file validation utilities.

Validates incoming uploaded files to protect downstream processing.
"""

import os
from app.utils.logger import logger

ALLOWED_EXTENSIONS = {".pdf"}
MIN_FILES = 2
MAX_FILES = 5
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def validate_files(files):
    """
    Validates uploaded PDF files.
    Raises ValueError if validation fails.
    """
    logger.info("Validating uploaded files")
    if not files:
        raise ValueError("No PDF files uploaded.")

    if len(files) < MIN_FILES:
        raise ValueError(
            f"Please upload at least {MIN_FILES} PDF files."
        )

    if len(files) > MAX_FILES:
        raise ValueError(
            f"Maximum {MAX_FILES} PDF files are allowed."
        )

    for file in files:

        # Check filename
        if not file.filename:
            raise ValueError("One of the uploaded files has no filename.")

        # Check extension
        _, extension = os.path.splitext(file.filename)

        if extension.lower() not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Invalid file '{file.filename}'. Only PDF files are allowed."
            )

        # Check file size
        file.stream.seek(0, os.SEEK_END)
        size = file.stream.tell()
        file.stream.seek(0)

        if size == 0:
            raise ValueError(
                f"File '{file.filename}' is empty."
            )

        if size > MAX_FILE_SIZE:
            raise ValueError(
                f"File '{file.filename}' exceeds the maximum size of 10 MB."
            )

    return True