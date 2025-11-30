"""
시스템 전역 상수 정의
"""
import os
from pathlib import Path
# ============================================
# 프로젝트 경로
# ============================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ============================================
# 추천 시스템 설정
# ============================================
MAX_RECOMMENDATIONS = 3

# ============================================
# 영양소 필터 기준값 (kcal, g, mg)
# ============================================

# 칼로리 (kcal)
CALORIE_LOW_THRESHOLD = 300
CALORIE_HIGH_THRESHOLD = 500

# 단백질 (g)
PROTEIN_LOW_THRESHOLD = 10
PROTEIN_HIGH_THRESHOLD = 20

# 카페인 (mg)
CAFFEINE_LOW_THRESHOLD = 100

# 당분 (g)
SUGAR_LOW_THRESHOLD = 15
SUGAR_HIGH_THRESHOLD = 25

# ============================================
# LLM 설정
# ============================================
GPT_MODEL = "gpt-5.1"
GPT5_MODEL = "gpt-5.1"
GPT4_MODEL = "gpt-4.1"
GEMINI_MODEL = "gemini-2.5-flash"

DEFAULT_REASONING = {"effort": "low"}      # ✅ dict 형태
DEFAULT_TEXT = {"verbosity": "low"}        # ✅ dict 형태

RECOMMENDATION_REASONING = {"effort": "medium"}
RECOMMENDATION_TEXT = {"verbosity": "medium"}

# ============================================
# 정렬 옵션
# ============================================
SORT_OPTIONS = [
    "calories_asc",
    "calories_desc",
    "protein_asc",
    "protein_desc",
    "price_asc",
    "price_desc",
    "sugar_asc",
    "sugar_desc"
]

DEFAULT_SORT = "price_asc"
