"""
Story Generator Service
컨텍스트 정보를 기반으로 감성적인 스토리 문구를 생성하는 서비스
"""

import os
from typing import Dict, List, Optional
from openai import OpenAI
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from logger import app_logger as logger
from config import settings


class StoryGeneratorService:
    """스토리 생성 서비스 (LLM 기반)"""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.model = "gpt-3.5-turbo"  # 비용 효율적인 모델

    def generate_story(
        self,
        context: Dict,
        store_name: Optional[str] = None,
        store_type: Optional[str] = "카페",
        menu_categories: Optional[List[str]] = None
    ) -> str:
        """
        컨텍스트 기반 스토리 문구 생성

        Args:
            context: Context Collector에서 수집한 정보
            store_name: 매장 이름
            store_type: 매장 타입 (카페, 레스토랑 등)
            menu_categories: 메뉴 카테고리 리스트

        Returns:
            생성된 스토리 문구 (1-2문장)
        """
        if not self.client:
            logger.warning("OpenAI client not initialized, returning mock story")
            return self._generate_mock_story(context, store_type)

        try:
            # Prompt 생성
            prompt = self._build_prompt(context, store_name, store_type, menu_categories)

            logger.info(f"Generating story with prompt: {prompt[:100]}...")

            # GPT API 호출
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 창의적인 카페/레스토랑 마케팅 전문가입니다. "
                                   "고객의 마음을 사로잡는 감성적이고 자연스러운 추천 문구를 작성합니다."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=150,
                temperature=0.8,  # 창의성을 높임
                top_p=0.9,
                presence_penalty=0.6,
                frequency_penalty=0.3
            )

            story = response.choices[0].message.content.strip()
            logger.info(f"Story generated successfully: {story}")

            return story

        except Exception as e:
            logger.error(f"Failed to generate story with GPT: {e}")
            return self._generate_mock_story(context, store_type)

    def generate_multiple_stories(
        self,
        context: Dict,
        store_name: Optional[str] = None,
        store_type: Optional[str] = "카페",
        menu_categories: Optional[List[str]] = None,
        count: int = 3
    ) -> List[str]:
        """
        여러 버전의 스토리 생성 (A/B 테스트용)

        Args:
            context: Context Collector에서 수집한 정보
            store_name: 매장 이름
            store_type: 매장 타입
            menu_categories: 메뉴 카테고리
            count: 생성할 스토리 개수

        Returns:
            스토리 리스트
        """
        stories = []

        for i in range(count):
            try:
                story = self.generate_story(
                    context=context,
                    store_name=store_name,
                    store_type=store_type,
                    menu_categories=menu_categories
                )
                stories.append(story)
                logger.info(f"Generated story variant {i+1}/{count}")

            except Exception as e:
                logger.error(f"Failed to generate story variant {i+1}: {e}")
                stories.append(self._generate_mock_story(context, store_type))

        return stories

    def _build_prompt(
        self,
        context: Dict,
        store_name: Optional[str],
        store_type: str,
        menu_categories: Optional[List[str]]
    ) -> str:
        """
        GPT 프롬프트 생성

        Args:
            context: 컨텍스트 정보
            store_name: 매장 이름
            store_type: 매장 타입
            menu_categories: 메뉴 카테고리

        Returns:
            생성된 프롬프트
        """
        weather = context.get("weather", {})
        time_info = context.get("time_info", {})
        season = context.get("season", "")
        trends = context.get("trends", [])

        # 날씨 정보
        weather_desc = weather.get("description", "맑음")
        temperature = weather.get("temperature", 15)

        # 시간대 정보
        period_kr = time_info.get("period_kr", "오후")
        time_str = time_info.get("time_str", "")

        # 계절 정보
        season_map = {
            "spring": "봄",
            "summer": "여름",
            "autumn": "가을",
            "winter": "겨울"
        }
        season_kr = season_map.get(season, "")

        # 트렌드 정보
        trend_str = ", ".join(trends[:3]) if trends else ""

        # 메뉴 카테고리
        menu_str = ", ".join(menu_categories) if menu_categories else "음료"

        # 브랜드 톤앤매너 (매장 타입별 차별화)
        tone_guide = {
            "카페": "친근하고 따뜻한 톤 (예: ~어떠세요?, ~해보세요)",
            "레스토랑": "품격있고 전문적인 톤 (예: ~어떻습니까?, ~만들어보세요)",
            "디저트": "발랄하고 달콤한 톤 (예: ~즐겨봐요!, ~느껴보세요)",
            "술집": "편안하고 캐주얼한 톤 (예: ~어때요?, ~함께해요)"
        }.get(store_type, "친근하고 자연스러운 톤")

        # 트렌드가 있을 경우 강조
        trend_instruction = ""
        if trend_str:
            trend_instruction = f"""
**🔥 트렌드 활용 (필수):**
- 현재 인기 키워드: {trend_str}
- 위 트렌드 중 1-2개를 자연스럽게 문구에 녹여내세요
- 억지로 끼워넣지 말고, 맥락에 맞게 활용
- 예: "요즘 인기인 {trends[0]}와 함께 {menu_str} 어떠세요?"
"""

        prompt = f"""다음 정보를 바탕으로 고객의 마음을 사로잡는 감성적인 추천 문구를 1-2문장으로 작성해주세요.

**매장 정보:**
- 매장 이름: {store_name or store_type}
- 매장 타입: {store_type}
- 주요 메뉴: {menu_str}
- 브랜드 톤: {tone_guide}

**현재 상황:**
- 날씨: {weather_desc}, 온도 {temperature}도
- 계절: {season_kr}
- 시간대: {period_kr} ({time_str})
{trend_instruction}

**작성 가이드:**
1. {tone_guide}로 작성
2. 현재 날씨, 계절, 시간대를 자연스럽게 녹여내기
3. 트렌드 키워드가 있다면 1-2개 반드시 활용 (자연스럽게)
4. 구체적인 메뉴를 언급하여 구매 욕구 자극
5. 1-2문장으로 간결하게 (최대 60자)
6. 이모지는 사용하지 말 것

예시:
- "비 오는 가을 오후, 따뜻한 아메리카노 한 잔과 함께 여유를 느껴보세요."
- "쌀쌀한 겨울 아침, 달콤한 카페모카로 하루를 시작하는 건 어떠세요?"
- "더운 여름 점심, 시원한 아이스 음료로 더위를 날려보세요."
- "요즘 핫한 딸기 시즌, 신선한 딸기 디저트로 달콤한 오후 시간 만들어보세요."

문구:"""

        return prompt

    def _generate_mock_story(self, context: Dict, store_type: str = "카페") -> str:
        """
        Mock 스토리 생성 (GPT 사용 불가 시)

        Args:
            context: 컨텍스트 정보
            store_type: 매장 타입

        Returns:
            Mock 스토리 문구
        """
        weather = context.get("weather", {})
        time_info = context.get("time_info", {})
        season = context.get("season", "")

        weather_desc = weather.get("description", "맑음")
        temperature = weather.get("temperature", 15)
        period_kr = time_info.get("period_kr", "오후")

        season_map = {
            "spring": "봄",
            "summer": "여름",
            "autumn": "가을",
            "winter": "겨울"
        }
        season_kr = season_map.get(season, "")

        # 간단한 템플릿 기반 생성
        templates = [
            f"{weather_desc} {season_kr} {period_kr}, 따뜻한 음료 한 잔 어떠세요?",
            f"{temperature}도의 {season_kr} 날씨, {store_type}에서 여유를 즐겨보세요.",
            f"{period_kr}의 특별한 순간, 맛있는 메뉴와 함께하세요."
        ]

        import random
        story = random.choice(templates)

        logger.info(f"Mock story generated: {story}")
        return story

    def generate_menu_storytelling(
        self,
        menu_name: str,
        ingredients: List[str],
        origin: Optional[str] = None,
        history: Optional[str] = None
    ) -> str:
        """
        메뉴 클릭 시 보여줄 스토리텔링 생성

        Args:
            menu_name: 메뉴 이름
            ingredients: 재료 리스트
            origin: 원산지
            history: 메뉴 역사

        Returns:
            메뉴 스토리텔링 문구
        """
        if not self.client:
            logger.warning("OpenAI client not initialized, returning simple description")
            return f"{menu_name}은(는) {', '.join(ingredients[:3])}로 만들어진 특별한 메뉴입니다."

        try:
            prompt = f"""다음 메뉴에 대한 감성적인 스토리를 2-3문장으로 작성해주세요.

**메뉴 정보:**
- 이름: {menu_name}
- 주요 재료: {', '.join(ingredients)}
{f'- 원산지: {origin}' if origin else ''}
{f'- 역사: {history}' if history else ''}

**작성 가이드:**
1. 메뉴의 역사나 유래를 창의적으로 스토리텔링
2. 재료의 특징과 원산지를 자연스럽게 언급
3. 고객이 "이야기를 소비"하도록 감성적으로 작성
4. 2-3문장, 최대 100자

예시:
"이 메뉴는 1803년 영국에서 시작되어 전 세계로 퍼진 클래식한 레시피입니다.
엄선된 {ingredients[0]}와 {ingredients[1] if len(ingredients) > 1 else '재료'}가 어우러져
특별한 맛을 선사합니다."

스토리:"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 음식 역사와 스토리텔링 전문가입니다."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=200,
                temperature=0.9
            )

            story = response.choices[0].message.content.strip()
            logger.info(f"Menu storytelling generated: {story}")

            return story

        except Exception as e:
            logger.error(f"Failed to generate menu storytelling: {e}")
            return f"{menu_name}은(는) 신선한 재료로 만들어진 특별한 메뉴입니다."


# 싱글톤 인스턴스
story_generator_service = StoryGeneratorService()
