"""
Menu Filter Service
AI 기반 메뉴 필터링/정렬 서비스
"""

from typing import List, Dict, Any
import json
from openai import OpenAI
from app.core.config import settings
from app.core.logging import app_logger as logger


class MenuFilterService:
    """메뉴 필터링 서비스"""

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def filter_menus(self, query: str, menus: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        자연어 쿼리 기반 메뉴 필터링

        Args:
            query: 고객 요청 (예: "칼로리 낮은 음료 추천", "달콤한 디저트 찾기")
            menus: 메뉴 리스트

        Returns:
            필터링된 메뉴와 설명
        """
        logger.info(f"Menu filter requested: query='{query}', menu_count={len(menus)}")

        try:
            # OpenAI를 사용하여 메뉴 필터링
            filtered_result = self._filter_with_openai(query, menus)

            logger.info(f"Filtered {len(filtered_result['filtered_menus'])} menus")
            return filtered_result

        except Exception as e:
            logger.error(f"Menu filtering failed: {e}")
            # 에러 발생 시 전체 메뉴 반환
            return {
                "filtered_menus": menus,
                "explanation": "필터링 중 오류가 발생하여 전체 메뉴를 보여드립니다.",
                "total_count": len(menus)
            }

    def _filter_with_openai(self, query: str, menus: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        OpenAI를 사용한 메뉴 필터링

        간단하고 효과적인 프롬프트로 구현
        """
        # 메뉴 정보를 간단하게 정리
        menu_list = []
        for menu in menus:
            menu_info = {
                "id": menu["id"],
                "name": menu["name"],
                "category": menu["category"],
                "price": menu["price"],
                "description": menu.get("description", ""),
                "ingredients": menu.get("ingredients", [])
            }
            menu_list.append(menu_info)

        # 프롬프트 작성
        prompt = f"""당신은 카페/레스토랑의 메뉴 추천 AI입니다.

고객 요청: "{query}"

전체 메뉴:
{json.dumps(menu_list, ensure_ascii=False, indent=2)}

위 요청에 맞는 메뉴를 필터링하고 추천 이유를 설명해주세요.

응답 형식 (JSON):
{{
  "filtered_menus": [
    {{
      "id": 메뉴ID,
      "name": "메뉴이름",
      "category": "카테고리",
      "price": 가격,
      "reason": "추천 이유 (1문장)"
    }}
  ],
  "explanation": "전체 설명 (2-3문장)",
  "total_count": 필터링된_메뉴_개수
}}

중요:
- 요청과 관련 없는 메뉴는 제외하세요
- 가장 적합한 메뉴를 상위에 배치하세요
- 추천 이유는 구체적이고 간결하게 작성하세요
- 반드시 JSON 형식으로만 응답하세요
"""

        # OpenAI API 호출
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",  # 빠르고 저렴한 모델
            messages=[
                {
                    "role": "system",
                    "content": "당신은 메뉴 추천 전문가입니다. 항상 JSON 형식으로만 응답합니다."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # 일관성 있는 응답
            max_tokens=1000,
            response_format={"type": "json_object"}  # JSON 응답 강제
        )

        # 응답 파싱
        result_text = response.choices[0].message.content
        result = json.loads(result_text)

        logger.info(f"OpenAI filtering result: {result}")
        return result


# 싱글톤 인스턴스
menu_filter_service = MenuFilterService()
