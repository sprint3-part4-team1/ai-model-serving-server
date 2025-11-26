"""
추천 시스템 서비스 레이어
"""
import sys
import os

from recommendation.intent_parser import IntentParser
from recommendation.recommendation import MenuRecommender
from recommendation.data_loader import DataLoader


class RecommendationService:
    """추천 시스템 진입점"""
    
    def __init__(self):
        self.parser = IntentParser()
        self.recommender = MenuRecommender()
        self.loader = None
    
    def get_recommendations(self, customer_request, source='json', store_id=2):
        """메뉴 추천"""
        try:
            # 1. 데이터 로드
            if not self.loader or self.loader.source != source:
                self.loader = DataLoader(source=source)
            
            data = self.loader.load(store_id=store_id)
            
            # ✅ 2. menus 정보 추출
            available_menus = data.get('menus', [])
            
            # ✅ 3. 의도 파싱 (menus 정보 전달)
            parsed_intent = self.parser.parse_customer_request(
                customer_request,
                available_menus=available_menus
            )
            
            # 4. 메뉴 추천
            result = self.recommender.recommend(
                data['menu_items'],
                data['nutrition_estimates'],
                parsed_intent
            )
            
            return {
                'success': True,
                'total_found': result['total_found'],
                'recommendations': result['recommendations'],
                'parsed_intent': parsed_intent,
                'error': None
            }
        
        except Exception as e:
            return {
                'success': False,
                'total_found': 0,
                'recommendations': [],
                'parsed_intent': None,
                'error': str(e)
            }
    
    def format_output(self, result):
        """결과 포맷팅"""
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
            n = menu.get('nutrition')
            
            output.append(f"\n[{i}] {menu['name']} - {menu['price']:,}원")
            output.append(f"    {menu['description']}")
            
            if n:
                output.append(f"    📊 {n['calories']}kcal | 단백질 {n['protein_g']}g | 당분 {n['sugar_g']}g | 카페인 {n['caffeine_mg']}mg")
            
            output.append(f"    💡 {rec['reason']}")
        
        output.append("\n" + "=" * 60)
        
        return "\n".join(output)
    
    def close(self):
        if self.loader:
            self.loader.close()
