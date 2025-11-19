"""
고객 요청 의도 파싱 모듈
자연어 요청을 분석하여 필터링/정렬 조건을 추출
"""
from recommendation.gpt_client import get_gpt_client


class IntentParser:
    """고객 요청을 분석하여 의도를 파싱"""

    def __init__(self):
        self.gpt_client = get_gpt_client()

    def parse_customer_request(self, customer_text):
        """
        고객 자연어 요청을 분석하여 필터/정렬 조건 추출

        Args:
            customer_text (str): 고객이 입력한 자연어 요청
                예: "칼로리 낮은 음료 추천", "고단백 메뉴 찾아줘"

        Returns:
            dict: 파싱된 의도
                {
                    "filter_conditions": {
                        "category": "drink",  # main, side, drink
                        "calorie": "low",     # low, high, medium
                        "protein": "high",    # low, high, medium
                        "caffeine": "none",   # none, low, high
                        "sugar": "low"        # low, high, medium
                    },
                    "sort_by": "calories_asc",  # calories_asc, calories_desc, protein_desc, etc.
                    "limit": 3,                  # 추천 개수
                    "explanation": "칼로리가 낮은 음료를 찾으시는군요!"
                }
        """
        # GPT-5.1은 단일 input_text를 사용하므로 system + user를 합침
        combined_prompt = """당신은 메뉴 추천 시스템의 의도 파싱 전문가입니다.
            고객의 자연어 요청을 분석하여 필터링 조건과 정렬 기준을 JSON으로 추출하세요.

            응답 형식:
            {
            "filter_conditions": {
                "category": null or "main" or "side" or "drink",
                "calorie": null or "low" or "high" or "medium",
                "protein": null or "low" or "high" or "medium",
                "caffeine": null or "none" or "low" or "high",
                "sugar": null or "low" or "high" or "medium"
            },
            "sort_by": "calories_asc" or "calories_desc" or "protein_desc" or "price_asc" or "price_desc",
            "limit": 3,
            "explanation": "고객 요청에 대한 간단한 설명"
            }

            카테고리 매핑:
            - 메인/파스타/스테이크/리조또/그라탕 → "main"
            - 사이드/샐러드/디저트/케이크 → "side"
            - 음료/커피/주스/스무디 → "drink"

            칼로리/당분/단백질 기준:
            - low: 낮은 것 우선
            - high: 높은 것 우선
            - medium: 중간 수준

            카페인:
            - none: 카페인 없는 것만
            - low: 낮은 것 우선
            - high: 높은 것 우선

            ---

            고객 요청: """ + customer_text + """

            위 요청을 분석하여 JSON 형식으로만 응답하세요. 다른 텍스트는 포함하지 마세요."""

        # GPT-5.1 호출 (JSON 응답 유도)
        response = self.gpt_client.create_response(
            input_text=combined_prompt,
            reasoning={"effort": "medium"},  # 적절한 추론 수준
            text={"verbosity": "low"}  # 간결한 응답
        )

        # JSON 파싱
        parsed_intent = self.gpt_client.parse_json_response(response)

        return parsed_intent
