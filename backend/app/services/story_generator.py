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
        store_type: Optional[str] = None,
        menu_categories: Optional[List[str]] = None,
        selected_trends: Optional[List[str]] = None,
        menu_text: Optional[str] = None
    ) -> str:
        """
        컨텍스트 기반 스토리 문구 생성

        Args:
            context: Context Collector에서 수집한 정보
            store_name: 매장 이름
            store_type: (사용 안 함 - 하위 호환성 유지용)
            menu_categories: 메뉴 카테고리 리스트
            selected_trends: 사용자가 선택한 트렌드 키워드 (우선적으로 반영)
            menu_text: 실제 메뉴 정보 텍스트 (예: "아메리카노(3,500원), 카페라떼(4,000원)")

        Returns:
            생성된 스토리 문구 (1-2문장)
        """
        if not self.client:
            logger.warning("OpenAI client not initialized, returning mock story")
            return self._generate_mock_story(context)

        try:
            # Prompt 생성 (store_type 제거)
            prompt = self._build_prompt(context, store_name, menu_categories, selected_trends, menu_text)

            logger.info(f"Generating story with prompt: {prompt[:100]}...")

            # 로그: menu_text 확인
            if menu_text:
                logger.info(f"Menu text provided: {menu_text[:100]}...")
            else:
                logger.warning("No menu_text provided, using categories only")

            # GPT API 호출
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 매장의 마케팅 담당자입니다. "
                                   "반드시 제공된 메뉴 목록에서만 선택하여 추천하며, "
                                   "목록에 없는 메뉴나 일반적인 단어(음료, 커피, 음식 등)는 절대 사용하지 않습니다. "
                                   "규칙을 엄격히 준수하는 것이 가장 중요합니다."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=150,
                temperature=0.3,  # 환각 방지를 위해 낮춤
                top_p=0.9,
                presence_penalty=0.6,
                frequency_penalty=0.3
            )

            story = response.choices[0].message.content.strip()
            logger.info(f"Story generated successfully: {story}")

            return story

        except Exception as e:
            logger.error(f"Failed to generate story with GPT: {e}")
            return self._generate_mock_story(context)

    def _build_prompt(
        self,
        context: Dict,
        store_name: Optional[str],
        menu_categories: Optional[List[str]],
        selected_trends: Optional[List[str]] = None,
        menu_text: Optional[str] = None
    ) -> str:
        """
        GPT 프롬프트 생성 (실제 메뉴 기반)

        Args:
            context: 컨텍스트 정보
            store_name: 매장 이름
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
            menu_info = f"**📋 사용 가능한 메뉴 (이 목록에만 있는 메뉴만 사용):**\n{menu_text}"
            menu_constraint = "위 목록에 있는 메뉴 이름만 사용하세요. 목록에 없는 메뉴는 절대 언급하지 마세요."
        else:
            # 없으면 일반적인 문구만 사용
            logger.warning("No menu_text available - generating generic message")
            menu_str = ", ".join(menu_categories) if menu_categories else "메뉴"
            menu_info = f"메뉴 카테고리: {menu_str}"
            menu_constraint = "메뉴 이름을 구체적으로 언급하지 말고, 매장 방문을 유도하는 일반적인 문구만 사용하세요."

        prompt = f"""당신은 {store_name or "이 매장"}의 마케팅 담당자입니다.

{menu_info}

**현재 날씨와 시간:**
- 날씨: {weather_desc}
- 온도: {temperature}도 ({season_kr})
- 시간대: {period_kr} ({time_str})
{f'- 트렌드: {trend_str}' if trend_str else ''}

**🚨 절대 규칙 (하나라도 어기면 안 됨!):**

1. **메뉴 제한 (최우선!):**
   {menu_constraint}
   - "음료", "커피", "음식", "메뉴", "한 잔", "요리" 같은 일반 단어 절대 금지
   - 반드시 위 목록에 있는 정확한 메뉴 이름만 사용
   - 다른 매장 메뉴 언급 금지

