from pydantic import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    AZURE_FORM_RECOGNIZER_ENDPOINT: str = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT", "")
    AZURE_FORM_RECOGNIZER_KEY: str = os.getenv("AZURE_FORM_RECOGNIZER_KEY", "")
    
    # Server settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "相続税申告書類処理システム"
    
    # CORS settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://*.cloudflarePages.dev",
        "https://*.railway.app"
    ]
    
    # File upload settings
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".jpg", ".jpeg", ".png", ".heic", ".heif"]
    
    # Processing settings
    MAX_CONCURRENT_OCR: int = 5
    OCR_TIMEOUT: int = 60  # seconds
    
    # Paths
    UPLOAD_PATH: str = "uploads"
    OUTPUT_PATH: str = "outputs"
    TEMP_PATH: str = "temp"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()