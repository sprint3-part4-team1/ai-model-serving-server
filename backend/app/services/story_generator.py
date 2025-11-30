"""
Story Generator Service
컨텍스트 정보를 기반으로 감성적인 스토리 문구를 생성하는 서비스
"""

import os
from typing import Dict, List, Optional
from openai import OpenAI
from app.core.logging import app_logger as logger
from app.core.config import settings


class StoryGeneratorService:
    """스토리 생성 서비스 (LLM 기반)"""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.model = "gpt-4o"  # GPT-4o: 빠르고 효율적인 모델

    def generate_story(
        self,
        context: Dict,
        store_name: Optional[str] = None,
        store_type: Optional[str] = "카페",
        menu_categories: Optional[List[str]] = None,
        selected_trends: Optional[List[str]] = None,
        menu_text: Optional[str] = None
    ) -> str:
        """
        컨텍스트 기반 스토리 문구 생성

        Args:
            context: Context Collector에서 수집한 정보
            store_name: 매장 이름
            store_type: 매장 타입 (카페, 레스토랑 등)
            menu_categories: 메뉴 카테고리 리스트
            selected_trends: 사용자가 선택한 트렌드 키워드 (우선적으로 반영)
            menu_text: 실제 메뉴 정보 텍스트 (예: "아메리카노(3,500원), 카페라떼(4,000원)")

        Returns:
            생성된 스토리 문구 (1-2문장)
        """
        if not self.client:
            logger.warning("OpenAI client not initialized, returning mock story")
            return self._generate_mock_story(context, store_type)

        try:
            # Prompt 생성
            prompt = self._build_prompt(context, store_name, store_type, menu_categories, selected_trends, menu_text)

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

    def _build_prompt(
        self,
        context: Dict,
        store_name: Optional[str],
        store_type: str,
        menu_categories: Optional[List[str]],
        selected_trends: Optional[List[str]] = None,
        menu_text: Optional[str] = None
    ) -> str:
        """
        GPT 프롬프트 생성

        Args:
            context: 컨텍스트 정보
            store_name: 매장 이름
            store_type: 매장 타입
            menu_categories: 메뉴 카테고리
            selected_trends: 사용자가 선택한 트렌드
            menu_text: 실제 메뉴 정보

        Returns:
            생성된 프롬프트
        """
        weather = context.get("weather", {})
        time_info = context.get("time_info", {})
        season = context.get("season", "")

        # 선택된 트렌드가 있으면 우선 사용, 없으면 기본 트렌드 사용
        if selected_trends:
            trends = selected_trends
        else:
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

        # 메뉴 정보
        if menu_text:
            # 실제 메뉴 정보가 있으면 사용
            menu_info = f"추천 메뉴: {menu_text}"
        else:
            # 없으면 메뉴 카테고리 사용
            menu_str = ", ".join(menu_categories) if menu_categories else "음료"
            menu_info = f"주요 메뉴: {menu_str}"

        # 매장 타입별 예시 생성
        examples = self._get_examples_by_store_type(store_type)

        prompt = f"""다음 정보를 바탕으로 고객의 마음을 사로잡는 감성적인 추천 문구를 1-2문장으로 작성해주세요.

**매장 정보:**
- 매장 이름: {store_name or store_type}
- 매장 타입: {store_type}
- {menu_info}

**현재 상황:**
- 날씨: {weather_desc}, 온도 {temperature}도
- 계절: {season_kr}
- 시간대: {period_kr} ({time_str})
{f'- 인기 트렌드: {trend_str}' if trend_str else ''}

**작성 가이드:**
1. 반드시 매장 타입({store_type})에 맞는 메뉴를 추천할 것
2. 자연스럽고 친근한 톤으로 작성
3. 현재 날씨, 계절, 시간대를 자연스럽게 녹여내기
4. 구체적인 메뉴를 언급하여 구매 욕구 자극
5. 1-2문장으로 간결하게 (최대 50자)
6. 이모지는 사용하지 말 것

{store_type}에 적합한 예시:
{examples}

문구:"""

        return prompt

    def _get_examples_by_store_type(self, store_type: str) -> str:
        """
        매장 타입에 맞는 예시 생성

        Args:
            store_type: 매장 타입

        Returns:
            예시 문자열
        """
        store_type_lower = store_type.lower()

        # 중국집
        if "중국" in store_type_lower:
            return """- "비 오는 가을 저녁, 따뜻한 짬뽕으로 몸을 녹여보세요."
- "쌀쌀한 겨울 점심, 얼큰한 마라탕이 생각나는 날씨네요."
- "더운 여름 저녁, 시원한 냉면 한 그릇 어떠세요?"""

        # 일식
        elif "일식" in store_type_lower or "초밥" in store_type_lower or "돈까스" in store_type_lower:
            return """- "맑은 가을 점심, 신선한 회덮밥으로 활력을 채워보세요."
- "추운 겨울 저녁, 따뜻한 우동이 그리워지는 날씨네요."
- "더운 여름 점심, 시원한 냉소바 한 그릇 어떠세요?"""

        # 한식
        elif "한식" in store_type_lower or "한정식" in store_type_lower:
            return """- "비 오는 가을 저녁, 따뜻한 된장찌개와 밥 한 공기가 생각나는 날씨네요."
- "추운 겨울 점심, 뜨끈한 김치찌개로 몸을 녹여보세요."
- "더운 여름 점심, 시원한 냉국수가 그리워지는 날씨네요."""

        # 양식/이탈리안
        elif "양식" in store_type_lower or "이탈리" in store_type_lower or "파스타" in store_type_lower:
            return """- "비 오는 가을 저녁, 크림 파스타와 함께 여유로운 저녁 시간을 즐겨보세요."
- "추운 겨울 점심, 따뜻한 스테이크 한 접시가 생각나는 날씨네요."
- "맑은 봄 저녁, 신선한 샐러드와 리조또는 어떠세요?"""

        # 분식
        elif "분식" in store_type_lower:
            return """- "쌀쌀한 가을 저녁, 매콤한 떡볶이로 입맛을 돋워보세요."
- "비 오는 날 오후, 따뜻한 어묵과 순대가 생각나는 날씨네요."
- "추운 겨울 저녁, 얼큰한 라면 한 그릇 어떠세요?"""

        # 치킨/패스트푸드
        elif "치킨" in store_type_lower or "패스트" in store_type_lower or "버거" in store_type_lower:
            return """- "비 오는 저녁, 바삭한 치킨과 함께 집에서 편안한 시간 보내세요."
- "주말 저녁, 치킨과 맥주로 하루의 피로를 풀어보세요."
- "간식이 생각나는 오후, 바삭한 치킨 한 조각 어떠세요?"""

        # 카페 (기본)
        elif "카페" in store_type_lower or "커피" in store_type_lower:
            return """- "비 오는 가을 오후, 따뜻한 아메리카노 한 잔과 함께 여유를 느껴보세요."
- "쌀쌀한 겨울 아침, 달콤한 카페모카로 하루를 시작하는 건 어떠세요?"
- "더운 여름 점심, 시원한 아이스 음료로 더위를 날려보세요."""

        # 디저트/베이커리
        elif "디저트" in store_type_lower or "베이커리" in store_type_lower or "빵" in store_type_lower:
            return """- "맑은 가을 오후, 갓 구운 빵과 따뜻한 차 한 잔 어떠세요?"
- "쌀쌀한 겨울 저녁, 달콤한 케이크로 기분 전환을 해보세요."
- "봄 오후, 신선한 과일 타르트와 함께 달콤한 휴식 시간을 즐겨보세요."""

        # 기타 레스토랑
        else:
            return """- "비 오는 가을 저녁, 따뜻한 음식과 함께 여유로운 시간을 즐겨보세요."
- "쌀쌀한 겨울 점심, 따뜻한 국물 요리가 생각나는 날씨네요."
- "더운 여름 저녁, 시원한 메뉴로 더위를 날려보세요."""

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

    def generate_welcome_message(
        self,
        context: Dict,
        store_name: str,
        store_type: str = "카페"
    ) -> str:
        """
        메뉴판 최상단 환영 문구 생성

        날씨, 계절, 시간, 트렌드를 반영하여 고객을 환영하는 매력적인 문구 생성

        Args:
            context: Context Collector에서 수집한 정보
            store_name: 매장 이름
            store_type: 매장 타입

        Returns:
            환영 문구 (1-2문장)
        """
        if not self.client:
            logger.warning("OpenAI client not initialized, returning mock welcome message")
            return self._generate_mock_welcome(context, store_name, store_type)

        try:
            weather = context.get("weather", {})
            time_info = context.get("time_info", {})
            season = context.get("season", "")
            trends = context.get("instagram_trends", []) or context.get("google_trends", []) or context.get("trends", [])

            # 날씨 정보
            weather_desc = weather.get("description", "맑음")
            temperature = weather.get("temperature", 15)

            # 시간대 정보
            period_kr = time_info.get("period_kr", "오후")
            weekday_kr = time_info.get("weekday_kr", "")

            # 계절 정보
            season_map = {
                "spring": "봄",
                "summer": "여름",
                "autumn": "가을",
                "winter": "겨울"
            }
            season_kr = season_map.get(season, "")

            # 트렌드 정보 (상위 3개)
            trend_str = ", ".join(trends[:3]) if trends else ""

            prompt = f"""다음 상황에 맞는 매력적인 환영 문구를 작성해주세요.

**매장 정보:**
- 이름: {store_name}
- 타입: {store_type}

**현재 상황:**
- 날씨: {weather_desc}, 온도 {temperature}도
- 계절: {season_kr}
- 시간대: {period_kr}, {weekday_kr}
{f'- 인기 트렌드: {trend_str}' if trend_str else ''}

**작성 가이드:**
1. 현재 날씨와 시간대를 자연스럽게 반영
2. 고객에게 따뜻하고 친근하게 다가가기
3. 매장 방문을 유도하는 감성적인 표현
4. 1-2문장으로 간결하게 (최대 60자)
5. 이모지는 사용하지 말 것
6. 매장 타입({store_type})에 맞는 분위기로 작성

좋은 예시:
- "비 오는 월요일 오후, 따뜻한 커피 한 잔으로 힐링하는 건 어떠세요?"
- "쌀쌀한 가을 아침, {store_name}에서 특별한 하루를 시작해보세요."
- "주말 저녁, 맛있는 음식과 함께 여유로운 시간을 즐겨보세요."

환영 문구:"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 감성적인 환대 전문가입니다. 고객이 매장을 방문하고 싶게 만드는 따뜻한 문구를 작성합니다."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=100,
                temperature=0.8,
                presence_penalty=0.5
            )

            message = response.choices[0].message.content.strip()
            # 따옴표 제거
            message = message.strip('"').strip("'")

            logger.info(f"Welcome message generated: {message}")
            return message

        except Exception as e:
            logger.error(f"Failed to generate welcome message: {e}")
            return self._generate_mock_welcome(context, store_name, store_type)

    def _generate_mock_welcome(self, context: Dict, store_name: str, store_type: str) -> str:
        """Mock 환영 문구 생성"""
        weather = context.get("weather", {})
        time_info = context.get("time_info", {})

        weather_desc = weather.get("description", "맑음")
        period_kr = time_info.get("period_kr", "오후")

        templates = [
            f"{weather_desc} {period_kr}, {store_name}에 오신 것을 환영합니다.",
            f"{period_kr}의 여유로운 시간, {store_name}에서 특별한 순간을 만들어보세요.",
            f"오늘도 좋은 하루 되세요. {store_name}이 함께합니다."
        ]

        import random
        return random.choice(templates)

    def generate_menu_highlights(
        self,
        context: Dict,
        menus: List[Dict],
        store_type: str = "카페",
        max_highlights: int = 3
    ) -> List[Dict]:
        """
        시즌/날씨에 맞는 메뉴 하이라이트 생성

        현재 컨텍스트에 가장 적합한 메뉴를 선택하고 추천 이유를 생성

        Args:
            context: 컨텍스트 정보
            menus: 메뉴 리스트 [{"id": 1, "name": "아메리카노", "category": "커피", ...}]
            store_type: 매장 타입
            max_highlights: 최대 하이라이트 개수

        Returns:
            하이라이트 메뉴 리스트 [{"menu_id": 1, "name": "아메리카노", "reason": "..."}]
        """
        if not menus:
            logger.warning("No menus provided for highlights")
            return []

        if not self.client:
            logger.warning("OpenAI client not initialized, returning random highlights")
            return self._generate_mock_highlights(menus, max_highlights)

        try:
            import json

            weather = context.get("weather", {})
            time_info = context.get("time_info", {})
            season = context.get("season", "")
            trends = context.get("instagram_trends", []) or context.get("google_trends", []) or context.get("trends", [])

            # 날씨 정보
            weather_desc = weather.get("description", "맑음")
            temperature = weather.get("temperature", 15)

            # 시간대
            period_kr = time_info.get("period_kr", "오후")

            # 계절
            season_map = {"spring": "봄", "summer": "여름", "autumn": "가을", "winter": "겨울"}
            season_kr = season_map.get(season, "")

            # 메뉴 정보 정리
            menu_info = []
            for menu in menus[:20]:  # 최대 20개만 전송 (토큰 절약)
                menu_info.append({
                    "id": menu.get("id"),
                    "name": menu.get("name"),
                    "category": menu.get("category", ""),
                    "description": menu.get("description", "")[:50]  # 50자로 제한
                })

            prompt = f"""다음 상황에 가장 잘 어울리는 메뉴 {max_highlights}개를 선택하고 추천 이유를 작성해주세요.