2. **온도 제한:**
   - {temperature}도 → {"10도 이하이므로 따뜻한 메뉴만" if temperature <= 10 else "25도 이상이므로 시원한 메뉴만" if temperature >= 25 else "온도에 맞는 메뉴 추천"}

3. **형식:**
   - 실제 메뉴 이름 그대로 정확히 사용
   - 이모지 사용 금지
   - 최대 2문장, 50자 이내

**✅ 좋은 예시:**
- "추운 겨울 저녁, 따뜻한 꿔바로우로 몸을 녹여보세요." (꿔바로우가 메뉴에 있는 경우)
- "쌀쌀한 아침, 얼큰한 유린기로 하루를 시작하는 건 어떠세요?" (유린기가 메뉴에 있는 경우)

**❌ 절대 금지 (이렇게 쓰면 안 됨!):**
- "겨울 밤, 따뜻한 음료 한 잔" ← "음료", "한 잔"은 일반 단어
- "맛있는 커피로 시작하세요" ← "커피"는 일반 단어
- "특별한 메뉴로" ← "메뉴"는 일반 단어
- "아메리카노 한 잔" ← 아메리카노가 목록에 없으면 사용 불가

⚠️ 반드시 위 목록에 있는 메뉴 이름만 사용하여 1-2문장의 추천 문구를 작성하세요:"""

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

    def _generate_mock_story(self, context: Dict) -> str:
        """
        Mock 스토리 생성 (GPT 사용 불가 시)

        Args:
            context: 컨텍스트 정보

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
            f"{weather_desc} {season_kr} {period_kr}, 특별한 메뉴로 여유를 즐겨보세요.",
            f"{temperature}도의 {season_kr} 날씨, 맛있는 한 끼 어떠세요?",
            f"{period_kr}의 특별한 순간, 따뜻한 메뉴와 함께하세요."
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
            from datetime import datetime

            weather = context.get("weather", {})
            time_info = context.get("time_info", {})
            season = context.get("season", "")
            trends = context.get("instagram_trends", []) or context.get("google_trends", []) or context.get("trends", [])

            # 날씨 정보
            weather_desc = weather.get("description", "맑음")
            temperature = weather.get("temperature", 15)

            # 시간대
            period_kr = time_info.get("period_kr", "오후")
            hour = time_info.get("hour", 12)

            # 계절
            season_map = {"spring": "봄", "summer": "여름", "autumn": "가을", "winter": "겨울"}
            season_kr = season_map.get(season, "")

            # 날짜 및 이벤트 정보
            today = datetime.now()
            month = today.month
            day = today.day
            weekday_kr = time_info.get("weekday_kr", "")

            # 특별 이벤트 감지
            special_event = ""
            if month == 12:
                if day <= 25:
                    days_until_christmas = 25 - day
                    if days_until_christmas == 0:
                        special_event = "오늘은 크리스마스!"
                    elif days_until_christmas <= 7:
                        special_event = f"크리스마스가 {days_until_christmas}일 남음"
                    elif days_until_christmas <= 14:
                        special_event = f"크리스마스가 2주도 채 안 남음"
                    else:
                        special_event = "크리스마스 시즌"
                elif day > 25:
                    special_event = "연말 분위기"
            elif month == 2 and day == 14:
                special_event = "발렌타인데이"
            elif month == 3 and day == 14:
                special_event = "화이트데이"
            elif month == 10 and day == 31:
                special_event = "할로윈"

            # 온도 구간 판단
            if temperature < 0:
                temp_desc = "영하의 매서운 추위"
            elif temperature < 5:
                temp_desc = "몸이 얼어붙는 추운 날씨"
            elif temperature < 10:
                temp_desc = "쌀쌀한 날씨"
            elif temperature < 15:
                temp_desc = "선선한 날씨"
            elif temperature < 20:
                temp_desc = "포근한 날씨"
            elif temperature < 25:
                temp_desc = "따뜻한 날씨"
            elif temperature < 30:
                temp_desc = "더운 날씨"
            else:
                temp_desc = "무더운 폭염"

            # 메뉴 정보 정리
            menu_info = []
            for menu in menus[:20]:  # 최대 20개만 전송 (토큰 절약)
                menu_info.append({
                    "id": menu.get("id"),
                    "name": menu.get("name"),
                    "category": menu.get("category", ""),
                    "description": menu.get("description", "")[:50]  # 50자로 제한
                })

            # 트렌드 문자열 생성
            trends_str = ', '.join(trends[:10]) if trends else '없음'

            prompt = f"""다음 상황에 가장 잘 어울리는 메뉴 {max_highlights}개를 선택하고 추천 이유를 작성해주세요.

**📍 현재 상황 (반드시 이 구체적인 정보를 활용하세요!):**
- 🌡️ 온도: {temperature}도 ({temp_desc})
- 🌤️ 날씨: {weather_desc}
- ❄️ 계절: {season_kr}
- 🕐 시간: {period_kr} ({hour}시경)
- 📅 요일: {weekday_kr}
{'- 🎄 특별: ' + special_event if special_event else ''}
- 📊 인기 트렌드: {trends_str}

**메뉴 목록:**
{json.dumps(menu_info, ensure_ascii=False, indent=2)}

**🎯 필수 작성 규칙 (하나라도 어기면 안 됨!):**

1️⃣ **길이**: 각 추천 이유는 **반드시 40-60자**로 작성 (30자 미만은 절대 금지!)

2️⃣ **구체적 데이터 활용 필수**:
   - 온도 {temperature}도를 직접 언급하거나 "{temp_desc}"라는 표현 사용
   - 인기 트렌드 키워드 중 최소 1개 이상 자연스럽게 포함
{'   - "' + special_event + '" 이벤트 언급' if special_event else ''}
   - {period_kr} 시간대의 특성 반영

3️⃣ **다양성**: 3개 메뉴의 추천 이유가 모두 완전히 다른 구조와 표현이어야 함

4️⃣ **감성 표현**: 구체적이고 생생한 감각적 표현 사용 (맛, 온도, 분위기)

**✅ 완벽한 예시 (이렇게 작성하세요!):**

온도 2.8도, 겨울, 오후, 크리스마스 23일 남음 상황이라면:
- "영하 근처 매서운 추위({temperature}도)를 녹여줄 따뜻한 고기 요리, 크리스마스 준비로 지친 오후의 완벽한 에너지 충전원" (55자)
- "추운 겨울 오후 SNS 트렌드 1위 파스타로 몸과 마음을 따뜻하게, 크리스마스 분위기까지 더해지는 특별한 한 끼" (58자)
- "얼어붙은 몸을 감싸는 뜨끈한 토마토 국물과 쫄깃한 면발의 조화, {weekday_kr} 오후 피로를 풀어주는 완벽한 선택" (52자)

**❌ 나쁜 예시 (이렇게 절대 쓰지 마세요!):**
- "겨울에 어울리는 스테이크" ❌ (14자, 너무 짧음, 온도 미언급, 트렌드 미활용)
- "추운 날씨에 좋은 파스타" ❌ (13자, 구체적 온도 없음, 감성 없음)
- "크리스마스 분위기와 어울리는 메뉴" ❌ (19자, 짧음, 맛/식감 표현 없음)
- "겨울 감성을 자극하는 음식" ❌ (14자, 너무 짧고 추상적)

**💡 상황별 필수 표현 가이드:**

온도별 (현재 {temperature}도):
- 5도 미만: "영하 근처 매서운 추위", "꽁꽁 얼어붙은 몸을", "차가운 겨울바람에 떨리는"
- 5-10도: "쌀쌀한 날씨에 움츠러든", "찬바람이 부는 날", "겨울 추위로 얼어붙은"
- 25도 이상: "무더운 열기를 식혀줄", "땀 흘리는 더위 속에서", "여름 폭염을 날려줄"

시간대별 (현재 {period_kr}):
- 아침: "하루를 활기차게 시작할", "아침 식사로 든든한", "상쾌한 아침의 에너지원"
- 점심: "오전 업무로 지친 몸에", "점심시간 최고의 선택", "오후 활력을 위한"
- 오후: "나른한 오후를 깨워줄", "오후 간식으로 완벽한", "저녁 전 허기를 달래줄"
- 저녁: "하루의 피로를 풀어주는", "저녁 식사로 특별한", "마음까지 따뜻해지는"

트렌드 활용 (반드시 키워드 1개 이상 포함):
- 현재 트렌드: {trends_str}
- 예: "SNS에서 가장 핫한 {trends[0] if trends else ''}로", "요즘 대세인 {trends[1] if len(trends) > 1 else ''}와 함께"

**응답 형식:**
{{
  "highlights": [
    {{"menu_id": 1, "name": "메뉴명", "reason": "40-60자의 완전한 문장..."}},
    {{"menu_id": 2, "name": "메뉴명", "reason": "40-60자의 완전한 문장..."}},
    {{"menu_id": 3, "name": "메뉴명", "reason": "40-60자의 완전한 문장..."}}
  ]
}}

**🚨 최종 확인: 각 reason이 40자 이상인지 반드시 확인 후 응답하세요!**

응답:"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 메뉴 큐레이션 전문가입니다. 반드시 다음 규칙을 지켜주세요: 1) 각 추천 이유는 40-60자의 완전한 문장, 2) 제공된 온도, 시간대, 트렌드 키워드를 구체적으로 활용, 3) 감각적이고 생생한 표현 사용, 4) 각 메뉴마다 완전히 다른 구조와 표현. 30자 미만의 짧은 추천은 절대 금지입니다."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=800,
                temperature=0.8,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            highlights = result.get("highlights", [])[:max_highlights]

            # 알레르기 정보 추가
            highlights = self._add_allergen_warnings(highlights)

            logger.info(f"Menu highlights generated: {len(highlights)} items")
            return highlights

        except Exception as e:
            logger.error(f"Failed to generate menu highlights: {e}")
            return self._generate_mock_highlights(menus, max_highlights)

    def _add_allergen_warnings(self, highlights: List[Dict]) -> List[Dict]:
        """
        메뉴 하이라이트에 알레르기 경고 추가

        Args:
            highlights: 하이라이트 리스트 [{"menu_id": 1, "name": "...", "reason": "..."}]

        Returns:
            알레르기 경고가 추가된 하이라이트 리스트
        """
        try:
            # AllergenMapper import (상대 경로)
            import sys
            import os
            # backend/src/nutrition 경로 추가
            backend_src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "src")
            if backend_src_path not in sys.path:
                sys.path.insert(0, backend_src_path)

            from nutrition.allergen_mapper import AllergenMapper
            from app.core.database import SessionLocal
            from app.models.menu import MenuItem

            # DB 세션
            db = SessionLocal()

            try:
                for highlight in highlights:
                    menu_id = highlight.get("menu_id")
                    if not menu_id:
                        continue

                    # DB에서 메뉴 아이템 조회
                    menu_item = db.query(MenuItem).filter(MenuItem.id == menu_id).first()
                    if not menu_item:
                        continue

                    # 재료 정보 가져오기
                    ingredients = [ing.ingredient_name for ing in menu_item.ingredients]

                    if not ingredients:
                        continue

                    # 알레르기 감지
                    allergens = AllergenMapper.detect_allergens(ingredients)

                    if allergens:
                        # 알레르기 경고 추가
                        warning = AllergenMapper.get_allergen_warning(allergens)
                        highlight["allergen_warning"] = warning

                        # reason에도 경고 추가 (선택사항)
                        # highlight["reason"] = f"{highlight['reason']} {warning}"

            finally:
                db.close()

        except Exception as e:
            logger.warning(f"Failed to add allergen warnings: {e}")
            # 에러 발생해도 하이라이트는 반환

        return highlights

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
