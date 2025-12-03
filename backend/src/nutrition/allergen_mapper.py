"""
알레르기 유발 재료 매핑 시스템
땅콩, 견과류 등을 폭넓게 인식하여 알레르기 경고
"""

from typing import List, Set, Dict

class AllergenMapper:
    """
    재료명 → 알레르기 유형 매핑
    폭넓은 인식을 위한 키워드 기반 매칭
    """

    # 알레르기 유형별 키워드 매핑
    ALLERGEN_MAP = {
        "견과류": [
            "땅콩", "peanut", "피넛",
            "호두", "walnut",
            "아몬드", "almond",
            "캐슈너트", "캐슈넛", "cashew",
            "피스타치오", "pistachio",
            "마카다미아", "macadamia",
            "헤이즐넛", "hazelnut",
            "피칸", "pecan",
            "잣", "pine nut",
            "밤", "chestnut",
            "견과", "nut", "nuts",
            "잡곡", "mixed nuts"
        ],

        "우유/유제품": [
            "우유", "milk", "밀크",
            "치즈", "cheese",
            "버터", "butter",
            "크림", "cream",
            "요거트", "요구르트", "yogurt",
            "생크림", "whipping cream",
            "휘핑크림",
            "라떼", "latte",
            "카푸치노", "cappuccino",
            "모카", "mocha",
            "유청", "whey",
            "카제인", "casein",
            "유제품", "dairy"
        ],

        "계란": [
            "계란", "달걀", "egg",
            "에그", "egg",
            "난황", "yolk",
            "난백", "egg white",
            "계란프라이",
            "수란",
            "마요네즈", "mayonnaise", "mayo"
        ],

        "글루텐/밀": [
            "밀가루", "flour", "wheat",
            "밀", "wheat",
            "글루텐", "gluten",
            "빵", "bread",
            "파스타", "pasta",
            "면", "noodle",
            "국수",
            "우동", "udon",
            "라면", "ramen",
            "시리얼", "cereal",
            "맥주", "beer",
            "보리", "barley",
            "호밀", "rye"
        ],

        "갑각류": [
            "새우", "shrimp", "prawn",
            "게", "crab",
            "랍스터", "lobster",
            "가재", "crayfish",
            "크릴", "krill",
            "갑각류", "shellfish", "crustacean"
        ],

        "생선": [
            "연어", "salmon",
            "참치", "tuna",
            "고등어", "mackerel",
            "광어", "flounder",
            "명태", "pollack",
            "대구", "cod",
            "멸치", "anchovy",
            "생선", "fish",
            "회", "sashimi",
            "피쉬", "fish"
        ],

        "조개류": [
            "조개", "clam", "shellfish",
            "굴", "oyster",
            "홍합", "mussel",
            "바지락",
            "전복", "abalone",
            "소라",
            "관자", "scallop"
        ],

        "콩": [
            "대두", "soybean", "soy",
            "콩", "bean",
            "두부", "tofu",
            "된장", "soybean paste",
            "간장", "soy sauce",
            "청국장",
            "낫토", "natto",
            "콩나물",
            "완두콩", "pea",
            "렌틸콩", "lentil",
            "병아리콩", "chickpea",
            "강낭콩", "kidney bean"
        ],

        "참깨": [
            "참깨", "sesame",
            "깨", "sesame",
            "세서미", "sesame",
            "참기름", "sesame oil"
        ],

        "복숭아": [
            "복숭아", "peach",
            "피치", "peach"
        ],

        "토마토": [
            "토마토", "tomato"
        ],

        "돼지고기": [
            "돼지고기", "pork",
            "삼겹살",
            "목살",
            "항정살",
            "베이컨", "bacon",
            "햄", "ham",
            "소시지", "sausage"
        ],

        "쇠고기": [
            "쇠고기", "beef",
            "소고기",
            "등심",
            "안심",
            "갈비",
            "스테이크", "steak"
        ],

        "닭고기": [
            "닭고기", "chicken",
            "치킨",
            "닭",
            "닭다리",
            "닭가슴살"
        ]
    }

    @classmethod
    def detect_allergens(cls, ingredients: List[str]) -> Dict[str, List[str]]:
        """
        재료 리스트에서 알레르기 유발 재료 감지

        Args:
            ingredients: 재료명 리스트 (예: ["우유", "계란", "밀가루"])

        Returns:
            {
                "견과류": ["땅콩", "호두"],
                "우유/유제품": ["우유", "크림"],
                ...
            }
        """
        detected = {}

        for ingredient in ingredients:
            ingredient_lower = ingredient.lower().strip()

            # 각 알레르기 유형별로 확인
            for allergen_type, keywords in cls.ALLERGEN_MAP.items():
                for keyword in keywords:
                    # 키워드가 재료명에 포함되어 있으면
                    if keyword.lower() in ingredient_lower:
                        if allergen_type not in detected:
                            detected[allergen_type] = []

                        # 중복 방지
                        if ingredient not in detected[allergen_type]:
                            detected[allergen_type].append(ingredient)
                        break

        return detected

    @classmethod
    def get_allergen_warning(cls, allergens: Dict[str, List[str]]) -> str:
        """
        알레르기 경고 문구 생성

        Args:
            allergens: detect_allergens() 반환값

        Returns:
            알레르기 경고 문구 (예: "⚠️ 견과류, 우유/유제품 포함")
        """
        if not allergens:
            return ""

        allergen_types = list(allergens.keys())

        if len(allergen_types) == 1:
            return f"⚠️ {allergen_types[0]} 포함"
        elif len(allergen_types) == 2:
            return f"⚠️ {allergen_types[0]}, {allergen_types[1]} 포함"
        else:
            # 3개 이상이면 앞 2개만 표시
            return f"⚠️ {allergen_types[0]}, {allergen_types[1]} 등 포함"

    @classmethod
    def get_detailed_allergen_info(cls, allergens: Dict[str, List[str]]) -> str:
        """
        알레르기 상세 정보 생성

        Args:
            allergens: detect_allergens() 반환값

        Returns:
            상세 알레르기 정보 (예: "견과류(땅콩, 호두), 우유/유제품(우유, 크림)")
        """
        if not allergens:
            return "알레르기 유발 재료 없음"

        details = []
        for allergen_type, ingredients in allergens.items():
            ingredient_str = ", ".join(ingredients[:3])  # 최대 3개까지만
            if len(ingredients) > 3:
                ingredient_str += " 등"
            details.append(f"{allergen_type}({ingredient_str})")

        return ", ".join(details)


# 사용 예시
if __name__ == "__main__":
    # 테스트
    test_ingredients = [
        "우유", "계란", "밀가루", "땅콩", "호두", "새우", "참치", "두부", "참깨"
    ]

    allergens = AllergenMapper.detect_allergens(test_ingredients)
    print("감지된 알레르기 유발 재료:")
    for allergen_type, ingredients in allergens.items():
        print(f"  {allergen_type}: {ingredients}")

    print("\n간단 경고:", AllergenMapper.get_allergen_warning(allergens))
    print("상세 정보:", AllergenMapper.get_detailed_allergen_info(allergens))
