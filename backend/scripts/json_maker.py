import json
from datetime import datetime

# 현재 시간
now = "2025-11-24 18:00:00"

# ===== Store 2: 부산카페 =====
stores = [
    {
        "id": 2,
        "name": "부산카페",
        "address": "부산광역시 해운대구 해변로 123",
        "phone": "051-987-6543",
        "created_at": now,
        "updated_at": now
    }
]

# ===== Menus =====
menus = [
    {
        "id": 4,
        "store_id": 2,
        "name": "시그니처 메뉴",
        "description": "부산카페만의 특별한 메뉴",
        "created_at": now,
        "updated_at": now
    },
    {
        "id": 5,
        "store_id": 2,
        "name": "음료",
        "description": "신선한 음료 모음",
        "created_at": now,
        "updated_at": now
    }
]

# ===== Menu Items (10개) =====
menu_items = [
    # 시그니처 메뉴 (5개)
    {
        "id": 21,
        "menu_id": 4,
        "name": "해운대 브런치 세트",
        "description": "에그베네딕트와 샐러드 세트",
        "price": 18000,
        "is_available": True,
        "image_url": "/img/brunch_set.png",
        "created_at": now,
        "updated_at": now
    },
    {
        "id": 22,
        "menu_id": 4,
        "name": "광안리 샌드위치",
        "description": "신선한 야채와 치킨 샌드위치",
        "price": 9500,
        "is_available": True,
        "image_url": "/img/sandwich.png",
        "created_at": now,
        "updated_at": now
    },
    {
        "id": 23,
        "menu_id": 4,
        "name": "부산 어묵 파스타",
        "description": "부산 특산 어묵이 들어간 퓨전 파스타",
        "price": 14000,
        "is_available": True,
        "image_url": "/img/eomuk_pasta.png",
        "created_at": now,
        "updated_at": now
    },
    {
        "id": 24,
        "menu_id": 4,
        "name": "해물 크림 리조또",
        "description": "신선한 해산물 크림 리조또",
        "price": 16000,
        "is_available": True,
        "image_url": "/img/seafood_risotto.png",
        "created_at": now,
        "updated_at": now
    },
    {
        "id": 25,
        "menu_id": 4,
        "name": "바다 샐러드",
        "description": "해초와 새우가 들어간 헬시 샐러드",
        "price": 12000,
        "is_available": True,
        "image_url": "/img/ocean_salad.png",
        "created_at": now,
        "updated_at": now
    },
    
    # 음료 (5개)
    {
        "id": 26,
        "menu_id": 5,
        "name": "제주 그린티 라떼",
        "description": "제주산 녹차로 만든 라떼",
        "price": 5500,
        "is_available": True,
        "image_url": "/img/greentea_latte.png",
        "created_at": now,
        "updated_at": now
    },
    {
        "id": 27,
        "menu_id": 5,
        "name": "부산 밀크티",
        "description": "달콤한 밀크티",
        "price": 5000,
        "is_available": True,
        "image_url": "/img/milktea.png",
        "created_at": now,
        "updated_at": now
    },
    {
        "id": 28,
        "menu_id": 5,
        "name": "레몬 에이드",
        "description": "상큼한 레몬 에이드",
        "price": 5500,
        "is_available": True,
        "image_url": "/img/lemonade.png",
        "created_at": now,
        "updated_at": now
    },
    {
        "id": 29,
        "menu_id": 5,
        "name": "콜드브루",
        "description": "부드러운 콜드브루 커피",
        "price": 4500,
        "is_available": True,
        "image_url": "/img/coldbrew.png",
        "created_at": now,
        "updated_at": now
    },
    {
        "id": 30,
        "menu_id": 5,
        "name": "유자 스무디",
        "description": "상큼한 유자 스무디",
        "price": 6500,
        "is_available": True,
        "image_url": "/img/yuja_smoothie.png",
        "created_at": now,
        "updated_at": now
    }
]

