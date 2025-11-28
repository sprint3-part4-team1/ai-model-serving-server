"""
MVP 음식 이미지 변환 통합 파이프라인
한글 지원 + 옵션 기반 변환 + U2-Net + SDXL + ControlNet
"""
import torch
import asyncio
from PIL import Image
from typing import Optional, Dict, Any
from loguru import logger
from pathlib import Path
import time

from backend.services.korean_translator import get_korean_translator
from backend.services.u2net_service import get_background_remover
from backend.services.image_transform_pipeline import get_image_pipeline
from backend.config.food_presets import (
    PromptBuilder,
    PURPOSE_PRESETS,
    STYLE_PRESETS,
    BACKGROUND_PRESETS
)
from backend.config.settings import settings


class MVPFoodPipeline:
    """
    MVP 음식 이미지 변환 파이프라인

    특징:
    - 한글 프롬프트 지원
    - 옵션 기반 간편 사용
    - 고품질 배경 처리
    - 음식 이미지 특화
    """

    def __init__(self, use_u2net: bool = False):
        """
        Args:
            use_u2net: True면 U2-Net 사용, False면 rembg 사용 (더 빠름)
        """
        self.translator = get_korean_translator()
        self.background_remover = get_background_remover(use_u2net=use_u2net)
        self.image_pipeline = get_image_pipeline()
        self.prompt_builder = PromptBuilder()

        logger.info("MVPFoodPipeline initialized")

    async def transform(
        self,
        image: Image.Image,
        purpose: str = "product_emphasis",
        style: str = "natural",
        background: str = "original",
        food_name: str = "delicious food",
        additional_prompt: str = "",
        **kwargs
    ) -> Dict[str, Any]:
        """
        음식 이미지 변환 (옵션 기반)

        Args:
            image: 입력 이미지
            purpose: 변환 목적 (banner_web, banner_sns, product_emphasis 등)
            style: 스타일 (natural, luxury, cafe, vintage, bright, rustic)
            background: 배경 (original, white, wood, marble, outdoor, remove, bokeh)
            food_name: 음식 이름 (한글/영어 모두 가능)
            additional_prompt: 추가 프롬프트 (한글/영어 모두 가능)
            **kwargs: 추가 파라미터

        Returns:
            {
                "image": 변환된 이미지,
                "prompt_used": 사용된 프롬프트,
                "processing_time": 처리 시간,
                "config": 사용된 설정
            }
        """
        start_time = time.time()
        logger.info(f"Starting MVP transform: purpose={purpose}, style={style}, background={background}")

        try:
            # ===== 1. 한글→영어 번역 =====
            if self.translator.is_korean(food_name):
                logger.info("Translating food name to English...")
                food_name = await self.translator.translate(
                    food_name,
                    context="food"
                )

            if additional_prompt and self.translator.is_korean(additional_prompt):
                logger.info("Translating additional prompt to English...")
                additional_prompt = await self.translator.translate(
                    additional_prompt,
                    context="food",
                    style=style
                )

            # ===== 2. 프롬프트 생성 (옵션 기반) =====
            positive_prompt, negative_prompt = self.prompt_builder.build_prompt(
                purpose=purpose,
                style=style,
                background=background,
                food_name=food_name,
                additional_prompt=additional_prompt
            )

            logger.info(f"Generated prompt: {positive_prompt[:100]}...")

            # ===== 3. 프리셋 설정 로드 =====
            preset_config = self.prompt_builder.get_preset_config(purpose)

            # kwargs에서 오버라이드할 값 가져오기 (디버깅)
            logger.info(f"kwargs before pop: {kwargs}")
            override_strength = kwargs.pop('strength', None)
            override_steps = kwargs.pop('num_inference_steps', None)
            logger.info(f"override_strength: {override_strength}, override_steps: {override_steps}")
            logger.info(f"kwargs after pop: {kwargs}")

            # 프리셋 값 오버라이드
            if override_strength is not None:
                preset_config.strength = override_strength
            if override_steps is not None:
                preset_config.num_inference_steps = override_steps

            # ===== 4. 배경 처리 =====
            processed_image = image
            removed_bg = False

            if self.prompt_builder.should_remove_background(background):
                logger.info("Removing background...")

                if self.prompt_builder.is_transparent_background(background):
                    # 투명 배경
                    processed_image = await self.background_remover.remove_background(image)
                    removed_bg = True
                else:
                    # 단색 배경
                    solid_color = self.prompt_builder.get_solid_color(background)
                    if solid_color:
                        processed_image = await self.background_remover.create_solid_background(
                            image,
                            color=solid_color
                        )
                        removed_bg = True

            # ===== 5. 이미지 생성 (SDXL + ControlNet) =====
            if not removed_bg or background != "remove":
                logger.info("Generating image with SDXL + ControlNet...")

                # ControlNet 타입
                controlnet_type = preset_config.controlnet_type

                # Canny 전처리 이미지 생성 (디버깅용)
                canny_image = None
                if controlnet_type == "canny":
                    from controlnet_aux import CannyDetector
                    canny_detector = CannyDetector()
                    canny_image = canny_detector(processed_image)
                    logger.info("Canny edge detection completed")

                # 이미지 생성 (kwargs는 이미 위에서 strength, num_inference_steps 제거됨)
                generated_image = await self.image_pipeline.transform_image(
                    image=processed_image,
                    prompt=positive_prompt,
                    negative_prompt=negative_prompt,
                    controlnet_type=controlnet_type,
                    strength=preset_config.strength,
                    guidance_scale=preset_config.guidance_scale,
                    num_inference_steps=preset_config.num_inference_steps,
                    **kwargs
                )

                result_image = generated_image
            else:
                # 배경 제거만 수행
                result_image = processed_image

            # ===== 6. 후처리 (리사이즈) =====
            target_size = preset_config.size
            if result_image.size != target_size:
                logger.info(f"Resizing to {target_size}...")
                result_image = result_image.resize(target_size, Image.Resampling.LANCZOS)

            # ===== 완료 =====
            processing_time = time.time() - start_time
            logger.info(f"Transform completed in {processing_time:.2f}s")

            return {
                "image": result_image,
                "canny_image": canny_image if 'canny_image' in locals() else None,
                "prompt_used": positive_prompt,
                "negative_prompt_used": negative_prompt,
                "processing_time": processing_time,
                "config": {
                    "purpose": purpose,
                    "style": style,
                    "background": background,
                    "controlnet_type": controlnet_type,
                    "strength": preset_config.strength,
                    "guidance_scale": preset_config.guidance_scale,
                    "num_inference_steps": preset_config.num_inference_steps,
                    "size": target_size
                }
            }

        except Exception as e:
            logger.error(f"Transform failed: {e}", exc_info=True)
            raise

    async def batch_transform(
        self,
        images: list[Image.Image],
        **kwargs
    ) -> list[Dict[str, Any]]:
        """
        배치 변환

        Args:
            images: 이미지 리스트
            **kwargs: transform 파라미터

        Returns:
            변환 결과 리스트
        """
        logger.info(f"Starting batch transform for {len(images)} images")

        tasks = [self.transform(img, **kwargs) for img in images]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 에러 처리
        successful = []
        failed = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Image {i} failed: {result}")
                failed.append((i, result))
            else:
                successful.append(result)

        logger.info(f"Batch transform completed: {len(successful)} succeeded, {len(failed)} failed")

        return successful

    def get_available_options(self) -> Dict[str, list]:
        """
        사용 가능한 옵션 목록 반환

        Returns:
            {
                "purposes": [...],
                "styles": [...],
                "backgrounds": [...]
            }
        """
        return {
            "purposes": [
                {
                    "id": key,
                    "name": preset.name,
                    "description": preset.description
                }
                for key, preset in PURPOSE_PRESETS.items()
            ],
            "styles": [
                {
                    "id": key,
                    "name": data["name"],
                    "description": data["description"]
                }
                for key, data in STYLE_PRESETS.items()
            ],
            "backgrounds": [
                {
                    "id": key,
                    "name": data["name"],
                    "description": data["description"]
                }
                for key, data in BACKGROUND_PRESETS.items()
            ]
        }

    async def quick_enhance(
        self,
        image: Image.Image,
        enhancement_type: str = "appetizing"
    ) -> Image.Image:
        """
        빠른 개선 (자주 사용하는 프리셋)

        Args:
            image: 입력 이미지
            enhancement_type: "appetizing", "professional", "bright"

        Returns:
            개선된 이미지
        """
        presets = {
            "appetizing": {
                "purpose": "color_correction",
                "style": "bright",
                "food_name": "appetizing food"
            },
            "professional": {
                "purpose": "product_emphasis",
                "style": "luxury",
                "food_name": "professional food shot"
            },
            "bright": {
                "purpose": "color_correction",
                "style": "bright",
                "food_name": "bright and fresh food"
            }
        }

        preset = presets.get(enhancement_type, presets["appetizing"])
        result = await self.transform(image, **preset)
        return result["image"]


