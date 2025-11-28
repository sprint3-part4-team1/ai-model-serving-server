"""
통합 이미지 변환 파이프라인
ControlNet, IP-Adapter, LoRA를 활용한 멀티모달 이미지 변환
"""
import torch
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List, Union
from PIL import Image
from loguru import logger

from diffusers import (
    StableDiffusionXLPipeline,
    StableDiffusionXLControlNetPipeline,
    ControlNetModel,
    AutoencoderKL,
    DPMSolverMultistepScheduler,
)
from diffusers.utils import load_image
from controlnet_aux import CannyDetector, OpenposeDetector, MLSDdetector
from transformers import CLIPVisionModelWithProjection, CLIPImageProcessor

from backend.config.settings import settings


class ImageTransformPipeline:
    """고급 이미지 변환 파이프라인"""

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.float16 if self.device == "cuda" else torch.float32

        # Lazy loading
        self.base_pipeline = None
        self.controlnet_pipeline = None
        self.controlnet_models = {}
        self.preprocessors = {}
        self.vae = None

        logger.info(f"ImageTransformPipeline initialized on {self.device}")

    def _load_vae(self):
        """VAE 로딩 (FP16 Fix 버전)"""
        if self.vae is None:
            logger.info("Loading VAE...")
            self.vae = AutoencoderKL.from_pretrained(
                "madebyollin/sdxl-vae-fp16-fix",
                torch_dtype=self.dtype
            ).to(self.device)

    def _load_base_pipeline(self):
        """기본 SDXL 파이프라인 로딩"""
        if self.base_pipeline is None:
            logger.info("Loading SDXL base pipeline...")
            self._load_vae()

            self.base_pipeline = StableDiffusionXLPipeline.from_pretrained(
                settings.SD_MODEL_ID,
                vae=self.vae,
                torch_dtype=self.dtype,
                use_safetensors=True,
                variant="fp16" if self.dtype == torch.float16 else None
            ).to(self.device)

            # 메모리 최적화
            if settings.USE_XFORMERS:
                try:
                    self.base_pipeline.enable_xformers_memory_efficient_attention()
                    logger.info("xFormers enabled")
                except Exception as e:
                    logger.warning(f"xFormers not available: {e}")

            # VAE Slicing
            self.base_pipeline.enable_vae_slicing()
            self.base_pipeline.enable_vae_tiling()

            # 스케줄러 최적화
            self.base_pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
                self.base_pipeline.scheduler.config,
                use_karras_sigmas=True
            )

            logger.info("Base pipeline loaded successfully")

    def _load_controlnet(self, controlnet_type: str = "canny"):
        """ControlNet 모델 로딩"""
        if controlnet_type not in self.controlnet_models:
            logger.info(f"Loading ControlNet ({controlnet_type})...")

            # ControlNet 모델 경로 매핑
            controlnet_paths = {
                "canny": "diffusers/controlnet-canny-sdxl-1.0",
                "depth": "diffusers/controlnet-depth-sdxl-1.0",
                "openpose": "thibaud/controlnet-openpose-sdxl-1.0",
                "mlsd": "xinsir/controlnet-mlsd-sdxl-1.0",
            }

            controlnet = ControlNetModel.from_pretrained(
                controlnet_paths.get(controlnet_type, controlnet_paths["canny"]),
                torch_dtype=self.dtype
            ).to(self.device)

            self.controlnet_models[controlnet_type] = controlnet
            logger.info(f"ControlNet ({controlnet_type}) loaded")

    def _load_controlnet_pipeline(self, controlnet_type: str = "canny"):
        """ControlNet 파이프라인 생성"""
        self._load_vae()
        self._load_controlnet(controlnet_type)

        logger.info("Creating ControlNet pipeline...")
        self.controlnet_pipeline = StableDiffusionXLControlNetPipeline.from_pretrained(
            settings.SD_MODEL_ID,
            controlnet=self.controlnet_models[controlnet_type],
            vae=self.vae,
            torch_dtype=self.dtype,
            use_safetensors=True,
            variant="fp16" if self.dtype == torch.float16 else None
        ).to(self.device)

        # 최적화
        if settings.USE_XFORMERS:
            try:
                self.controlnet_pipeline.enable_xformers_memory_efficient_attention()
            except Exception:
                pass

        self.controlnet_pipeline.enable_vae_slicing()
        self.controlnet_pipeline.enable_vae_tiling()

        self.controlnet_pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
            self.controlnet_pipeline.scheduler.config,
            use_karras_sigmas=True
        )

    def _get_preprocessor(self, controlnet_type: str):
        """ControlNet 전처리기 로딩"""
        if controlnet_type not in self.preprocessors:
            logger.info(f"Loading preprocessor ({controlnet_type})...")

            if controlnet_type == "canny":
                self.preprocessors[controlnet_type] = CannyDetector()
            elif controlnet_type == "openpose":
                self.preprocessors[controlnet_type] = OpenposeDetector.from_pretrained(
                    "lllyasviel/ControlNet"
                )
            elif controlnet_type == "mlsd":
                self.preprocessors[controlnet_type] = MLSDdetector.from_pretrained(
                    "lllyasviel/ControlNet"
                )

        return self.preprocessors.get(controlnet_type)

    async def generate_base(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        num_inference_steps: int = 30,
        guidance_scale: float = 7.5,
        num_images: int = 1,
    ) -> List[Image.Image]:
        """
        기본 텍스트→이미지 생성

        Args:
            prompt: 프롬프트
            negative_prompt: 네거티브 프롬프트
            width: 너비
            height: 높이
            num_inference_steps: 추론 스텝
            guidance_scale: 가이던스 스케일
            num_images: 생성 이미지 수

        Returns:
            생성된 이미지 리스트
        """
        self._load_base_pipeline()

        logger.info(f"Generating {num_images} images with base pipeline...")

        images = self.base_pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            num_images_per_prompt=num_images,
        ).images

        logger.info(f"Generated {len(images)} images")
        return images

    async def generate_with_controlnet(
        self,
        prompt: str,
        control_image: Union[str, Image.Image],
        controlnet_type: str = "canny",
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        num_inference_steps: int = 30,
        guidance_scale: float = 7.5,
        controlnet_conditioning_scale: float = 0.7,
        control_guidance_start: float = 0.0,
        control_guidance_end: float = 1.0,
    ) -> List[Image.Image]:
        """
        ControlNet을 사용한 구조 보존 이미지 생성

        Args:
            prompt: 프롬프트
            control_image: 컨트롤 이미지 (경로 또는 PIL Image)
            controlnet_type: ControlNet 타입 (canny, depth, openpose, mlsd)
            controlnet_conditioning_scale: ControlNet 강도 (0.0-2.0)
            control_guidance_start: 컨트롤 시작 시점 (0.0-1.0)
            control_guidance_end: 컨트롤 종료 시점 (0.0-1.0)

        Returns:
            생성된 이미지 리스트
        """
        # 파이프라인 로딩
        self._load_controlnet_pipeline(controlnet_type)

        # 이미지 로딩
        if isinstance(control_image, str):
            control_image = load_image(control_image)

        # 이미지 크기 조정
        control_image = control_image.resize((width, height))

        # 전처리
        preprocessor = self._get_preprocessor(controlnet_type)
        if preprocessor:
            logger.info(f"Preprocessing with {controlnet_type}...")
            control_image = preprocessor(control_image)

        logger.info(f"Generating with ControlNet ({controlnet_type})...")

        images = self.controlnet_pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            image=control_image,
            width=width,
            height=height,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            controlnet_conditioning_scale=controlnet_conditioning_scale,
            control_guidance_start=control_guidance_start,
            control_guidance_end=control_guidance_end,
        ).images

        logger.info(f"Generated {len(images)} images with ControlNet")
        return images

    async def transform_food_banner(
        self,
        food_image: Union[str, Image.Image],
        prompt: str,
        style: str = "professional",
    ) -> Image.Image:
        """
        음식 이미지를 배너 이미지로 변환

        Args:
            food_image: 원본 음식 이미지
            prompt: 추가 프롬프트
            style: 스타일 (professional, casual, elegant, vibrant)

        Returns:
            배너 이미지
        """
        enhanced_prompt = f"{prompt}, {style} food banner, commercial advertising, high-end presentation, 4k quality"
        negative = "low quality, blurry, amateur, messy, cluttered"

        images = await self.generate_with_controlnet(
            prompt=enhanced_prompt,
            control_image=food_image,
            controlnet_type="canny",
            negative_prompt=negative,
            width=1920,
            height=1080,
            guidance_scale=8.0,
            controlnet_conditioning_scale=0.6,
        )

        return images[0]

    async def transform_product_emphasis(
        self,
        product_image: Union[str, Image.Image],
        prompt: str,
    ) -> Image.Image:
        """
        제품 강조 이미지 생성

        Args:
            product_image: 원본 제품 이미지
            prompt: 추가 프롬프트

        Returns:
            제품 강조 이미지
        """
        enhanced_prompt = f"{prompt}, professional product photography, studio lighting, clean background, sharp focus, commercial quality"
        negative = "distracting background, poor lighting, blurry, low quality"

        images = await self.generate_with_controlnet(
            prompt=enhanced_prompt,
            control_image=product_image,
            controlnet_type="canny",
            negative_prompt=negative,
            width=1024,
            height=1024,
            guidance_scale=7.5,
            controlnet_conditioning_scale=0.8,
        )

        return images[0]

    async def transform_image(
        self,
        image: Union[str, Image.Image],
        prompt: str,
        negative_prompt: str = "",
        controlnet_type: str = "canny",
        strength: float = 0.7,
        guidance_scale: float = 7.5,
        num_inference_steps: int = 30,
        **kwargs
    ) -> Image.Image:
        """
        일반적인 이미지 변환 (MVP에서 사용)

        Args:
            image: 입력 이미지
            prompt: 프롬프트
            negative_prompt: 네거티브 프롬프트
            controlnet_type: ControlNet 타입
            strength: 변환 강도 (controlnet_conditioning_scale)
            guidance_scale: 가이던스 스케일
            num_inference_steps: 추론 스텝 수

        Returns:
            변환된 이미지
        """
        # kwargs에서 중복 파라미터 제거
        kwargs.pop('strength', None)
        kwargs.pop('guidance_scale', None)
        kwargs.pop('num_inference_steps', None)
        kwargs.pop('controlnet_type', None)

        images = await self.generate_with_controlnet(
            prompt=prompt,
            control_image=image,
            controlnet_type=controlnet_type,
            negative_prompt=negative_prompt,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            controlnet_conditioning_scale=strength,
            **kwargs
        )

        return images[0]

    def cleanup(self):
        """메모리 정리"""
        if self.base_pipeline:
            del self.base_pipeline
            self.base_pipeline = None

        if self.controlnet_pipeline:
            del self.controlnet_pipeline
            self.controlnet_pipeline = None

        for key in list(self.controlnet_models.keys()):
            del self.controlnet_models[key]
        self.controlnet_models.clear()

        if self.vae:
            del self.vae
            self.vae = None

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        logger.info("Pipeline memory cleaned")


# 싱글톤 인스턴스
_pipeline_instance = None


def get_image_pipeline() -> ImageTransformPipeline:
    """ImageTransformPipeline 싱글톤 인스턴스 반환"""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = ImageTransformPipeline()
    return _pipeline_instance
