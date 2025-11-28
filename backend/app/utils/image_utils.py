"""
이미지 처리 유틸리티 함수
"""
import os
import uuid
from pathlib import Path
from typing import Tuple
from PIL import Image
import io
from datetime import datetime

from app.core.config import settings
from app.core.logging import app_logger as logger


def ensure_upload_dir():
    """업로드 디렉토리 생성"""
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    logger.info(f"Upload directory ensured: {settings.UPLOAD_DIR}")


def generate_image_filename(extension: str = "png") -> str:
    """
    고유한 이미지 파일명 생성

    형식: YYYYMMDD_UUID.extension
    예: 20251104_a1b2c3d4-e5f6-7890-abcd-ef1234567890.png
    """
    date_str = datetime.now().strftime("%Y%m%d")
    unique_id = str(uuid.uuid4())
    filename = f"{date_str}_{unique_id}.{extension}"
    return filename


def save_image(image: Image.Image, filename: str = None) -> Tuple[str, str]:
    """
    이미지를 파일 시스템에 저장

    Args:
        image: PIL Image 객체
        filename: 파일명 (None이면 자동 생성)

    Returns:
        (파일 경로, 상대 URL)
    """
    try:
        ensure_upload_dir()

        # 파일명 생성
        if filename is None:
            filename = generate_image_filename()

        # 전체 경로
        file_path = os.path.join(settings.UPLOAD_DIR, filename)

        # 이미지 저장
        image.save(file_path, format='PNG', optimize=True, quality=95)
        logger.info(f"Image saved: {file_path}")

        # 상대 URL 생성
        relative_url = f"/static/uploads/{filename}"

        return file_path, relative_url

    except Exception as e:
        logger.exception(f"Failed to save image: {str(e)}")
        raise


def save_images(images: list[Image.Image]) -> list[str]:
    """
    여러 이미지를 저장하고 URL 리스트 반환

    Args:
        images: PIL Image 객체 리스트

    Returns:
        URL 리스트
    """
    urls = []

    for i, image in enumerate(images):
        try:
            _, url = save_image(image)
            urls.append(url)
            logger.info(f"Image {i+1}/{len(images)} saved: {url}")
        except Exception as e:
            logger.error(f"Failed to save image {i+1}: {str(e)}")
            # 실패해도 계속 진행
            continue

    return urls


def validate_image_size(width: int, height: int) -> bool:
    """이미지 크기 검증"""
    if width < 512 or height < 512:
        return False
    if width > settings.MAX_IMAGE_WIDTH or height > settings.MAX_IMAGE_HEIGHT:
        return False
    return True


def resize_image(image: Image.Image, max_width: int = 2048, max_height: int = 2048) -> Image.Image:
    """
    이미지 크기 조절 (비율 유지)

    Args:
        image: PIL Image 객체
        max_width: 최대 너비
        max_height: 최대 높이

    Returns:
        리사이즈된 Image 객체
    """
    width, height = image.size

    # 이미 작으면 그대로 반환
    if width <= max_width and height <= max_height:
        return image

    # 비율 계산
    ratio = min(max_width / width, max_height / height)
    new_width = int(width * ratio)
    new_height = int(height * ratio)

    # 리사이즈
    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    logger.info(f"Image resized: {width}x{height} -> {new_width}x{new_height}")

    return resized


def image_to_base64(image: Image.Image) -> str:
    """이미지를 Base64 문자열로 변환"""
    import base64

    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    img_bytes = buffer.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')

    return img_base64


def base64_to_image(base64_str: str) -> Image.Image:
    """Base64 문자열을 이미지로 변환"""
    import base64

    img_bytes = base64.b64decode(base64_str)
    image = Image.open(io.BytesIO(img_bytes))

    return image
