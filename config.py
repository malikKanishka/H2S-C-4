import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-only-change-me-too")
    CORS_ALLOWED_ORIGINS = [
        origin.strip() 
        for origin in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",") 
        if origin.strip()
    ]
    # Limiter uses memory for this demo
    RATELIMIT_STORAGE_URI = "memory://"