# ===== Item Ingredients (간단하게 각 메뉴당 2-3개씩) =====
item_ingredients = [
    # 21. 해운대 브런치 세트
    {"id": 68, "item_id": 21, "ingredient_name": "계란", "quantity_unit": "개", "quantity_value": 2, "notes": "유정란"},
    {"id": 69, "item_id": 21, "ingredient_name": "베이컨", "quantity_unit": "g", "quantity_value": 50, "notes": "훈제"},
    {"id": 70, "item_id": 21, "ingredient_name": "아보카도", "quantity_unit": "g", "quantity_value": 80, "notes": "멕시코산"},
    
    # 22. 광안리 샌드위치
    {"id": 71, "item_id": 22, "ingredient_name": "닭가슴살", "quantity_unit": "g", "quantity_value": 120, "notes": "국내산"},
    {"id": 72, "item_id": 22, "ingredient_name": "양상추", "quantity_unit": "g", "quantity_value": 50, "notes": "신선한"},
    {"id": 73, "item_id": 22, "ingredient_name": "토마토", "quantity_unit": "g", "quantity_value": 40, "notes": "완숙"},
    
    # 23. 부산 어묵 파스타
    {"id": 74, "item_id": 23, "ingredient_name": "파스타 면", "quantity_unit": "g", "quantity_value": 120, "notes": "스파게티"},
    {"id": 75, "item_id": 23, "ingredient_name": "부산 어묵", "quantity_unit": "g", "quantity_value": 100, "notes": "삼진 어묵"},
    {"id": 76, "item_id": 23, "ingredient_name": "크림", "quantity_unit": "ml", "quantity_value": 60, "notes": "생크림"},
    
    # 24. 해물 크림 리조또
    {"id": 77, "item_id": 24, "ingredient_name": "쌀", "quantity_unit": "g", "quantity_value": 100, "notes": "아르보리오"},
    {"id": 78, "item_id": 24, "ingredient_name": "새우", "quantity_unit": "g", "quantity_value": 80, "notes": "국내산"},
    {"id": 79, "item_id": 24, "ingredient_name": "관자", "quantity_unit": "g", "quantity_value": 70, "notes": "생관자"},
    
    # 25. 바다 샐러드
    {"id": 80, "item_id": 25, "ingredient_name": "미역", "quantity_unit": "g", "quantity_value": 50, "notes": "국내산"},
    {"id": 81, "item_id": 25, "ingredient_name": "새우", "quantity_unit": "g", "quantity_value": 60, "notes": "냉동"},
    
    # 26. 제주 그린티 라떼
    {"id": 82, "item_id": 26, "ingredient_name": "녹차 가루", "quantity_unit": "g", "quantity_value": 10, "notes": "제주산"},
    {"id": 83, "item_id": 26, "ingredient_name": "우유", "quantity_unit": "ml", "quantity_value": 200, "notes": "국내산"},
    
    # 27. 부산 밀크티
    {"id": 84, "item_id": 27, "ingredient_name": "홍차", "quantity_unit": "g", "quantity_value": 8, "notes": "얼그레이"},
    {"id": 85, "item_id": 27, "ingredient_name": "우유", "quantity_unit": "ml", "quantity_value": 180, "notes": "국내산"},
    
    # 28. 레몬 에이드
    {"id": 86, "item_id": 28, "ingredient_name": "레몬", "quantity_unit": "g", "quantity_value": 100, "notes": "생과일"},
    {"id": 87, "item_id": 28, "ingredient_name": "탄산수", "quantity_unit": "ml", "quantity_value": 200, "notes": "스파클링"},
    
    # 29. 콜드브루
    {"id": 88, "item_id": 29, "ingredient_name": "원두", "quantity_unit": "g", "quantity_value": 20, "notes": "에티오피아산"},
    {"id": 89, "item_id": 29, "ingredient_name": "물", "quantity_unit": "ml", "quantity_value": 250, "notes": "정수"},
    
    # 30. 유자 스무디
    {"id": 90, "item_id": 30, "ingredient_name": "유자청", "quantity_unit": "g", "quantity_value": 80, "notes": "국내산"},
    {"id": 91, "item_id": 30, "ingredient_name": "요거트", "quantity_unit": "g", "quantity_value": 100, "notes": "플레인"},
]