**현재 상황:**
- 날씨: {weather_desc}, {temperature}도
- 계절: {season_kr}
- 시간대: {period_kr}
- 인기 트렌드: {', '.join(trends[:5]) if trends else '없음'}

**메뉴 목록 (메인 메뉴만, 사이드/음료 제외됨):**
{json.dumps(menu_info, ensure_ascii=False, indent=2)}

**작성 가이드:**
1. 날씨/계절/시간대에 가장 잘 맞는 메뉴 선택
2. 트렌드와 관련된 메뉴 우선 선택
3. 추천 이유는 간결하고 설득력 있게 (20자 내외)
4. 현재 날씨와 트렌드를 자연스럽게 반영한 이유 작성
5. JSON 형식으로 응답

**응답 형식:**
{{
  "highlights": [
    {{"menu_id": 1, "name": "아메리카노", "reason": "비 오는 날엔 따뜻한 커피가 제격"}},
    {{"menu_id": 3, "name": "호떡", "reason": "인스타그램 핫트렌드 1위"}}
  ]
}}

응답:"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 메뉴 큐레이션 전문가입니다. 현재 상황에 가장 적합한 메뉴를 선택하고 설득력 있는 이유를 제시합니다."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            highlights = result.get("highlights", [])[:max_highlights]

            logger.info(f"Menu highlights generated: {len(highlights)} items")
            return highlights

        except Exception as e:
            logger.error(f"Failed to generate menu highlights: {e}")
            return self._generate_mock_highlights(menus, max_highlights)

    def _generate_mock_highlights(self, menus: List[Dict], max_highlights: int) -> List[Dict]:
        """Mock 메뉴 하이라이트 생성"""
        import random

        selected = random.sample(menus, min(max_highlights, len(menus)))

        reasons = [
            "오늘의 추천 메뉴입니다",
            "인기 메뉴입니다",
            "시즌 한정 메뉴입니다",
            "베스트셀러입니다"
        ]

        highlights = []
        for menu in selected:
            highlights.append({
                "menu_id": menu.get("id"),
                "name": menu.get("name"),
                "reason": random.choice(reasons)
            })

        return highlights


# 싱글톤 인스턴스
story_generator_service = StoryGeneratorService()
