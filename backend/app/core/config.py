"""
애플리케이션 설정 관리
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator
import os
from pathlib import Path


class Settings(BaseSettings):
    """애플리케이션 전역 설정"""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # Ignore extra env vars like HF_HUB_DISABLE_SYMLINKS
    )

    # Application
    APP_NAME: str = "소상공인 광고 콘텐츠 생성 서비스"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 9090
    WORKERS: int = 4

    # API Keys
    OPENAI_API_KEY: str
    HUGGINGFACE_TOKEN: str = ""

    # Seasonal Story API Keys
    OPENWEATHER_API_KEY: str = "YOUR_API_KEY_HERE"
    NAVER_CLIENT_ID: str = ""
    NAVER_CLIENT_SECRET: str = ""

    # Instagram Graph API (SNS 트렌드 수집용)
    INSTAGRAM_ACCESS_TOKEN: str = "YOUR_ACCESS_TOKEN_HERE"
    INSTAGRAM_BUSINESS_ACCOUNT_ID: str = ""

    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str
    REDIS_MAX_CONNECTIONS: int = 50

    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    CORS_ALLOW_CREDENTIALS: bool = True

    # File Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: str = "jpg,jpeg,png,webp"
    UPLOAD_DIR: str = "./data/uploads"
    STATIC_DIR: str = "./data/static"

    # Model Settings
    MODEL_CACHE_DIR: str = "./data/models"
    STABLE_DIFFUSION_MODEL: str = "stabilityai/stable-diffusion-xl-base-1.0"
    CONTROLNET_MODEL: str = "lllyasviel/control_v11p_sd15_canny"
    LORA_DIR: str = "./data/lora_models"

    # Generation Settings
    DEFAULT_IMAGE_WIDTH: int = 1024
    DEFAULT_IMAGE_HEIGHT: int = 1024
    MAX_IMAGE_WIDTH: int = 2048
    MAX_IMAGE_HEIGHT: int = 2048
    DEFAULT_NUM_INFERENCE_STEPS: int = 50
    MAX_NUM_INFERENCE_STEPS: int = 100
    DEFAULT_GUIDANCE_SCALE: float = 7.5

    # Performance
    USE_XFORMERS: bool = True
    ENABLE_CPU_OFFLOAD: bool = False
    USE_HALF_PRECISION: bool = True

    # Caching
    CACHE_TTL: int = 3600
    ENABLE_RESULT_CACHE: bool = True

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    LOG_ROTATION: str = "500 MB"
    LOG_RETENTION: str = "10 days"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 30
    RATE_LIMIT_PER_HOUR: int = 500

    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090

    @validator("ALLOWED_ORIGINS")
    def parse_origins(cls, v: str) -> List[str]:
        """CORS origins를 리스트로 변환"""
        return [origin.strip() for origin in v.split(",")]

    @validator("ALLOWED_EXTENSIONS")
    def parse_extensions(cls, v: str) -> List[str]:
        """허용된 파일 확장자를 리스트로 변환"""
        return [ext.strip() for ext in v.split(",")]

    def ensure_directories(self):
        """필요한 디렉토리 생성"""
        dirs = [
            self.UPLOAD_DIR,
            self.STATIC_DIR,
            self.MODEL_CACHE_DIR,
            self.LORA_DIR,
            os.path.dirname(self.LOG_FILE),
        ]
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)


# 전역 설정 인스턴스
settings = Settings()

# 필요한 디렉토리 생성
settings.ensure_directories()
