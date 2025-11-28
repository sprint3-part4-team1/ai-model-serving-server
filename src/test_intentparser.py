import os
from dotenv import load_dotenv
from recommendation.intent_parser import IntentParser

# 환경변수 로드
load_dotenv()


if __name__ == "__main__":
    parser = IntentParser()
    
    test_menus = [
        {"id": 4, "name": "시그니처 메뉴"},
        {"id": 5, "name": "음료"}
    ]
    
    test_cases = [
        "음료 추천해줘",
        "칼로리 낮은 음료",
        "추운 날 먹기 좋은 메뉴",
        "다이어트 중인데 뭐 먹을까"
    ]
    
    for request in test_cases:
        print(f"\n{'='*60}")
        print(f"요청: {request}")
        print('='*60)
        
        result = parser.parse_customer_request(request, test_menus)
        
        print(f"✅ 사용 모델: {result.get('_meta', {}).get('model_used', 'unknown')}")
        print(f"⏱️  응답 시간: {result.get('_meta', {}).get('elapsed_time', 0):.2f}s")
        print(f"📊 결과: {result.get('filter_conditions', {})}")
        print(f"💡 설명: {result.get('explanation', '')}")