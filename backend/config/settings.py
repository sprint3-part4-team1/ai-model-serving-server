"""
Advanced AI Image Transformation System Configuration
Supports multiple backends: vLLM, TensorRT-LLM, Triton, HuggingFace
"""
import os
from pathlib import Path
from typing import Optional, Literal
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """시스템 전역 설정"""

    # Project Info
    PROJECT_NAME: str = "FoodAI Transform Studio"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"

    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    MODELS_DIR: Path = DATA_DIR / "models"
    UPLOADS_DIR: Path = DATA_DIR / "uploads"
    OUTPUTS_DIR: Path = DATA_DIR / "outputs"
    CACHE_DIR: Path = DATA_DIR / "cache"

    # OpenAI API (for prompt understanding)
    OPENAI_API_KEY: str = Field(default="")
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_VISION_MODEL: str = "gpt-4-vision-preview"

    # Model Backend Selection
    IMAGE_BACKEND: Literal["diffusers", "tensorrt", "triton", "onnx"] = "diffusers"
    LLM_BACKEND: Literal["vllm", "transformers", "ollama", "mlserver"] = "vllm"

    # Stable Diffusion Settings
    SD_MODEL_ID: str = "stabilityai/stable-diffusion-xl-base-1.0"
    SD_REFINER_ID: str = "stabilityai/stable-diffusion-xl-refiner-1.0"
    CONTROLNET_MODEL: str = "diffusers/controlnet-canny-sdxl-1.0"
    IP_ADAPTER_MODEL: str = "h94/IP-Adapter"

    # VLLM Settings
    VLLM_MODEL: str = "llava-hf/llava-v1.6-mistral-7b-hf"
    VLLM_TENSOR_PARALLEL: int = 1
    VLLM_GPU_MEMORY_UTIL: float = 0.9
    VLLM_MAX_MODEL_LEN: int = 4096

    # Performance Settings
    USE_XFORMERS: bool = True
    USE_TORCH_COMPILE: bool = False
    ENABLE_CPU_OFFLOAD: bool = False
    USE_SAFETENSORS: bool = True

    # TensorRT Settings
    TENSORRT_ENABLED: bool = False
    TENSORRT_PRECISION: Literal["fp32", "fp16", "int8"] = "fp16"

    # KV Cache Settings (for LLM)
    KV_CACHE_DTYPE: str = "auto"
    ENABLE_PREFIX_CACHING: bool = True

    # Generation Settings
    DEFAULT_HEIGHT: int = 1024
    DEFAULT_WIDTH: int = 1024
    MAX_HEIGHT: int = 2048
    MAX_WIDTH: int = 2048
    DEFAULT_STEPS: int = 30
    DEFAULT_GUIDANCE: float = 7.5
    MAX_BATCH_SIZE: int = 4

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 9090
    WORKERS: int = 1
    RELOAD: bool = True

    # Redis Cache
    REDIS_ENABLED: bool = False
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    CACHE_TTL: int = 3600

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[Path] = BASE_DIR / "logs" / "app.log"

    # MLFlow Tracking
    MLFLOW_ENABLED: bool = False
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    MLFLOW_EXPERIMENT_NAME: str = "food_ai_transform"

    # Throughput & Latency Optimization
    ASYNC_GENERATION: bool = True
    BATCH_TIMEOUT: float = 0.1  # seconds
    MAX_QUEUE_SIZE: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories
        for dir_path in [self.DATA_DIR, self.MODELS_DIR, self.UPLOADS_DIR,
                        self.OUTPUTS_DIR, self.CACHE_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)

        if self.LOG_FILE:
            self.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
