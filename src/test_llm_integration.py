# test_llm_integration.py
from recommendation.recommendation_service import RecommendationService

def test_with_llm_router():
    """LLMRouter 통합 테스트"""
    service = RecommendationService()
    
    test_cases = [
        ("음료 추천해줘", 2),
        ("칼로리 낮은 음료", 2),
        ("고단백 메뉴", 1),
    ]
    
    for request, store_id in test_cases:
        print(f"\n{'='*80}")
        print(f"🔍 요청: {request} (Store {store_id})")
        print('='*80)
        
        result = service.get_recommendations(
            request, 
            source='mysql', 
            store_id=store_id
        )
        
        output = service.format_output(result)
        print(output)
    
    service.close()

if __name__ == "__main__":
    test_with_llm_router()
