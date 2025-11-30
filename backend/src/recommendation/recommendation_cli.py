"""
추천 시스템 CLI 인터페이스
main.py에서 호출할 대화형 인터페이스
"""
import sys
import time
from .recommendation_service import RecommendationService


def run_recommendation_demo():
    """추천 시스템 대화형 데모 실행"""
    print("=" * 60)
    print("🍽️  고객 요청 기반 메뉴 추천 시스템")
    print("=" * 60)

    service = RecommendationService()

    # 데이터 소스 선택
    print("\n데이터 소스를 선택하세요:")
    print("1. JSON 파일 (테스트용)")
    print("2. MySQL 데이터베이스")

    choice = input("\n선택 (1 또는 2): ").strip()

    if choice == '1':
        source = 'json'
        print("\n✅ JSON 파일에서 데이터를 로드합니다.")
    elif choice == '2':
        source = 'mysql'
        print("\n✅ MySQL 데이터베이스에서 데이터를 로드합니다.")
    else:
        print("\n❌ 잘못된 선택입니다.")
        return

    # 추천 루프
    print("\n" + "=" * 60)
    print("무엇을 찾고 계신가요? (종료하려면 'exit' 입력)")
    print("=" * 60)

    while True:
        print("\n💬 고객 요청 예시:")
        print("   - 칼로리 낮은 음료 추천해줘")
        print("   - 고단백 메인 메뉴 찾아줘")
        print("   - 카페인 없는 디저트 뭐있어?")
        print("   - 다이어트 중인데 뭐 먹을까")

        customer_request = input("\n👤 당신: ").strip()

        if customer_request.lower() in ['exit', '종료', 'quit', 'q']:
            print("\n👋 추천 시스템을 종료합니다.")
            break

        if not customer_request:
            print("\n⚠️  요청을 입력해주세요.")
            continue

        try:
            # 추천 실행
            start = time.time()
            print("\n🤖 AI가 요청을 분석 중...")
            result = service.get_recommendations(customer_request, source=source)

            # 결과 출력
            if result['success']:
                print(f"✅ 분석 완료: {result['parsed_intent'].get('explanation', '')}")
                print(service.format_output(result))
            else:
                print(f"\n❌ 오류 발생: {result['error']}")
            
            end = time.time()
            print(f"실행 시간: {end - start:.4f}초")

        except KeyboardInterrupt:
            print("\n\n👋 중단되었습니다.")
            break
        except Exception as e:
            print(f"\n❌ 예상치 못한 오류: {e}")
            print("다시 시도해주세요.")

    # 종료
    service.close()
