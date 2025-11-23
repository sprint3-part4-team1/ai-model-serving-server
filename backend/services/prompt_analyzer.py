"""
프롬프트 분석 및 이해 서비스
OpenAI GPT-4를 사용하여 사용자의 자연어 프롬프트를 분석하고
적절한 이미지 변환 파이프라인을 결정
"""
import json
from typing import Dict, List, Optional, Literal
from openai import AsyncOpenAI
from loguru import logger
from backend.config.settings import settings


class PromptAnalyzer:
    """프롬프트 분석 및 의도 파악"""

    TRANSFORMATION_TYPES = [
        "background_change",  # 배경 변경
        "style_transfer",  # 스타일 변환
        "color_change",  # 색상 변경
        "add_elements",  # 요소 추가
        "product_emphasis",  # 제품 강조
        "ingredient_label",  # 성분표 생성
        "banner_creation",  # 배너 이미지
        "menu_design",  # 메뉴판 디자인
        "social_media",  # SNS용 이미지
        "package_design",  # 패키지 디자인
    ]

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def analyze_prompt(
        self,
        prompt: str,
        image_description: Optional[str] = None
    ) -> Dict:
        """
        프롬프트를 분석하여 변환 의도와 파라미터 추출

        Returns:
            {
                "transformation_type": str,
                "target_style": str,
                "elements_to_preserve": List[str],
                "elements_to_add": List[str],
                "color_scheme": Optional[str],
                "mood": str,
                "technical_params": {
                    "controlnet_type": str,
                    "strength": float,
                    "guidance_scale": float
                }
            }
        """
        system_prompt = """당신은 이미지 변환 AI의 프롬프트 분석 전문가입니다.
사용자의 자연어 요청을 분석하여 다음 정보를 JSON 형식으로 추출하세요:

1. transformation_type: 변환 유형 (background_change, style_transfer, color_change, add_elements,
   product_emphasis, ingredient_label, banner_creation, menu_design, social_media, package_design)
2. target_style: 목표 스타일 (realistic, artistic, minimalist, vintage, modern, colorful, professional)
3. elements_to_preserve: 보존할 요소들 (예: ["제품", "음식", "접시"])
4. elements_to_add: 추가할 요소들 (예: ["로고", "텍스트", "장식"])
5. color_scheme: 색상 테마 (warm, cool, vibrant, pastel, monochrome, null)
6. mood: 분위기 (appetizing, elegant, casual, festive, healthy, premium)
7. technical_params:
   - controlnet_type: canny, depth, openpose, mlsd, normal, segment 중 선택
   - strength: 0.3-1.0 (원본 보존도)
   - guidance_scale: 7.0-15.0 (프롬프트 충실도)
   - use_ip_adapter: true/false (스타일 참조 필요 여부)

음식 이미지에 특화된 분석을 수행하세요."""

        user_prompt = f"""프롬프트: {prompt}"""
        if image_description:
            user_prompt += f"\n\n현재 이미지: {image_description}"

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            analysis = json.loads(response.choices[0].message.content)
            logger.info(f"Prompt analysis: {analysis}")
            return analysis

        except Exception as e:
            logger.error(f"Prompt analysis failed: {e}")
            # 기본값 반환
            return self._get_default_analysis()

    async def analyze_image(self, image_path: str) -> str:
        """
        GPT-4 Vision을 사용하여 이미지 내용 분석

        Returns:
            이미지 설명 텍스트
        """
        try:
            import base64
            from pathlib import Path

            # 이미지를 base64로 인코딩
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode()

            response = await self.client.chat.completions.create(
                model=settings.OPENAI_VISION_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """이 음식 이미지를 분석하세요. 다음을 포함하여 설명해주세요:
1. 음식 종류와 주요 재료
2. 색상과 질감
3. 플레이팅과 구성
4. 배경과 분위기
5. 조명과 스타일"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )

            description = response.choices[0].message.content
            logger.info(f"Image analysis: {description[:100]}...")
            return description

        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return "이미지 분석 실패"

    def _get_default_analysis(self) -> Dict:
        """기본 분석 결과 반환"""
        return {
            "transformation_type": "product_emphasis",
            "target_style": "realistic",
            "elements_to_preserve": ["food", "product"],
            "elements_to_add": [],
            "color_scheme": None,
            "mood": "appetizing",
            "technical_params": {
                "controlnet_type": "canny",
                "strength": 0.7,
                "guidance_scale": 7.5,
                "use_ip_adapter": False
            }
        }

    async def generate_enhanced_prompt(
        self,
        original_prompt: str,
        analysis: Dict,
        image_description: Optional[str] = None
    ) -> Dict[str, str]:
        """
        분석 결과를 바탕으로 향상된 프롬프트 생성

        Returns:
            {
                "positive_prompt": str,
                "negative_prompt": str
            }
        """
        transformation_type = analysis.get("transformation_type", "product_emphasis")
        target_style = analysis.get("target_style", "realistic")
        mood = analysis.get("mood", "appetizing")

        # 변환 타입별 프롬프트 템플릿
        templates = {
            "banner_creation": {
                "positive": "professional food photography banner, commercial advertising style, high-end presentation, clean layout, eye-catching composition, {style}, {mood} atmosphere, 4k quality, marketing material",
                "negative": "blurry, low quality, amateur, messy, cluttered, unprofessional"
            },
            "product_emphasis": {
                "positive": "studio product photography, clean white background, professional lighting, sharp focus on food, appetizing presentation, {style} style, commercial quality, high resolution",
                "negative": "distracting background, poor lighting, blurry, unappetizing, low quality"
            },
            "ingredient_label": {
                "positive": "clean ingredient label design, nutritional information display, modern typography, professional layout, {style}, clear and readable, infographic style",
                "negative": "cluttered, hard to read, unprofessional, messy layout"
            },
            "menu_design": {
                "positive": "restaurant menu design, food photography, elegant typography, professional layout, {style}, appetizing presentation, commercial quality",
                "negative": "cheap looking, amateur, cluttered, hard to read"
            },
            "social_media": {
                "positive": "instagram-worthy food photography, trendy aesthetic, vibrant colors, {style} style, social media optimized, eye-catching, engaging composition",
                "negative": "boring, unappealing, low engagement, poor composition"
            },
            "style_transfer": {
                "positive": "artistic food photography, {style} style, creative interpretation, {mood} mood, professional quality, unique presentation",
                "negative": "generic, boring, low quality, unappealing"
            }
        }

        template = templates.get(transformation_type, templates["product_emphasis"])

        positive = template["positive"].format(style=target_style, mood=mood)
        negative = template["negative"]

        # 원본 프롬프트 통합
        if original_prompt:
            positive = f"{original_prompt}, {positive}"

        # 이미지 설명 추가
        if image_description:
            positive = f"{image_description}, {positive}"

        return {
            "positive_prompt": positive,
            "negative_prompt": negative
        }


# 싱글톤 인스턴스
_analyzer_instance = None


def get_prompt_analyzer() -> PromptAnalyzer:
    """PromptAnalyzer 싱글톤 인스턴스 반환"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = PromptAnalyzer()
    return _analyzer_instance
