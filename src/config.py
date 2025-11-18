"""
Configuration settings for the application
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings"""

    # OpenAI API
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Weather API
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "YOUR_API_KEY_HERE")

    # Naver API (optional)
    NAVER_CLIENT_ID: str = os.getenv("NAVER_CLIENT_ID", "")
    NAVER_CLIENT_SECRET: str = os.getenv("NAVER_CLIENT_SECRET", "")

    # Database
    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_HOST: str = os.getenv("DB_HOST", "")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_NAME: str = os.getenv("DB_NAME", "")


settings = Settings()
