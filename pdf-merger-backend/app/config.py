import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "secret-key")
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB

    UPLOAD_FOLDER = "uploads"
    OUTPUT_FOLDER = "output"