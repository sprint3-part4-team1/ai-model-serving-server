import os
from dotenv import load_dotenv
from llm.llm_router import get_llm_router

# 환경변수 로드
load_dotenv()

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

if __name__ == "__main__":
    test_llm_router()