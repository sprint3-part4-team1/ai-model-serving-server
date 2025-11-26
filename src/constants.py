"""
시스템 전역 상수 정의
"""

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
# GPT 설정
# ============================================
GPT_MODEL = "5-mini"

DEFAULT_REASONING  = "low"
DEFAULT_TEXT  = "low"

RECOMMENDATION_REASONING_EFFORT = "medium"
RECOMMENDATION_TEXT_VERBOSITY = "medium"

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
