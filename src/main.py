# main.py
import os
from dotenv import load_dotenv

# .env 로드 (프로그램 시작 시 한 번만)
load_dotenv()

from nutrition_service import compute_nutrition_for_item
from story_service import generate_story_for_item

if __name__ == "__main__":
    # 예시: 까르보나라 메뉴 아이템
    compute_nutrition_for_item(1)
    story = generate_story_for_item(1)  # 예: 까르보나라
    print("스토리 결과:", story)
