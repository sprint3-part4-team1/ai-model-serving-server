"""
유틸리티 함수 모음
"""

def format_menu_display(menu, nutrition):
    """
    메뉴 정보를 보기 좋게 포맷팅

    Args:
        menu (dict): 메뉴 정보
        nutrition (dict): 영양소 정보

    Returns:
        str: 포맷팅된 문자열
    """
    return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🍽️  {menu['name']} - {menu['price']:,}원
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 {menu['description']}

📊 영양 정보:
   칼로리: {nutrition['calories']} kcal
   단백질: {nutrition['protein_g']}g | 지방: {nutrition['fat_g']}g | 탄수화물: {nutrition['carbs_g']}g
   당분: {nutrition['sugar_g']}g | 카페인: {nutrition['caffeine_mg']}mg

🔬 AI 신뢰도: {nutrition['confidence']*100:.0f}%
"""


def format_recommendation_result(recommendations):
    """
    추천 결과를 보기 좋게 포맷팅

    Args:
        recommendations (list): 추천 메뉴 리스트

    Returns:
        str: 포맷팅된 문자열
    """
    output = "\n" + "="*60 + "\n"
    output += "🎯 추천 메뉴\n"
    output += "="*60 + "\n"

    for i, rec in enumerate(recommendations, 1):
        menu = rec['menu']
        nutrition = menu['nutrition']
        reason = rec['reason']

        output += f"\n[{i}] {menu['name']} - {menu['price']:,}원\n"
        output += f"    {menu['description']}\n"
        output += f"    📊 {nutrition['calories']}kcal | 단백질 {nutrition['protein_g']}g | 당분 {nutrition['sugar_g']}g\n"
        output += f"    💡 {reason}\n"

    output += "\n" + "="*60 + "\n"

    return output


def validate_env_vars():
    """
    필수 환경변수 체크

    Returns:
        dict: 검증 결과
    """
    import os

    required_vars = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'DB_HOST': os.getenv('DB_HOST'),
        'DB_USER': os.getenv('DB_USER'),
        'DB_PASSWORD': os.getenv('DB_PASSWORD'),
        'DB_NAME': os.getenv('DB_NAME')
    }

    missing = [key for key, value in required_vars.items() if not value]

    return {
        'valid': len(missing) == 0,
        'missing': missing
    }


def calculate_nutrition_score(nutrition, goal='balanced'):
    """
    영양소 정보를 기반으로 점수 계산

    Args:
        nutrition (dict): 영양소 정보
        goal (str): 목표 ('balanced', 'low_cal', 'high_protein')

    Returns:
        float: 점수 (0~100)
    """
    if goal == 'low_cal':
        # 칼로리가 낮을수록 높은 점수
        return max(0, 100 - nutrition['calories'] / 10)

    elif goal == 'high_protein':
        # 단백질이 높을수록 높은 점수
        return min(100, nutrition['protein_g'] * 2)

    elif goal == 'balanced':
        # 균형잡힌 영양소 비율
        protein_score = min(50, nutrition['protein_g'] * 1.5)
        cal_score = max(0, 50 - nutrition['calories'] / 20)
        return protein_score + cal_score

    return 50.0
