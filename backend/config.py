import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'masktif.db')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-this-jwt-secret")
    
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024 # 10mb max
    
    # Model path stuff
    MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "masktif_model.pth")
    TRAIN_DIR = os.path.join(PROJECT_ROOT, "data", "masked", "train")
    
    RATELIMIT_DEFAULT = "200 per minute"
    RATELIMIT_STORAGE_URI = os.environ.get("REDIS_URL", "memory://")
    
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "gif", "webp"}
