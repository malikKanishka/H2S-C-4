import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-only-change-me-too")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "30")))
    JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    CORS_ALLOWED_ORIGINS = [
        origin.strip() 
        for origin in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",") 
        if origin.strip()
    ]
    # Limiter uses memory for this demo
    RATELIMIT_STORAGE_URI = "memory://"
