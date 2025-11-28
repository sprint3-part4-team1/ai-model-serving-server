"""
Stable Diffusion 2 Inpainting Pipeline
배경만 변경하고 제품은 보존
"""
import torch
import numpy as np
from PIL import Image
from typing import Optional, Union
from loguru import logger

from diffusers import StableDiffusionInpaintPipeline, DPMSolverMultistepScheduler
from backend.config.settings import settings


class InpaintingPipeline:
    """SD 2 Inpainting 기반 배경 교체"""

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.float16 if self.device == "cuda" else torch.float32
        self.pipeline = None

        logger.info(f"InpaintingPipeline initialized on {self.device}")

    def _load_pipeline(self):
        """Inpainting 파이프라인 로딩 (Lazy Loading)"""
        if self.pipeline is not None:
            return

        logger.info("Loading SD 2 Inpainting model...")

        self.pipeline = StableDiffusionInpaintPipeline.from_pretrained(
            "stabilityai/stable-diffusion-2-inpainting",
            torch_dtype=self.dtype,
            use_safetensors=True
        ).to(self.device)

        # 최적화
        if settings.USE_XFORMERS:
            try:
                self.pipeline.enable_xformers_memory_efficient_attention()
                logger.info("xFormers enabled for inpainting")
            except Exception as e:
                logger.warning(f"xFormers not available: {e}")

        self.pipeline.enable_vae_slicing()
        self.pipeline.enable_vae_tiling()

        # 스케줄러 최적화
        self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
            self.pipeline.scheduler.config,
            use_karras_sigmas=True
        )

        logger.info("Inpainting pipeline loaded successfully")

    async def replace_background(
        self,
        image: Image.Image,
        mask: Union[Image.Image, np.ndarray],
        prompt: str,
        negative_prompt: str = "",
        strength: float = 0.75,
        guidance_scale: float = 8.0,
        num_inference_steps: int = 50,
    ) -> Image.Image:
        """
        배경만 교체 (제품 보존)

        Args:
            image: 원본 이미지
            mask: 마스크 (255 = 변경할 영역(배경), 0 = 보존할 영역(제품))
            prompt: 배경 프롬프트
            negative_prompt: 네거티브 프롬프트
            strength: 변환 강도 (0.0-1.0)
            guidance_scale: 가이던스 스케일
            num_inference_steps: 추론 스텝 수

        Returns:
            배경이 교체된 이미지
        """
        self._load_pipeline()

        # 마스크 처리
        if isinstance(mask, np.ndarray):
            mask_image = Image.fromarray((mask * 255).astype(np.uint8)).convert("L")
        else:
            mask_image = mask.convert("L")

        # 이미지 크기를 8의 배수로 조정
        width, height = image.size
        new_width = (width // 8) * 8
        new_height = (height // 8) * 8

        if (new_width, new_height) != (width, height):
            logger.info(f"Resizing from {width}x{height} to {new_width}x{new_height}")
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            mask_image = mask_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        logger.info(f"Inpainting with prompt: {prompt[:100]}...")

        # Inpainting 실행
        result = self.pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            image=image,
            mask_image=mask_image,
            strength=strength,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
        ).images[0]

        # 원본 크기로 복원
        if (new_width, new_height) != (width, height):
            result = result.resize((width, height), Image.Resampling.LANCZOS)

        logger.info("Inpainting completed")
        return result

    def cleanup(self):
        """메모리 정리"""
        if self.pipeline:
            del self.pipeline
            self.pipeline = None

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        logger.info("Inpainting pipeline memory cleaned")


# 싱글톤 인스턴스
_inpainting_instance = None


def get_inpainting_pipeline() -> InpaintingPipeline:
    """Inpainting Pipeline 싱글톤 반환"""
    global _inpainting_instance
    if _inpainting_instance is None:
        _inpainting_instance = InpaintingPipeline()
    return _inpainting_instance
