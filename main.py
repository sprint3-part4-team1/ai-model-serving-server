"""
AI 메뉴 추천 시스템 - 메인 실행 파일
"""

import sys
from src.recommendation.recommendation_cli import run_recommendation_demo

def main():
    """메인 메뉴 (라우터 역할만)"""
    while True:
        print("\n" + "=" * 60)
        print("🍽️  AI 메뉴 추천 시스템 - 팀 프로젝트")
        print("=" * 60)
        print("\n어떤 기능을 실행하시겠습니까?")
        print("\n1. 고객 요청 기반 추천 (Part 1)")
        print("2. 메뉴 스토리텔링 (Part 2 - 팀원 B)")
        print("3. 시즈널/이벤트 스토리 (Part 3 - 팀원 C)")
        print("4. 테마 자동 생성 (Part 4 - 팀원 D)")
        print("0. 종료")

        choice = input("\n선택: ").strip()

        if choice == '1':
            # Part 1: 고객 요청 기반 추천
            run_recommendation_demo()
        # elif choice == '2':
        #     # Part 2: 메뉴 스토리텔링
        # elif choice == '3':
        #     # Part 3: 시즈널/이벤트 스토리
        # elif choice == '4':
        #     # Part 4: 테마 자동 생성
        elif choice == '0':
            print("\n👋 프로그램을 종료합니다.")
            sys.exit(0)
        else:
            print("\n❌ 잘못된 선택입니다.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 프로그램이 종료되었습니다.")
        sys.exit(0)
