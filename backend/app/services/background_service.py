"""
배경 제거/교체 서비스
"""
from PIL import Image
import io
import httpx
import time
from typing import Tuple, Optional

from app.core.config import settings
from app.core.logging import app_logger as logger


class BackgroundService:
    """배경 처리 서비스"""

    def __init__(self):
        """초기화"""
        logger.info("Background 서비스 초기화")
        self.rembg_available = False

        # rembg 라이브러리 체크
        try:
            from rembg import remove
            self.rembg_available = True
            logger.info("✅ rembg 라이브러리 사용 가능")
        except ImportError:
            logger.warning("⚠️  rembg 라이브러리 없음 - 기본 방식 사용")

    async def download_image(self, image_url: str) -> Image.Image:
        """URL에서 이미지 다운로드"""
        try:
            logger.info(f"이미지 다운로드: {image_url}")

            async with httpx.AsyncClient() as client:
                response = await client.get(image_url, timeout=30)
                response.raise_for_status()
                image_data = response.content

            image = Image.open(io.BytesIO(image_data))
            logger.info(f"이미지 다운로드 완료: {image.size}")

            return image

        except Exception as e:
            logger.exception(f"이미지 다운로드 실패: {str(e)}")
            raise

    async def remove_background(
        self,
        image: Image.Image,
        return_mask: bool = False
    ) -> Tuple[Image.Image, Optional[Image.Image]]:
        """
        배경 제거

        Args:
            image: 입력 이미지
            return_mask: 마스크도 함께 반환

        Returns:
            (배경 제거된 이미지, 마스크 (선택))
        """
        start_time = time.time()

        try:
            logger.info(f"배경 제거 시작 - 크기: {image.size}")

            if self.rembg_available:
                # rembg 라이브러리 사용
                from rembg import remove

                # RGBA 모드로 변환 (투명 배경)
                output = remove(image, alpha_matting=True)
                logger.info("rembg로 배경 제거 완료")

                mask = None
                if return_mask:
                    # 알파 채널을 마스크로 추출
                    mask = output.split()[3]  # RGBA의 A 채널

            else:
                # 간단한 배경 제거 (색상 기반)
                # 실제 프로덕션에서는 rembg 사용 권장
                logger.warning("rembg 없이 기본 방식으로 배경 제거")

                # RGB로 변환
                if image.mode != 'RGB':
                    image = image.convert('RGB')

                # 간단한 임계값 기반 배경 제거
                # 실제로는 더 정교한 알고리즘 필요
                output = image.copy()
                output = output.convert('RGBA')

                # 흰색 배경을 투명하게
                data = output.getdata()
                new_data = []
                for item in data:
                    # 흰색에 가까운 픽셀을 투명하게
                    if item[0] > 240 and item[1] > 240 and item[2] > 240:
                        new_data.append((255, 255, 255, 0))
                    else:
                        new_data.append(item)

                output.putdata(new_data)

                mask = None

            processing_time = time.time() - start_time
            logger.info(f"✅ 배경 제거 완료 - {processing_time:.2f}초")

            return output, mask

        except Exception as e:
            logger.exception(f"배경 제거 실패: {str(e)}")
            raise

    async def replace_background(
        self,
        foreground: Image.Image,
        background: Image.Image
    ) -> Image.Image:
        """
        배경 교체

        Args:
            foreground: 전경 이미지 (배경 제거된 이미지)
            background: 새 배경 이미지

        Returns:
            합성된 이미지
        """
        try:
            logger.info(f"배경 교체 - 전경: {foreground.size}, 배경: {background.size}")

            # 배경을 전경 크기에 맞춤
            background_resized = background.resize(foreground.size, Image.Resampling.LANCZOS)

            # RGBA 모드 확인
            if foreground.mode != 'RGBA':
                foreground = foreground.convert('RGBA')
            if background_resized.mode != 'RGBA':
                background_resized = background_resized.convert('RGBA')

            # 합성
            result = Image.alpha_composite(background_resized, foreground)

            logger.info("✅ 배경 교체 완료")

            return result

        except Exception as e:
            logger.exception(f"배경 교체 실패: {str(e)}")
            raise

    async def create_simple_background(
        self,
        width: int,
        height: int,
        color: str = "#FFFFFF"
    ) -> Image.Image:
        """
        단색 배경 생성

        Args:
            width: 너비
            height: 높이
            color: 배경색 (hex)

        Returns:
            배경 이미지
        """
        try:
            from PIL import ImageDraw

            # 새 이미지 생성
            background = Image.new('RGB', (width, height), color)

            logger.info(f"단색 배경 생성: {width}x{height}, {color}")

            return background

        except Exception as e:
            logger.exception(f"배경 생성 실패: {str(e)}")
            raise


# 전역 서비스 인스턴스
background_service = BackgroundService()
