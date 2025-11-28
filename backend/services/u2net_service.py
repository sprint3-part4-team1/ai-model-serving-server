"""
U2-Net 기반 배경 제거 서비스
고품질 배경 제거 및 교체 기능 제공
"""
import torch
import numpy as np
from PIL import Image
from typing import Optional, Tuple
from pathlib import Path
from loguru import logger
import cv2

try:
    from u2net import U2NET, U2NETP
    U2NET_AVAILABLE = True
except ImportError:
    U2NET_AVAILABLE = False
    logger.warning("U2-Net not installed, falling back to rembg")

from rembg import remove as rembg_remove
from backend.config.settings import settings


class U2NetBackgroundRemover:
    """U2-Net 기반 배경 제거 서비스"""

    def __init__(self, use_u2net: bool = True):
        """
        Args:
            use_u2net: True면 U2-Net 사용, False면 rembg 사용
        """
        self.use_u2net = use_u2net and U2NET_AVAILABLE
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None

        if self.use_u2net:
            logger.info("Initializing U2-Net background remover")
        else:
            logger.info("Using rembg for background removal")

    def _load_model(self):
        """U2-Net 모델 로딩 (Lazy Loading)"""
        if self.model is not None:
            return

        if not self.use_u2net:
            return

        try:
            logger.info("Loading U2-Net model...")
            # U2-Net 모델 로딩
            self.model = U2NET(3, 1)  # 입력 3채널, 출력 1채널

            # 사전 학습된 가중치 로딩
            model_path = Path(settings.MODEL_CACHE_DIR) / "u2net" / "u2net.pth"
            if model_path.exists():
                self.model.load_state_dict(
                    torch.load(model_path, map_location=self.device)
                )
            else:
                logger.warning(f"U2-Net weights not found at {model_path}")
                logger.info("Downloading U2-Net weights...")
                # TODO: 자동 다운로드 구현

            self.model.to(self.device)
            self.model.eval()
            logger.info("U2-Net model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load U2-Net: {e}")
            logger.info("Falling back to rembg")
            self.use_u2net = False

    async def remove_background(
        self,
        image: Image.Image,
        alpha_matting: bool = True,
        alpha_matting_foreground_threshold: int = 240,
        alpha_matting_background_threshold: int = 10
    ) -> Image.Image:
        """
        배경 제거

        Args:
            image: 입력 이미지
            alpha_matting: 알파 매팅 사용 여부 (경계 부드럽게)
            alpha_matting_foreground_threshold: 전경 임계값
            alpha_matting_background_threshold: 배경 임계값

        Returns:
            배경이 제거된 이미지 (투명 PNG)
        """
        logger.info("Removing background...")

        if self.use_u2net:
            return await self._remove_with_u2net(image, alpha_matting)
        else:
            return await self._remove_with_rembg(
                image,
                alpha_matting,
                alpha_matting_foreground_threshold,
                alpha_matting_background_threshold
            )

    async def _remove_with_u2net(
        self,
        image: Image.Image,
        alpha_matting: bool
    ) -> Image.Image:
        """U2-Net으로 배경 제거"""
        self._load_model()

        try:
            # 전처리
            image_np = np.array(image)
            image_rgb = cv2.cvtColor(image_np, cv2.COLOR_RGBA2RGB) if image_np.shape[2] == 4 else image_np
            image_resized = cv2.resize(image_rgb, (320, 320))
            image_normalized = image_resized.astype(np.float32) / 255.0
            image_normalized = np.transpose(image_normalized, (2, 0, 1))
            image_tensor = torch.from_numpy(image_normalized).unsqueeze(0).to(self.device)

            # 추론
            with torch.no_grad():
                d1, *_ = self.model(image_tensor)
                pred = d1[:, 0, :, :]
                pred = torch.sigmoid(pred)
                pred = pred.squeeze().cpu().numpy()

            # 마스크 후처리
            mask = cv2.resize(pred, (image.width, image.height))
            mask = (mask * 255).astype(np.uint8)

            # 알파 매팅
            if alpha_matting:
                mask = self._apply_alpha_matting(image_np, mask)

            # 투명 배경 적용
            if image.mode != "RGBA":
                image = image.convert("RGBA")

            image_np = np.array(image)
            image_np[:, :, 3] = mask

            result = Image.fromarray(image_np, "RGBA")
            logger.info("Background removed with U2-Net")
            return result

        except Exception as e:
            logger.error(f"U2-Net removal failed: {e}")
            logger.info("Falling back to rembg")
            return await self._remove_with_rembg(image, alpha_matting)

    async def _remove_with_rembg(
        self,
        image: Image.Image,
        alpha_matting: bool = True,
        alpha_matting_foreground_threshold: int = 240,
        alpha_matting_background_threshold: int = 10
    ) -> Image.Image:
        """rembg로 배경 제거"""
        try:
            result = rembg_remove(
                image,
                alpha_matting=alpha_matting,
                alpha_matting_foreground_threshold=alpha_matting_foreground_threshold,
                alpha_matting_background_threshold=alpha_matting_background_threshold
            )
            logger.info("Background removed with rembg")
            return result

        except Exception as e:
            logger.error(f"rembg removal failed: {e}")
            # 실패 시 원본 반환
            return image.convert("RGBA")

    def _apply_alpha_matting(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        iterations: int = 3
    ) -> np.ndarray:
        """알파 매팅으로 경계 부드럽게"""
        # 모폴로지 연산으로 마스크 정제
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=iterations)
        mask = cv2.GaussianBlur(mask, (5, 5), 0)

        return mask

    async def replace_background(
        self,
        image: Image.Image,
        background: Image.Image,
        blend_edges: bool = True
    ) -> Image.Image:
        """
        배경 교체

        Args:
            image: 전경 이미지
            background: 새 배경 이미지
            blend_edges: 경계 블렌딩 여부

        Returns:
            배경이 교체된 이미지
        """
        logger.info("Replacing background...")

        # 배경 제거
        foreground = await self.remove_background(image, alpha_matting=blend_edges)

        # 배경 리사이즈
        background = background.resize(foreground.size, Image.Resampling.LANCZOS)
        background = background.convert("RGBA")

        # 합성
        result = Image.alpha_composite(background, foreground)
        logger.info("Background replaced successfully")

        return result

    async def create_solid_background(
        self,
        image: Image.Image,
        color: Tuple[int, int, int] = (255, 255, 255)
    ) -> Image.Image:
        """
        단색 배경 생성

        Args:
            image: 입력 이미지
            color: 배경 색상 (R, G, B)

        Returns:
            단색 배경의 이미지
        """
        # 배경 제거
        foreground = await self.remove_background(image)

        # 단색 배경 생성
        background = Image.new("RGBA", foreground.size, (*color, 255))

        # 합성
        result = Image.alpha_composite(background, foreground)

        return result

    async def batch_remove_background(
        self,
        images: list[Image.Image]
    ) -> list[Image.Image]:
        """
        배치 배경 제거

        Args:
            images: 이미지 리스트

        Returns:
            배경이 제거된 이미지 리스트
        """
        import asyncio
        tasks = [self.remove_background(img) for img in images]
        return await asyncio.gather(*tasks)


