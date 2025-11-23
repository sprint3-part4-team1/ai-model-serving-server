"""
한글 프롬프트 번역 및 최적화 서비스
OpenAI GPT-4를 사용하여 한글 프롬프트를 Stable Diffusion에 최적화된 영어 프롬프트로 변환
"""
import re
from typing import Optional, Dict
from functools import lru_cache
from openai import AsyncOpenAI
from loguru import logger

from backend.config.settings import settings


class KoreanPromptTranslator:
    """한글 프롬프트를 영어로 번역하고 Stable Diffusion에 최적화"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.cache: Dict[str, str] = {}

    def is_korean(self, text: str) -> bool:
        """텍스트에 한글이 포함되어 있는지 확인"""
        return bool(re.search(r'[가-힣]', text))

    async def translate(
        self,
        prompt: str,
        context: str = "food",
        style: Optional[str] = None
    ) -> str:
        """
        한글 프롬프트를 영어로 번역 및 최적화

        Args:
            prompt: 한글 또는 영어 프롬프트
            context: 이미지 맥락 ("food", "product", "banner" 등)
            style: 추가 스타일 지시 (optional)

        Returns:
            Stable Diffusion에 최적화된 영어 프롬프트
        """
        # 영어만 있으면 바로 반환
        if not self.is_korean(prompt):
            logger.info("No Korean detected, returning original prompt")
            return prompt

        # 캐시 확인
        cache_key = f"{prompt}:{context}:{style}"
        if cache_key in self.cache:
            logger.info("Returning cached translation")
            return self.cache[cache_key]

        logger.info(f"Translating Korean prompt: {prompt[:50]}...")

        try:
            # GPT-4를 사용한 번역 및 최적화
            system_prompt = self._build_system_prompt(context, style)

            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # 일관성을 위해 낮은 temperature
                max_tokens=500
            )

            translated = response.choices[0].message.content.strip()

            # 캐시 저장
            self.cache[cache_key] = translated

            logger.info(f"Translation successful: {translated[:50]}...")
            return translated

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            # 실패 시 원본 반환
            return prompt

    def _build_system_prompt(self, context: str, style: Optional[str]) -> str:
        """번역 시스템 프롬프트 생성"""

        base_prompt = """당신은 한글 프롬프트를 Stable Diffusion XL에 최적화된 영어 프롬프트로 변환하는 전문가입니다.

### 변환 규칙:
1. **구체적이고 디테일한 표현 사용**
   - "예쁘게" → "beautiful, elegant, visually appealing"
   - "맛있게" → "appetizing, delicious-looking, mouth-watering"

2. **전문 용어 활용**
   - 촬영: "professional food photography, studio lighting"
   - 배경: "bokeh background, depth of field"
   - 품질: "high resolution, sharp focus, detailed"

3. **Stable Diffusion 키워드 포함**
   - 품질: "masterpiece, best quality, highly detailed"
   - 스타일: "photorealistic, 8k, professional"
   - 조명: "natural lighting, soft shadows, golden hour"

4. **불필요한 단어 제거**
   - 조사, 접속사 제거
   - 핵심 키워드만 추출

5. **쉼표로 구분된 키워드 형식**
   - 올바른 예: "food photography, delicious pizza, wooden table, natural lighting"
"""

        # Context별 추가 지시사항
        context_prompts = {
            "food": """
### 음식 이미지 특화:
- 음식의 종류를 명확히 표현
- 조리 상태, 플레이팅 스타일 포함
- 배경, 테이블 세팅 디테일
- 색감, 질감, 신선도 강조
- "food photography, professional plating, appetizing" 등 키워드 포함

예시:
입력: "맛있어 보이는 비빔밥 사진, 고급 레스토랑 느낌"
출력: "appetizing bibimbap in stone bowl, professional food photography, fine dining restaurant ambiance, colorful vegetables, perfectly plated, elegant table setting, natural lighting, shallow depth of field, 8k, highly detailed"
""",
            "product": """
