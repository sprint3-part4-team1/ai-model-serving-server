"""
로깅 설정
"""
import sys
from loguru import logger
from app.core.config import settings


def setup_logging():
    """로깅 시스템 초기화"""

    # 기본 로거 제거
    logger.remove()

    # 콘솔 로깅 설정
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
    )

    # 파일 로깅 설정
    logger.add(
        settings.LOG_FILE,
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.LOG_LEVEL,
        enqueue=True,  # 비동기 로깅
    )

    # 에러 전용 로그 파일
    logger.add(
        settings.LOG_FILE.replace(".log", "_error.log"),
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        enqueue=True,
    )

    logger.info(f"로깅 시스템 초기화 완료 - Level: {settings.LOG_LEVEL}")

    return logger


# 전역 로거 인스턴스
app_logger = setup_logging()
