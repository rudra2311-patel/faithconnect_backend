from pathlib import Path
from pydantic_settings import BaseSettings
import os

# Get the path to the .env file (in backend directory)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    DATABASE_URL: str
    
    # JWT Settings
    SECRET_KEY: str = "your-secret-key-here-change-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    
    # Server URL (auto-detect from environment)
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")
    
    # Cloudinary Settings (for cloud storage)
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")
    
    class Config:
        env_file = str(ENV_FILE)
        case_sensitive = True


settings = Settings()
