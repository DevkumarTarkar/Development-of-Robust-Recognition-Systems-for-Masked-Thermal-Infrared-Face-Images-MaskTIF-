"""Application configuration for the MaskTIF backend.

Centralizes paths, secrets, database URI, and other runtime options.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# This points to the MaskTIF_Project folder that contains data/, models/, src/, etc.
PROJECT_ROOT = os.path.dirname(BASE_DIR)


class Config:
    """Base configuration class used by the Flask app."""

    # General security / app settings
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key")

    # Database configuration (SQLite file in the backend folder by default)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'masktif.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT configuration
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-this-jwt-secret")

    # File uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB

    # Model and data paths (compatible with existing MaskTIF project structure)
    MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "masktif_model.pth")
    TRAIN_DIR = os.path.join(PROJECT_ROOT, "data", "masked", "train")

    # Rate limiting (requests per minute per IP)
    RATELIMIT_DEFAULT = "200 per minute"
    RATELIMIT_STORAGE_URI = os.environ.get("REDIS_URL", "memory://")

    # Allowed image extensions for upload
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "gif", "webp"}