### 제품 이미지 특화:
- 제품의 특징 강조
- 스튜디오 촬영 스타일
- 클린한 배경
- "product photography, commercial shot, studio lighting" 등 키워드 포함
""",
            "banner": """
### 배너 이미지 특화:
- 와이드 구도
- 마케팅 목적 강조
- 시각적 임팩트
- "hero shot, marketing banner, wide angle, eye-catching" 등 키워드 포함
"""
        }

        prompt = base_prompt + context_prompts.get(context, context_prompts["food"])

        # 스타일 추가
        if style:
            prompt += f"\n\n### 추가 스타일 지시:\n{style}"

        prompt += "\n\n### 출력 형식:\n영어 프롬프트만 출력하세요. 설명이나 부가 텍스트는 포함하지 마세요."

        return prompt

    async def optimize_prompt(
        self,
        prompt: str,
        add_quality: bool = True,
        add_style: bool = True
    ) -> str:
        """
        프롬프트에 품질 및 스타일 키워드 추가

        Args:
            prompt: 기본 프롬프트
            add_quality: 품질 키워드 추가 여부
            add_style: 스타일 키워드 추가 여부

        Returns:
            최적화된 프롬프트
        """
        parts = [prompt]

        if add_quality:
            quality_keywords = [
                "masterpiece",
                "best quality",
                "highly detailed",
                "8k",
                "sharp focus"
            ]
            parts.extend(quality_keywords)

        if add_style:
            style_keywords = [
                "professional photography",
                "photorealistic",
                "natural lighting"
            ]
            parts.extend(style_keywords)

        return ", ".join(parts)

    async def translate_batch(
        self,
        prompts: list[str],
        context: str = "food"
    ) -> list[str]:
        """
        여러 프롬프트를 배치로 번역

        Args:
            prompts: 프롬프트 리스트
            context: 이미지 맥락

        Returns:
            번역된 프롬프트 리스트
        """
        import asyncio
        tasks = [self.translate(p, context) for p in prompts]
        return await asyncio.gather(*tasks)

    def clear_cache(self):
        """번역 캐시 초기화"""
        self.cache.clear()
        logger.info("Translation cache cleared")

    def get_cache_size(self) -> int:
        """캐시 크기 반환"""
        return len(self.cache)


# 싱글톤 인스턴스
_translator_instance: Optional[KoreanPromptTranslator] = None


def get_korean_translator() -> KoreanPromptTranslator:
    """KoreanPromptTranslator 싱글톤 인스턴스 반환"""
    global _translator_instance
    if _translator_instance is None:
        _translator_instance = KoreanPromptTranslator()
    return _translator_instance


# 편의 함수
async def translate_to_english(
    prompt: str,
    context: str = "food",
    optimize: bool = True
) -> str:
    """
    한글 프롬프트를 영어로 번역하는 편의 함수

    Args:
        prompt: 한글 또는 영어 프롬프트
        context: 이미지 맥락
        optimize: 품질 키워드 자동 추가 여부

    Returns:
        번역 및 최적화된 영어 프롬프트
    """
    translator = get_korean_translator()
    translated = await translator.translate(prompt, context)

    if optimize:
        translated = await translator.optimize_prompt(translated)

    return translated


# 테스트용
if __name__ == "__main__":
    import asyncio

    async def test():
        translator = KoreanPromptTranslator()

        # 테스트 케이스
        test_prompts = [
            "맛있어 보이는 비빔밥 사진",
            "고급 레스토랑의 스테이크, 와인 한 잔과 함께",
            "카페 감성의 라떼 아트",
            "흑백 사진을 컬러로 복원",
            "배경을 깔끔한 흰색으로 변경",
        ]

        print("=== 한글 프롬프트 번역 테스트 ===\n")

        for prompt in test_prompts:
            print(f"입력: {prompt}")
            translated = await translator.translate(prompt, context="food")
            print(f"출력: {translated}")
            print("-" * 80)

    asyncio.run(test())