# ===== Nutrition Estimates (10개) =====
nutrition_estimates = [
    # 21. 해운대 브런치 세트
    {
        "id": 21,
        "item_id": 21,
        "calories": 620,
        "sugar_g": 12.0,
        "caffeine_mg": 0,
        "protein_g": 32.0,
        "fat_g": 38.0,
        "carbs_g": 35.0,
        "confidence": 0.89,
        "last_computed_at": now
    },
    # 22. 광안리 샌드위치
    {
        "id": 22,
        "item_id": 22,
        "calories": 380,
        "sugar_g": 8.0,
        "caffeine_mg": 0,
        "protein_g": 28.0,
        "fat_g": 12.0,
        "carbs_g": 42.0,
        "confidence": 0.91,
        "last_computed_at": now
    },
    # 23. 부산 어묵 파스타
    {
        "id": 23,
        "item_id": 23,
        "calories": 520,
        "sugar_g": 6.5,
        "caffeine_mg": 0,
        "protein_g": 22.0,
        "fat_g": 18.0,
        "carbs_g": 62.0,
        "confidence": 0.87,
        "last_computed_at": now
    },
    # 24. 해물 크림 리조또
    {
        "id": 24,
        "item_id": 24,
        "calories": 560,
        "sugar_g": 5.0,
        "caffeine_mg": 0,
        "protein_g": 26.0,
        "fat_g": 22.0,
        "carbs_g": 58.0,
        "confidence": 0.88,
        "last_computed_at": now
    },
    # 25. 바다 샐러드
    {
        "id": 25,
        "item_id": 25,
        "calories": 180,
        "sugar_g": 6.0,
        "caffeine_mg": 0,
        "protein_g": 15.0,
        "fat_g": 8.0,
        "carbs_g": 12.0,
        "confidence": 0.90,
        "last_computed_at": now
    },
    # 26. 제주 그린티 라떼
    {
        "id": 26,
        "item_id": 26,
        "calories": 160,
        "sugar_g": 18.0,
        "caffeine_mg": 60,
        "protein_g": 6.0,
        "fat_g": 5.0,
        "carbs_g": 22.0,
        "confidence": 0.93,
        "last_computed_at": now
    },
    # 27. 부산 밀크티
    {
        "id": 27,
        "item_id": 27,
        "calories": 200,
        "sugar_g": 22.0,
        "caffeine_mg": 45,
        "protein_g": 5.0,
        "fat_g": 6.0,
        "carbs_g": 28.0,
        "confidence": 0.92,
        "last_computed_at": now
    },
    # 28. 레몬 에이드
    {
        "id": 28,
        "item_id": 28,
        "calories": 120,
        "sugar_g": 25.0,
        "caffeine_mg": 0,
        "protein_g": 0.5,
        "fat_g": 0.2,
        "carbs_g": 30.0,
        "confidence": 0.94,
        "last_computed_at": now
    },
    # 29. 콜드브루
    {
        "id": 29,
        "item_id": 29,
        "calories": 10,
        "sugar_g": 0,
        "caffeine_mg": 200,
        "protein_g": 1.0,
        "fat_g": 0,
        "carbs_g": 2.0,
        "confidence": 0.97,
        "last_computed_at": now
    },
    # 30. 유자 스무디
    {
        "id": 30,
        "item_id": 30,
        "calories": 220,
        "sugar_g": 32.0,
        "caffeine_mg": 0,
        "protein_g": 5.0,
        "fat_g": 3.5,
        "carbs_g": 42.0,
        "confidence": 0.90,
        "last_computed_at": now
    }
]

# ===== 전체 데이터 통합 =====
sample_data_v3 = {
    "stores": stores,
    "menus": menus,
    "menu_items": menu_items,
    "item_ingredients": item_ingredients,
    "nutrition_estimates": nutrition_estimates
}

# JSON 파일 저장
with open('samples/menu_sample_data_v3.json', 'w', encoding='utf-8') as f:
    json.dump(sample_data_v3, f, ensure_ascii=False, indent=2)

print("=" * 60)
print("🎉 menu_sample_data_v3.json 생성 완료!")
print("=" * 60)
print(f"📍 Store: 부산카페 (ID: 2)")
print(f"📋 Menus: {len(menus)}개")
print(f"🍽️  Menu Items: {len(menu_items)}개")
print(f"   ├─ 시그니처: 5개")
print(f"   └─ 음료: 5개")
print(f"🥬 Item Ingredients: {len(item_ingredients)}개")
print(f"🔬 Nutrition Estimates: {len(nutrition_estimates)}개")
print("=" * 60)
