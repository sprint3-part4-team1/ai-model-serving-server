"""
추천 시스템 서비스 레이어
팀 프로젝트 main.py에서 호출할 진입점
"""

import sys
import os

from src.recommendation.intent_parser import IntentParser
from src.recommendation.recommendation import MenuRecommender
from src.recommendation.data_loader import DataLoader


class RecommendationService:
    """추천 시스템 진입점 (Entry Point)"""

    def __init__(self):
        """서비스 초기화"""
        self.parser = IntentParser()
        self.recommender = MenuRecommender()
        self.loader = None

    def get_recommendations(self, customer_request, source='json', store_id=1):
        """
        고객 요청에 따른 메뉴 추천 (메인 API)

        Args:
            customer_request (str): 고객의 자연어 요청
                예: "칼로리 낮은 음료 추천", "고단백 메인 메뉴"
            source (str): 데이터 소스 ('json' 또는 'mysql')
            store_id (int): 매장 ID (MySQL 사용 시)

        Returns:
            dict: {
                'success': True/False,
                'total_found': int,
                'recommendations': [
                    {
                        'menu': {
                            'id': int,
                            'name': str,
                            'description': str,
                            'price': int,
                            'nutrition': {
                                'calories': int,
                                'protein_g': float,
                                'fat_g': float,
                                'carbs_g': float,
                                'sugar_g': float,
                                'caffeine_mg': int
                            }
                        },
                        'reason': str  # AI 추천 이유
                    }
                ],
                'parsed_intent': dict,  # 파싱된 의도 (디버깅용)
                'error': None or str
            }
        """
        try:
            # 1. 데이터 로드
            if not self.loader or self.loader.source != source:
                self.loader = DataLoader(source=source)

            data = self.loader.load(store_id=store_id)

            # 2. 의도 파싱
            parsed_intent = self.parser.parse_customer_request(customer_request)

            # 3. 메뉴 추천
            result = self.recommender.recommend(
                data['menu_items'],
                data['nutrition_estimates'],
                parsed_intent
            )

            # 4. 성공 응답 반환
            return {
                'success': True,
                'total_found': result['total_found'],
                'recommendations': result['recommendations'],
                'parsed_intent': parsed_intent,
                'error': None
            }

        except Exception as e:
            # 5. 에러 응답 반환
            return {
                'success': False,
                'total_found': 0,
                'recommendations': [],
                'parsed_intent': None,
                'error': str(e)
            }

    def format_output(self, result):
        """
        추천 결과를 보기 좋은 텍스트로 포맷팅

        Args:
            result (dict): get_recommendations() 반환값

        Returns:
            str: 포맷팅된 텍스트
        """
        if not result['success']:
            return f"❌ 오류 발생: {result['error']}"

        if result['total_found'] == 0:
            return "❌ 조건에 맞는 메뉴를 찾을 수 없습니다."

        output = []
        output.append("=" * 60)
        output.append(f"🎯 추천 메뉴 ({result['total_found']}개 발견)")
        output.append("=" * 60)

        for i, rec in enumerate(result['recommendations'], 1):
            menu = rec['menu']
            n = menu['nutrition']

            output.append(f"\n[{i}] {menu['name']} - {menu['price']:,}원")
            output.append(f"    {menu['description']}")
            output.append(f"    📊 {n['calories']}kcal | 단백질 {n['protein_g']}g | 당분 {n['sugar_g']}g | 카페인 {n['caffeine_mg']}mg")
            output.append(f"    💡 {rec['reason']}")

        output.append("\n" + "=" * 60)

        return "\n".join(output)

    def close(self):
        """리소스 정리"""
        if self.loader:
            self.loader.close()


# 간단한 테스트 함수
def test_service():
    """서비스 테스트"""
    service = RecommendationService()

    print("🧪 추천 서비스 테스트\n")

    # 테스트 케이스 1
    print("=" * 60)
    print("테스트 1: 칼로리 낮은 음료")
    print("=" * 60)
    result = service.get_recommendations("칼로리 낮은 음료 추천해줘", source='json')
    print(service.format_output(result))

    # 테스트 케이스 2
    print("\n\n" + "=" * 60)
    print("테스트 2: 고단백 메뉴")
    print("=" * 60)
    result = service.get_recommendations("고단백 메뉴 찾아줘", source='json')
    print(service.format_output(result))

    service.close()


if __name__ == "__main__":
    test_service()
