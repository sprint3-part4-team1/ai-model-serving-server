"""
메뉴 추천 엔진
필터링, 정렬, 추천 문구 생성을 담당
"""
from recommendation.gpt_client import get_gpt_client


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
            list: 필터링된 메뉴 리스트 (영양소 정보 포함)
        """
        # 영양소 정보를 item_id로 매핑
        nutrition_map = {n['item_id']: n for n in nutrition_data}

        # 메뉴와 영양소 결합
        combined = []
        for item in menu_items:
            if item['id'] in nutrition_map:
                combined.append({
                    **item,
                    'nutrition': nutrition_map[item['id']]
                })

        filtered = combined.copy()

        # 카테고리 필터
        if filter_conditions.get('category'):
            category = filter_conditions['category']
            category_map = {
                'main': [1],    # menu_id = 1
                'side': [2],    # menu_id = 2
                'drink': [3]    # menu_id = 3
            }
            if category in category_map:
                allowed_menu_ids = category_map[category]
                filtered = [m for m in filtered if m['menu_id'] in allowed_menu_ids]

        # 칼로리 필터
        if filter_conditions.get('calorie'):
            cal_type = filter_conditions['calorie']
            if cal_type == 'low':
                filtered = [m for m in filtered if m['nutrition']['calories'] < 300]
            elif cal_type == 'high':
                filtered = [m for m in filtered if m['nutrition']['calories'] > 500]

        # 단백질 필터
        if filter_conditions.get('protein'):
            protein_type = filter_conditions['protein']
            if protein_type == 'high':
                filtered = [m for m in filtered if m['nutrition']['protein_g'] > 20]
            elif protein_type == 'low':
                filtered = [m for m in filtered if m['nutrition']['protein_g'] < 10]

        # 카페인 필터
        if filter_conditions.get('caffeine'):
            caffeine_type = filter_conditions['caffeine']
            if caffeine_type == 'none':
                filtered = [m for m in filtered if m['nutrition']['caffeine_mg'] == 0]
            elif caffeine_type == 'high':
                filtered = [m for m in filtered if m['nutrition']['caffeine_mg'] > 100]

        # 당분 필터
        if filter_conditions.get('sugar'):
            sugar_type = filter_conditions['sugar']
            if sugar_type == 'low':
                filtered = [m for m in filtered if m['nutrition']['sugar_g'] < 15]
            elif sugar_type == 'high':
                filtered = [m for m in filtered if m['nutrition']['sugar_g'] > 25]

        return filtered

    def sort_menus(self, menus, sort_by):
        """
        메뉴 정렬

        Args:
            menus (list): 메뉴 리스트
            sort_by (str): 정렬 기준

        Returns:
            list: 정렬된 메뉴 리스트
        """
        sort_map = {
            'calories_asc': lambda m: m['nutrition']['calories'],
            'calories_desc': lambda m: -m['nutrition']['calories'],
            'protein_desc': lambda m: -m['nutrition']['protein_g'],
            'protein_asc': lambda m: m['nutrition']['protein_g'],
            'price_asc': lambda m: m['price'],
            'price_desc': lambda m: -m['price'],
            'sugar_asc': lambda m: m['nutrition']['sugar_g'],
            'sugar_desc': lambda m: -m['nutrition']['sugar_g']
        }

        if sort_by in sort_map:
            return sorted(menus, key=sort_map[sort_by])

        return menus

    def generate_recommendation_text(self, selected_menus, customer_request):
        """
        추천 메뉴에 대한 설명 문구 생성 (GPT 활용)

        Args:
            selected_menus (list): 추천할 메뉴 리스트 (최대 3개)
            customer_request (str): 고객의 원래 요청

        Returns:
            list: 각 메뉴별 추천 문구
                [
                    {
                        "menu": {...},
                        "reason": "이 메뉴를 추천하는 이유"
                    }
                ]
        """
        # 메뉴 정보를 텍스트로 변환
        menu_texts = []
        for menu in selected_menus:
            n = menu['nutrition']
            text = f"""
                메뉴명: {menu['name']}
                설명: {menu['description']}
                가격: {menu['price']:,}원
                칼로리: {n['calories']}kcal
                단백질: {n['protein_g']}g / 지방: {n['fat_g']}g / 탄수화물: {n['carbs_g']}g
                당분: {n['sugar_g']}g / 카페인: {n['caffeine_mg']}mg
                """
            menu_texts.append(text)

        # GPT-5.1용 단일 프롬프트 생성
        combined_prompt = """당신은 메뉴 추천 전문가입니다.
            고객의 요청에 맞는 메뉴를 추천하면서, 각 메뉴를 왜 추천하는지 친근하고 자연스럽게 설명하세요.

            요구사항:
            1. 각 메뉴당 1-2문장으로 간결하게 작성
            2. 영양소 수치를 근거로 제시
            3. 친근하고 따뜻한 톤 사용
            4. 고객의 요청과 연결하여 설명

            응답 형식 (JSON):
            {
            "recommendations": [
                {
                "menu_name": "메뉴 이름",
                "reason": "추천 이유 (1-2문장)"
                }
            ]
            }

            ---

            고객 요청: """" + customer_request + """"

            추천 메뉴 목록:
            """ + ''.join(menu_texts) + """

            위 메뉴들을 고객에게 추천하는 이유를 JSON 형식으로만 작성해주세요. 다른 텍스트는 포함하지 마세요."""

        # GPT-5.1 호출
        response = self.gpt_client.create_response(
            input_text=combined_prompt,
            reasoning={"effort": "medium"},  # 적절한 추론
            text={"verbosity": "medium"}  # 적당한 길이의 응답
        )

        result = self.gpt_client.parse_json_response(response)

        # 메뉴 객체와 추천 이유 결합
        recommendations = []
        for i, menu in enumerate(selected_menus):
            reason = result['recommendations'][i]['reason'] if i < len(result['recommendations']) else "맛있는 메뉴입니다!"
            recommendations.append({
                "menu": menu,
                "reason": reason
            })

        return recommendations

    def recommend(self, menu_items, nutrition_data, parsed_intent):
        """
        전체 추천 프로세스 실행

        Args:
            menu_items (list): 전체 메뉴 리스트
            nutrition_data (list): 영양소 정보 리스트
            parsed_intent (dict): 파싱된 고객 의도

        Returns:
            dict: 추천 결과
                {
                    "total_found": 5,
                    "recommendations": [...]
                }
        """
        # 1. 필터링
        filtered = self.filter_menus(
            menu_items, 
            nutrition_data, 
            parsed_intent.get('filter_conditions', {})
        )

        # 2. 정렬
        sorted_menus = self.sort_menus(
            filtered, 
            parsed_intent.get('sort_by', 'calories_asc')
        )

        # 3. 상위 N개 선택
        limit = parsed_intent.get('limit', 3)
        top_menus = sorted_menus[:limit]

        # 4. 추천 문구 생성
        customer_request = parsed_intent.get('explanation', '추천 메뉴')
        recommendations = self.generate_recommendation_text(top_menus, customer_request)

        return {
            "total_found": len(filtered),
            "recommendations": recommendations
        }