# 싱글톤 인스턴스
_pipeline_instance: Optional[MVPFoodPipeline] = None


def get_mvp_pipeline(use_u2net: bool = False) -> MVPFoodPipeline:
    """MVPFoodPipeline 싱글톤 인스턴스 반환"""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = MVPFoodPipeline(use_u2net=use_u2net)
    return _pipeline_instance


# 편의 함수
async def transform_food_image(
    image: Image.Image,
    purpose: str = "product_emphasis",
    style: str = "natural",
    background: str = "original",
    food_name: str = "delicious food",
    additional_prompt: str = ""
) -> Image.Image:
    """음식 이미지 변환 편의 함수"""
    pipeline = get_mvp_pipeline()
    result = await pipeline.transform(
        image=image,
        purpose=purpose,
        style=style,
        background=background,
        food_name=food_name,
        additional_prompt=additional_prompt
    )
    return result["image"]


# 테스트용
if __name__ == "__main__":
    async def test():
        pipeline = MVPFoodPipeline(use_u2net=False)

        # 테스트 이미지
        test_image = Image.open("test_food.jpg")

        print("=== MVP 파이프라인 테스트 ===\n")

        # 테스트 케이스 1: 한글 프롬프트
        print("1. 한글 프롬프트 테스트")
        result = await pipeline.transform(
            image=test_image,
            purpose="product_emphasis",
            style="luxury",
            background="white",
            food_name="맛있는 비빔밥",
            additional_prompt="더 먹음직스럽게 만들어주세요"
        )
        result["image"].save("test_result_1.png")
        print(f"완료: test_result_1.png")
        print(f"처리 시간: {result['processing_time']:.2f}s")
        print(f"사용된 프롬프트: {result['prompt_used'][:100]}...\n")

        # 테스트 케이스 2: 배너 생성
        print("2. 배너 이미지 생성")
        result = await pipeline.transform(
            image=test_image,
            purpose="banner_web",
            style="cafe",
            background="wood",
            food_name="latte with beautiful latte art"
        )
        result["image"].save("test_result_2.png")
        print(f"완료: test_result_2.png")
        print(f"크기: {result['image'].size}\n")

        # 테스트 케이스 3: 배경 제거
        print("3. 배경 제거")
        result = await pipeline.transform(
            image=test_image,
            purpose="product_emphasis",
            style="natural",
            background="remove",
            food_name="food"
        )
        result["image"].save("test_result_3.png")
        print(f"완료: test_result_3.png (투명 배경)\n")

        # 옵션 목록 출력
        print("4. 사용 가능한 옵션")
        options = pipeline.get_available_options()
        print(f"목적: {len(options['purposes'])}개")
        print(f"스타일: {len(options['styles'])}개")
        print(f"배경: {len(options['backgrounds'])}개")

    asyncio.run(test())
