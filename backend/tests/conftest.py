import os

import pytest


class TestConfig:
    TESTING = True
    # Keep secrets long enough to avoid PyJWT InsecureKeyLengthWarning (>= 32 bytes recommended).
    SECRET_KEY = "test-secret-key-32-bytes-minimum____"
    JWT_SECRET_KEY = "test-jwt-secret-key-32-bytes-minimum_"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads_test")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    RATELIMIT_DEFAULT = "1000 per minute"
    RATELIMIT_STORAGE_URI = "memory://"
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "gif", "webp"}


@pytest.fixture()
def app():
    # Import here so env/config overrides are already set.
    from app import create_app

    os.makedirs(TestConfig.UPLOAD_FOLDER, exist_ok=True)
    app = create_app(TestConfig)
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()

