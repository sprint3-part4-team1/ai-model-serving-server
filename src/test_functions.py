# test_functions.py
import os
from dotenv import load_dotenv
from llm.llm_router import get_llm_router
from recommendation.recommendation_service import RecommendationService
from recommendation.intent_parser import IntentParser
from recommendation.data_loader import DataLoader
import time

# 환경변수 로드
load_dotenv()
    
def test_dataloader():
    loader = DataLoader(source='mysql')
    
    print("=" * 60)
    print("첫 번째 로드 (DB 쿼리)")
    print("=" * 60)
    start = time.time()
    data1 = loader.load(store_id=1)
    elapsed1 = time.time() - start
    print(f"⏱️  시간: {elapsed1:.3f}s")
    print(f"📊 메뉴 아이템: {len(data1['menu_items'])}개")
    print(f"📊 영양 정보: {len(data1['nutrition_estimates'])}개")
    print(f"📊 메뉴 카테고리: {len(data1['menus'])}개")
    
    print("\n" + "=" * 60)
    print("두 번째 로드 (캐시)")
    print("=" * 60)
    start = time.time()
    data2 = loader.load(store_id=1)
    elapsed2 = time.time() - start
    print(f"⏱️  시간: {elapsed2:.3f}s")
    print(f"🚀 속도 향상: {(elapsed1/elapsed2):.1f}배 빠름!")
    
    print("\n" + "=" * 60)
    print("캐시 정보")
    print("=" * 60)
    cache_info = loader.get_cache_info()
    for key, info in cache_info.items():
        print(f"  {key}:")
        print(f"    - 나이: {info['age']}")
        print(f"    - 남은 TTL: {info['remaining_ttl']}")
    
    loader.close()

def test_intentparser():
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

def test_llm_router():
    """LLM Router 테스트"""
    router = get_llm_router()

    test_prompt = """
    다음 요청을 분석하세요: "칼로리 낮은 음료 추천"

    JSON 형식으로 응답:
    {
        "category": "음료",
        "filter": "칼로리 낮음"
    }
    """

    # 1. 일반 호출
    result = router.create_response(test_prompt)
    print(f"사용된 모델: {result['model_used']}")
    print(f"응답 시간: {result['elapsed_time']:.2f}s")
    print(f"응답: {result['response']}")

    # 2. JSON 파싱
    parsed = router.parse_json_response(result)
    print(f"파싱 결과: {parsed['data']}")

    # 성능 요약
    summary = router.get_performance_summary()
    print("성능 요약: {summary}")

    # 4. 메트릭 저장
    router.save_metrics("test_metrics.json")

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
    # test_with_llm_router()
    # test_llm_router()
    # test_dataloader()
    # test_intentparser()
