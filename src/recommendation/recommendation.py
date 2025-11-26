"""
메뉴 추천 엔진
필터링, 정렬, 추천 문구 생성을 담당
"""
from recommendation.gpt_client import get_gpt_client
from constants import (
    MAX_RECOMMENDATIONS,
    CALORIE_LOW_THRESHOLD,
    CALORIE_HIGH_THRESHOLD,
    PROTEIN_LOW_THRESHOLD,
    PROTEIN_HIGH_THRESHOLD,
    CAFFEINE_LOW_THRESHOLD,
    SUGAR_LOW_THRESHOLD,
    SUGAR_HIGH_THRESHOLD,
    RECOMMENDATION_REASONING_EFFORT,
    RECOMMENDATION_TEXT_VERBOSITY,
    DEFAULT_SORT
)

class MenuRecommender:
    """메뉴 추천 엔진"""
    
    def __init__(self):
        self.gpt_client = get_gpt_client()
    
    def filter_menus(self, menu_items, nutrition_data, filter_conditions):
        """
        필터 조건에 따라 메뉴 필터링
        
        Args:
            menu_items (list): 전체 메뉴 리스트
            nutrition_data (list): 영양소 정보 리스트
            filter_conditions (dict): 필터 조건
        
        Returns:
            list: 필터링된 메뉴 리스트
        """
        # 영양소 정보를 item_id로 매핑
        nutrition_map = {n['item_id']: n for n in nutrition_data}
        
        # 메뉴와 영양소 결합 (영양소 없어도 포함)
        combined = []
        for item in menu_items:
            combined.append({
                **item,
                'nutrition': nutrition_map.get(item['id'], None)
            })
        
        filtered = combined.copy()
        
        # menu_id 필터
        if filter_conditions.get('menu_id'):
            menu_id = filter_conditions['menu_id']
            filtered = [m for m in filtered if m.get('menu_id') == menu_id]
        
        # 영양소 있는 것/없는 것 분리
        has_nutrition = [m for m in filtered if m['nutrition'] is not None]
        no_nutrition = [m for m in filtered if m['nutrition'] is None]
        
        # 영양소 필터 조건 체크
        has_nutrition_filter = any([
            filter_conditions.get('calorie'),
            filter_conditions.get('protein'),
            filter_conditions.get('caffeine'),
            filter_conditions.get('sugar')
        ])
        
        # 영양소 필터 적용 (nutrition 있는 것만)
        if has_nutrition_filter and has_nutrition:
            # 칼로리 필터
            if filter_conditions.get('calorie'):
                cal_type = filter_conditions['calorie']
                if cal_type == 'low':
                    has_nutrition = [m for m in has_nutrition if m['nutrition']['calories'] < CALORIE_LOW_THRESHOLD]
                elif cal_type == 'high':
                    has_nutrition = [m for m in has_nutrition if m['nutrition']['calories'] > CALORIE_HIGH_THRESHOLD]
                elif cal_type == 'medium':
                    has_nutrition = [m for m in has_nutrition if CALORIE_LOW_THRESHOLD <= m['nutrition']['calories'] <= CALORIE_HIGH_THRESHOLD]
            
            # 단백질 필터
            if filter_conditions.get('protein'):
                protein_type = filter_conditions['protein']
                if protein_type == 'high':
                    has_nutrition = [m for m in has_nutrition if m['nutrition']['protein_g'] > PROTEIN_HIGH_THRESHOLD]
                elif protein_type == 'low':
                    has_nutrition = [m for m in has_nutrition if m['nutrition']['protein_g'] < PROTEIN_LOW_THRESHOLD]
                elif protein_type == 'medium':
                    has_nutrition = [m for m in has_nutrition if PROTEIN_LOW_THRESHOLD <= m['nutrition']['protein_g'] <= PROTEIN_HIGH_THRESHOLD]
            
            # 카페인 필터
            if filter_conditions.get('caffeine'):
                caffeine_type = filter_conditions['caffeine']
                if caffeine_type == 'none':
                    has_nutrition = [m for m in has_nutrition if m['nutrition']['caffeine_mg'] == 0]
                elif caffeine_type == 'low':
                    has_nutrition = [m for m in has_nutrition if 0 < m['nutrition']['caffeine_mg'] <= CAFFEINE_LOW_THRESHOLD]
                elif caffeine_type == 'high':
                    has_nutrition = [m for m in has_nutrition if m['nutrition']['caffeine_mg'] > CAFFEINE_LOW_THRESHOLD]
            
            # 당분 필터
            if filter_conditions.get('sugar'):
                sugar_type = filter_conditions['sugar']
                if sugar_type == 'low':
                    has_nutrition = [m for m in has_nutrition if m['nutrition']['sugar_g'] < SUGAR_LOW_THRESHOLD]
                elif sugar_type == 'high':
                    has_nutrition = [m for m in has_nutrition if m['nutrition']['sugar_g'] > SUGAR_HIGH_THRESHOLD]
                elif sugar_type == 'medium':
                    has_nutrition = [m for m in has_nutrition if SUGAR_LOW_THRESHOLD <= m['nutrition']['sugar_g'] <= SUGAR_HIGH_THRESHOLD]
            
            # 영양소 필터 조건이 있으면 영양소 있는 것만 반환
            filtered = has_nutrition
        else:
            # 영양소 필터 없으면 모두 포함
            filtered = has_nutrition + no_nutrition
        
        return filtered
    
    def sort_menus(self, menus, sort_by):
        """메뉴 정렬"""
        nutrition_sorts = ['calories_asc', 'calories_desc', 'protein_asc', 
                          'protein_desc', 'sugar_asc', 'sugar_desc']
        
        if sort_by in nutrition_sorts:
            with_nutrition = [m for m in menus if m['nutrition'] is not None]
            without_nutrition = [m for m in menus if m['nutrition'] is None]
            
            sort_map = {
                'calories_asc': lambda m: m['nutrition']['calories'],
                'calories_desc': lambda m: -m['nutrition']['calories'],
                'protein_desc': lambda m: -m['nutrition']['protein_g'],
                'protein_asc': lambda m: m['nutrition']['protein_g'],
                'sugar_asc': lambda m: m['nutrition']['sugar_g'],
                'sugar_desc': lambda m: -m['nutrition']['sugar_g']
            }
            
            if with_nutrition:
                sorted_with = sorted(with_nutrition, key=sort_map[sort_by])
                return sorted_with + without_nutrition
            else:
                return without_nutrition
        else:
            sort_map = {
                'price_asc': lambda m: m['price'],
                'price_desc': lambda m: -m['price']
            }
            return sorted(menus, key=sort_map.get(sort_by, lambda m: m['price']))
    
    def generate_recommendation_text(self, selected_menus, customer_request):
        """추천 문구 생성"""
        menu_texts = []
        for menu in selected_menus:
            n = menu.get('nutrition')
            
            if n:
                text = f"""
                메뉴명: {menu['name']}
                카테고리: {menu.get('menu_name', '일반')}
                설명: {menu['description']}
                가격: {menu['price']:,}원
                칼로리: {n['calories']}kcal / 단백질: {n['protein_g']}g / 당분: {n['sugar_g']}g / 카페인: {n['caffeine_mg']}mg
                """
            else:
                text = f"""
                메뉴명: {menu['name']}
                카테고리: {menu.get('menu_name', '일반')}
                설명: {menu['description']}
                가격: {menu['price']:,}원
                """
            menu_texts.append(text)
        
        combined_prompt = f"""
        당신은 메뉴 추천 전문가입니다.

        고객 요청: "{customer_request}"

        추천 메뉴:
        {''.join(menu_texts)}

        각 메뉴를 왜 추천하는지 1-2문장으로 설명하세요.

        JSON 형식:
        {{
        "recommendations": [
            {{
            "menu_name": "메뉴 이름",
            "reason": "추천 이유"
            }}
        ]
        }}

        순수 JSON만 반환하세요."""

        try:
            response = self.gpt_client.create_response(
                input_text=combined_prompt,
                reasoning={"effort": RECOMMENDATION_REASONING_EFFORT},
                text={"verbosity": RECOMMENDATION_TEXT_VERBOSITY}
            )
            
            result = self.gpt_client.parse_json_response(response)
            
            if not result or 'recommendations' not in result:
                raise ValueError("GPT 응답 형식 오류")
            
            recommendations = []
            for i, menu in enumerate(selected_menus):
                if i < len(result['recommendations']):
                    reason = result['recommendations'][i].get('reason', "추천드립니다!")
                else:
                    reason = "맛있는 메뉴입니다!"
                
                recommendations.append({
                    "menu": menu,
                    "reason": reason
                })
            
            return recommendations
        
        except Exception as e:
            print(f"⚠️ GPT 추천 문구 생성 실패: {e}, 기본 문구 사용")
            
            recommendations = []
            for menu in selected_menus:
                n = menu.get('nutrition')
                
                if n:
                    reason = f"가격 {menu['price']:,}원, {n['calories']}kcal로 좋은 선택입니다!"
                else:
                    reason = f"{menu.get('menu_name', '')} 카테고리의 인기 메뉴입니다!"
                
                recommendations.append({
                    "menu": menu,
                    "reason": reason
                })
            
            return recommendations
    
    def recommend(self, menu_items, nutrition_data, parsed_intent):
        """전체 추천 프로세스"""
        # 1. 필터링
        filtered = self.filter_menus(
            menu_items, 
            nutrition_data, 
            parsed_intent.get('filter_conditions', {})
        )
        
        # 2. 정렬
        sorted_menus = self.sort_menus(
            filtered, 
            parsed_intent.get('sort_by', DEFAULT_SORT)
        )

        # 3. 상위 N개 선택
        limit = parsed_intent.get('limit', MAX_RECOMMENDATIONS)
        top_menus = sorted_menus[:limit]
        
        # 4. 추천 문구 생성
        customer_request = parsed_intent.get('explanation', '추천 메뉴')
        recommendations = self.generate_recommendation_text(top_menus, customer_request)
        
        return {
            "total_found": len(filtered),
            "recommendations": recommendations
        }
