"""
고객 요청 의도 파싱
GPT-5.1을 사용하여 자연어를 구조화된 필터 조건으로 변환
"""

from ..llm.llm_router import get_llm_router
from ..constants import (
    MAX_RECOMMENDATIONS,
    CALORIE_LOW_THRESHOLD,
    CALORIE_HIGH_THRESHOLD,
    PROTEIN_LOW_THRESHOLD,
    PROTEIN_HIGH_THRESHOLD,
    CAFFEINE_LOW_THRESHOLD,
    SUGAR_LOW_THRESHOLD,
    SUGAR_HIGH_THRESHOLD,
    DEFAULT_SORT
)

class IntentParser:
    """고객 요청 의도 파싱 클래스"""
    
    def __init__(self):
        self.llm_router = get_llm_router()
    
    def parse_customer_request(self, customer_request, available_menus=None):
        """
        고객의 자연어 요청을 구조화된 필터 조건으로 변환
        
        Args:
            customer_request (str): 고객의 자연어 요청
            available_menus (list): 사용 가능한 메뉴 목록
                [{"id": 4, "name": "시그니처 메뉴"}, {"id": 5, "name": "음료"}]
        
        Returns:
            dict: 파싱된 의도
        """
        # 메뉴 옵션
        menu_options = f"사용 가능한 메뉴: {available_menus}" if available_menus else ""
        
        prompt = f"""당신은 고객의 메뉴 추천 요청을 분석하는 전문가입니다.

        {menu_options}

        필터 기준:
        - calorie: "low"(<{CALORIE_LOW_THRESHOLD}kcal), "medium"({CALORIE_LOW_THRESHOLD}-{CALORIE_HIGH_THRESHOLD}kcal), "high"(>{CALORIE_HIGH_THRESHOLD}kcal)
        - protein: "low"(<{PROTEIN_LOW_THRESHOLD}g), "medium"({PROTEIN_LOW_THRESHOLD}-{PROTEIN_HIGH_THRESHOLD}g), "high"(>{PROTEIN_HIGH_THRESHOLD}g)
        - caffeine: "none"(0mg), "low"(1-{CAFFEINE_LOW_THRESHOLD}mg), "high"(>{CAFFEINE_LOW_THRESHOLD}mg)
        - sugar: "low"(<{SUGAR_LOW_THRESHOLD}g), "medium"({SUGAR_LOW_THRESHOLD}-{SUGAR_HIGH_THRESHOLD}g), "high"(>{SUGAR_HIGH_THRESHOLD}g)

        정렬 옵션:
        - calories_asc/desc, protein_asc/desc, price_asc/desc, sugar_asc/desc

        최대 {MAX_RECOMMENDATIONS}개 메뉴만 추천합니다.

        응답 형식:
        {{
        "filter_conditions": {{
            "menu_id": null 또는 숫자,
            "calorie": null 또는 "low"/"medium"/"high",
            "protein": null 또는 "low"/"medium"/"high",
            "caffeine": null 또는 "none"/"low"/"high",
            "sugar": null 또는 "low"/"medium"/"high"
        }},
        "sort_by": "정렬 기준",
        "limit": {MAX_RECOMMENDATIONS},
        "explanation": "분석 설명 (한 문장)"
        }}

        고객 요청: "{customer_request}"

        순수 JSON만 반환하세요."""

        try:
            # ✅ LLMRouter 사용 (자동 Fallback!)
            response = self.llm_router.create_response(
                prompt,
                reasoning={"effort": "low"},
                text={"verbosity": "low"}
            )
            
            parsed = self.llm_router.parse_json_response(response)
            result = parsed['data']
            

            if result:
                result['limit'] = MAX_RECOMMENDATIONS
                # 사용된 모델 정보 추가
                result['_meta'] = {
                    'model_used': parsed['model_used'],
                    'elapsed_time': parsed['elapsed_time']
                }
            return result
        
        except Exception as e:
            # 파싱 실패 시 기본값 반환
            print(f"⚠️ 의도 파싱 실패: {e}, 기본값 사용")
            return {
                "filter_conditions": {
                    "menu_id": None,
                    "calorie": None,
                    "protein": None,
                    "caffeine": None,
                    "sugar": None
                },
                "sort_by": DEFAULT_SORT,
                "limit": MAX_RECOMMENDATIONS,
                "explanation": "모든 메뉴를 가격 순으로 추천합니다.",
                "_meta": {
                    'model_used': 'fallback',
                    'elapsed_time': 0
                }
            }
        
