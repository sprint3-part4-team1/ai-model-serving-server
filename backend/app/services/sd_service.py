"""
Stable Diffusion 이미지 생성 서비스
"""
import os
# Set HuggingFace environment variables to disable symlinks on Windows
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"

import torch
from diffusers import (
    StableDiffusionXLPipeline,
    DPMSolverMultistepScheduler,
    AutoencoderKL
)
from compel import Compel, ReturnedEmbeddingsType
import time
from typing import List, Optional, Tuple
import io
from PIL import Image
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.core.config import settings
from app.core.logging import app_logger as logger
from app.schemas.image import TextToImageRequest
from openai import OpenAI
import re


class StableDiffusionService:
    """Stable Diffusion XL 서비스"""

    def __init__(self):
        """Stable Diffusion 파이프라인 초기화"""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.float16 if settings.USE_HALF_PRECISION and torch.cuda.is_available() else torch.float32

        logger.info(f"Stable Diffusion 초기화 시작 - Device: {self.device}, dtype: {self.dtype}")

        # 초기화는 lazy loading으로 처리 (메모리 절약)
        self.pipe = None
        self.compel = None
        self.executor = ThreadPoolExecutor(max_workers=2)

        # OpenAI 클라이언트 (번역용)
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

        logger.info("Stable Diffusion 서비스 초기화 완료 (Lazy Loading)")

    def _load_model(self):
        """모델 로딩 (첫 요청 시 실행)"""
        if self.pipe is not None:
            return

        logger.info(f"Stable Diffusion XL 모델 로딩 시작: {settings.STABLE_DIFFUSION_MODEL}")

        try:
            # VAE 모델 로딩 (더 나은 이미지 품질)
            vae = AutoencoderKL.from_pretrained(
                "madebyollin/sdxl-vae-fp16-fix",
                torch_dtype=self.dtype,
                cache_dir=settings.MODEL_CACHE_DIR
            )

            # Stable Diffusion XL 파이프라인 로딩
            self.pipe = StableDiffusionXLPipeline.from_pretrained(
                settings.STABLE_DIFFUSION_MODEL,
                vae=vae,
                torch_dtype=self.dtype,
                cache_dir=settings.MODEL_CACHE_DIR,
                use_safetensors=True,
                variant="fp16" if self.dtype == torch.float16 else None
            )

            # 스케줄러 설정 (DPM-Solver++ - 빠르고 고품질)
            self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipe.scheduler.config,
                use_karras_sigmas=True,  # 더 나은 품질
                algorithm_type="dpmsolver++"
            )

            # 성능 최적화
            if self.device == "cuda":
                self.pipe = self.pipe.to(self.device)

                # xFormers 메모리 최적화 (선택사항)
                if settings.USE_XFORMERS:
                    try:
                        self.pipe.enable_xformers_memory_efficient_attention()
                        logger.info("xFormers 메모리 최적화 활성화")
                    except Exception as e:
                        logger.warning(f"xFormers 활성화 실패: {e}")

                # CPU offload (VRAM 절약)
                if settings.ENABLE_CPU_OFFLOAD:
                    self.pipe.enable_model_cpu_offload()
                    logger.info("CPU offload 활성화")

                # VAE slicing (메모리 절약)
                self.pipe.enable_vae_slicing()
                logger.info("VAE slicing 활성화")

            # Compel 프롬프트 가중치 조절기
            self.compel = Compel(
                tokenizer=[self.pipe.tokenizer, self.pipe.tokenizer_2],
                text_encoder=[self.pipe.text_encoder, self.pipe.text_encoder_2],
                returned_embeddings_type=ReturnedEmbeddingsType.PENULTIMATE_HIDDEN_STATES_NON_NORMALIZED,
                requires_pooled=[False, True]
            )

            logger.info("✅ Stable Diffusion XL 모델 로딩 완료")

        except Exception as e:
            logger.exception(f"모델 로딩 실패: {str(e)}")
            raise

    def _apply_style_preset(self, prompt: str, style: str) -> Tuple[str, str]:
        """
        스타일 프리셋 적용

        Returns:
            (enhanced_prompt, negative_prompt)
        """
        style_presets = {
            "realistic": {
                "prefix": "professional product photography, studio lighting, high quality, detailed, ",
                "suffix": ", 8k uhd, sharp focus, photorealistic",
                "negative": "cartoon, anime, illustration, painting, drawing, low quality, blurry, distorted"
            },
            "artistic": {
                "prefix": "artistic illustration, creative design, beautiful composition, ",
                "suffix": ", vibrant colors, detailed artwork, masterpiece",
                "negative": "photo, photograph, realistic, low quality, blurry"
            },
            "minimalist": {
                "prefix": "minimalist design, clean composition, simple background, ",
                "suffix": ", elegant, modern, professional",
                "negative": "cluttered, busy, complex, low quality"
            },
            "vintage": {
                "prefix": "vintage style, retro aesthetic, nostalgic feeling, ",
                "suffix": ", film grain, classic look, warm tones",
                "negative": "modern, digital, low quality, blurry"
            },
            "modern": {
                "prefix": "modern design, contemporary style, sleek and professional, ",
                "suffix": ", clean lines, high quality, polished",
                "negative": "old-fashioned, vintage, low quality"
            },
            "colorful": {
                "prefix": "vibrant colors, eye-catching design, dynamic composition, ",
                "suffix": ", colorful, energetic, high saturation, attractive",
                "negative": "monochrome, dull, faded, low quality"
            }
        }

        preset = style_presets.get(style, style_presets["realistic"])
        enhanced_prompt = preset["prefix"] + prompt + preset["suffix"]
        negative_prompt = preset["negative"]

        return enhanced_prompt, negative_prompt

    def _translate_prompt(self, prompt: str) -> str:
        """
        한글 프롬프트를 영어로 번역
        Stable Diffusion은 영어로 학습되었기 때문에 한글을 이해하지 못함

        Args:
            prompt: 원본 프롬프트 (한글 포함 가능)

        Returns:
            영어로 번역된 프롬프트
        """
        # 한글이 포함되어 있는지 확인
        korean_pattern = re.compile(r'[\u3131-\u314e\u314f-\u3163\uac00-\ud7a3]+')
        has_korean = korean_pattern.search(prompt)

        if not has_korean:
            # 한글이 없으면 그대로 반환
            return prompt

        if not self.openai_client:
            logger.warning("OpenAI client not available for translation, using original prompt")
            return prompt

        try:
            logger.info(f"한글 프롬프트 감지, 영어로 번역 중: {prompt}")

            # OpenAI로 번역
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a translator specializing in converting Korean image generation prompts to English. "
                                   "Translate the prompt naturally while preserving the visual intent and details. "
                                   "Keep it concise and suitable for AI image generation."
                    },
                    {
                        "role": "user",
                        "content": f"Translate this Korean image prompt to English: {prompt}"
                    }
                ],
                temperature=0.3,  # 낮은 temperature로 일관성 있는 번역
                max_tokens=200
            )

            translated = response.choices[0].message.content.strip()
            logger.info(f"번역 완료: {translated}")

            return translated

        except Exception as e:
            logger.error(f"프롬프트 번역 실패: {e}, 원본 사용")
            return prompt

    def _calculate_dimensions(self, aspect_ratio: str, width: Optional[int] = None, height: Optional[int] = None) -> Tuple[int, int]:
        """
        종횡비에 따라 이미지 크기 계산

        SDXL은 1024x1024 기본, 최대 2048x2048
        """
        aspect_ratios = {
            "1:1": (1024, 1024),
            "4:5": (896, 1152),  # Instagram portrait
            "16:9": (1344, 768),  # Landscape
            "21:9": (1536, 640),  # Wide banner
        }

        if width and height:
            # 커스텀 크기 (8의 배수로 조정)
            width = (width // 8) * 8
            height = (height // 8) * 8
            return min(width, settings.MAX_IMAGE_WIDTH), min(height, settings.MAX_IMAGE_HEIGHT)

        return aspect_ratios.get(aspect_ratio, (1024, 1024))

    def _generate_single_image(
        self,
        prompt: str,
        negative_prompt: str,
        width: int,
        height: int,
        num_inference_steps: int,
        guidance_scale: float,
        seed: Optional[int] = None
    ) -> Image.Image:
        """단일 이미지 생성 (동기 함수 - ThreadPoolExecutor에서 실행)"""

        # 모델 로딩 (lazy loading)
        self._load_model()

        # Compel을 사용한 프롬프트 임베딩 생성
        conditioning, pooled = self.compel(prompt)
        negative_conditioning, negative_pooled = self.compel(negative_prompt)

        # Generator 설정 (재현성)
        generator = None
        if seed is not None:
            generator = torch.Generator(device=self.device).manual_seed(seed)
        else:
            # 랜덤 시드
            import random
            seed = random.randint(0, 2**32 - 1)
            generator = torch.Generator(device=self.device).manual_seed(seed)

        logger.info(f"이미지 생성 시작 - Size: {width}x{height}, Steps: {num_inference_steps}, Seed: {seed}")

        # 이미지 생성
        with torch.inference_mode():
            result = self.pipe(
                prompt_embeds=conditioning,
                pooled_prompt_embeds=pooled,
                negative_prompt_embeds=negative_conditioning,
                negative_pooled_prompt_embeds=negative_pooled,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator,
            )

        image = result.images[0]
        logger.info(f"이미지 생성 완료 - Seed: {seed}")

        return image

    async def generate_text_to_image(self, request: TextToImageRequest) -> Tuple[List[Image.Image], float, dict]:
        """
        텍스트→이미지 생성

        Returns:
            (images, generation_time, parameters)
        """
        start_time = time.time()

        try:
            logger.info(f"텍스트→이미지 생성 요청: {request.prompt[:100]}...")

            # 한글 프롬프트 영어로 번역
            translated_prompt = self._translate_prompt(request.prompt)

            # 프롬프트 개선
            enhanced_prompt, style_negative = self._apply_style_preset(
                translated_prompt,
                request.style.value if request.style else "realistic"
            )

            # 네거티브 프롬프트 결합
            negative_prompt = request.negative_prompt
            if style_negative:
                negative_prompt = f"{negative_prompt}, {style_negative}"

            # 이미지 크기 계산
            width, height = self._calculate_dimensions(
                request.aspect_ratio.value,
                request.width,
                request.height
            )

            # 파라미터 제한
            num_inference_steps = min(request.num_inference_steps, settings.MAX_NUM_INFERENCE_STEPS)

            logger.info(f"생성 설정 - Prompt: {enhanced_prompt[:100]}")
            logger.info(f"Size: {width}x{height}, Steps: {num_inference_steps}, Guidance: {request.guidance_scale}")

            # 여러 이미지 생성 (병렬 처리)
            images = []
            tasks = []

            for i in range(request.num_images):
                seed = request.seed + i if request.seed is not None else None

                # ThreadPoolExecutor로 동기 함수 비동기 실행
                task = asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self._generate_single_image,
                    enhanced_prompt,
                    negative_prompt,
                    width,
                    height,
                    num_inference_steps,
                    request.guidance_scale,
                    seed
                )
                tasks.append(task)

            # 모든 이미지 생성 완료 대기
            images = await asyncio.gather(*tasks)

            generation_time = time.time() - start_time

            parameters = {
                "prompt": enhanced_prompt,
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": request.guidance_scale,
                "style": request.style.value if request.style else None,
                "seed": request.seed
            }

            logger.info(f"✅ 텍스트→이미지 생성 완료 - {len(images)}개, {generation_time:.2f}초")

            return images, generation_time, parameters

        except Exception as e:
            logger.exception(f"이미지 생성 실패: {str(e)}")
            raise


# 전역 서비스 인스턴스
sd_service = StableDiffusionService()