# 싱글톤 인스턴스
_remover_instance: Optional[U2NetBackgroundRemover] = None


def get_background_remover(use_u2net: bool = True) -> U2NetBackgroundRemover:
    """U2NetBackgroundRemover 싱글톤 인스턴스 반환"""
    global _remover_instance
    if _remover_instance is None:
        _remover_instance = U2NetBackgroundRemover(use_u2net=use_u2net)
    return _remover_instance


# 편의 함수
async def remove_background(
    image: Image.Image,
    use_u2net: bool = True
) -> Image.Image:
    """배경 제거 편의 함수"""
    remover = get_background_remover(use_u2net=use_u2net)
    return await remover.remove_background(image)


async def replace_background(
    image: Image.Image,
    background: Image.Image,
    use_u2net: bool = True
) -> Image.Image:
    """배경 교체 편의 함수"""
    remover = get_background_remover(use_u2net=use_u2net)
    return await remover.replace_background(image, background)


# 테스트용
if __name__ == "__main__":
    import asyncio

    async def test():
        remover = U2NetBackgroundRemover(use_u2net=False)  # rembg로 테스트

        # 테스트 이미지
        test_image = Image.open("test.jpg")

        print("=== 배경 제거 테스트 ===\n")

        # 배경 제거
        result = await remover.remove_background(test_image)
        result.save("test_removed.png")
        print("배경 제거 완료: test_removed.png")

        # 단색 배경
        result_white = await remover.create_solid_background(test_image, (255, 255, 255))
        result_white.save("test_white_bg.png")
        print("흰색 배경: test_white_bg.png")

    asyncio.run(test())
