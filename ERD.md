### ERD
```
Stores (매장)
   └── Menus (메뉴판)
         └── Menu_Items (메뉴 아이템)
               ├── Item_Ingredients (메뉴 재료) → AI 계산에 활용
               └── Nutrition_Estimates (영양 성분 추정치) → 결과 저장
```

1. **stores** (매장)
 - id (INT, PK, AUTO_INCREMENT) : 매장 고유번호
 - name (VARCHAR) : 매장 이름
 - address (VARCHAR) : 매장 주소
 - phone (VARCHAR) : 연락처
 - created_at (DATETIME) : 생성일
 - updated_at (DATETIME) : 수정일

2. **menus** (메뉴판)
 - id (INT, PK, AUTO_INCREMENT) : 메뉴판 고유번호
 - store_id (INT, FK → Stores.id) : 어떤 매장에 속하는지 연결
 - name (VARCHAR) : 메뉴판 이름
 - description (VARCHAR) : 메뉴판 설명
 - created_at (DATETIME) : 생성일
 - updated_at (DATETIME) : 수정일

3. **menu_items** (메뉴 아이템)
 - id (INT, PK, AUTO_INCREMENT) : 메뉴 아이템 고유번호
 - menu_id (INT, FK → Menus.id) : 어떤 메뉴판에 속하는지 연결
 - name (VARCHAR) : 메뉴 이름 (예: 아메리카노, 카푸치노)
 - description (VARCHAR) : 메뉴 설명
 - price (DECIMAL) : 가격
 - is_available (BOOLEAN) : 판매 가능 여부
 - image_url (VARCHAR) : 메뉴 이미지
 - created_at (DATETIME) : 생성일
 - updated_at (DATETIME) : 수정일

4. **item_ingredients** (메뉴 재료)
 - id (INT, PK, AUTO_INCREMENT) : 재료 고유번호
 - item_id (INT, FK → Menu_Items.id) : 어떤 메뉴 아이템에 속하는지 연결
 - ingredient_name (VARCHAR) : 재료 이름 (예: 원두, 우유, 시럽)
 - quantity_unit (VARCHAR) : 단위 (ml, g 등)
 - quantity_value (DECIMAL) : 수량 값
 - notes (VARCHAR) : 추가 설명 (예: 원산지, 특징)

5. **nutrition_estimates** (영양 성분 추정치)
 - id (INT, PK, AUTO_INCREMENT)
 - item_id (INT, FK → Menu_Items.id)
 - calories (DECIMAL) : 칼로리
 - sugar_g (DECIMAL) : 당분 g
 - caffeine_mg (DECIMAL) : 카페인 mg
 - protein_g (DECIMAL) : 단백질 g
 - fat_g (DECIMAL) : 지방 g
 - carbs_g (DECIMAL) : 탄수화물 g
 - confidence (DECIMAL) : AI 추정 신뢰도 (0~1)
 - last_computed_at (DATETIME) : 계산 시점


### 샘플데이터
```
stores:
  - id: 1
    name: "서울카페"
    address: "전북 서울시 노원구 경기로"
    phone: "02-123-4567"
    created_at: "2025-11-17 16:00:00"
    updated_at: "2025-11-17 16:00:00"

menus:
  - id: 1
    store_id: 1
    name: "메인 메뉴"
    description: "기본 음료 메뉴판"
    created_at: "2025-11-17 16:00:00"
  - id: 2
    store_id: 1
    name: "시즌 메뉴"
    description: "겨울 한정 메뉴판"
    created_at: "2025-11-17 16:00:00"

menu_items:
  - id: 1
    menu_id: 1
    name: "아메리카노"
    description: "진한 원두 향의 커피"
    price: 4000
    is_available: true
    image_url: "/img/americano.png"
    created_at: "2025-11-17 16:00:00"
    updated_at: "2025-11-17 16:00:00"
  - id: 2
    menu_id: 1
    name: "카푸치노"
    description: "우유 거품이 올라간 커피"
    price: 4500
    is_available: true
    image_url: "/img/cappuccino.png"
    created_at: "2025-11-17 16:00:00"
    updated_at: "2025-11-17 16:00:00"
  - id: 3
    menu_id: 2
    name: "크리스마스 라떼"
    description: "시나몬 향 가득한 겨울 한정 라떼"
    price: 5500
    is_available: true
    image_url: "/img/xmas_latte.png"
    created_at: "2025-11-17 16:00:00"
    updated_at: "2025-11-17 16:00:00"

item_ingredients:
  - id: 1
    item_id: 1
    ingredient_name: "원두"
    quantity_unit: "g"
    quantity_value: 15
    notes: "콜롬비아산 원두 사용"
  - id: 2
    item_id: 1
    ingredient_name: "물"
    quantity_unit: "ml"
    quantity_value: 200
    notes: "정수기 물"
  - id: 3
    item_id: 2
    ingredient_name: "원두"
    quantity_unit: "g"
    quantity_value: 15
    notes: "에스프레소 샷"
  - id: 4
    item_id: 2
    ingredient_name: "우유"
    quantity_unit: "ml"
    quantity_value: 150
    notes: "국내산 우유"
  - id: 5
    item_id: 2
    ingredient_name: "시나몬 파우더"
    quantity_unit: "g"
    quantity_value: 2
    notes: "겨울 시즌 한정 토핑"
  - id: 6
    item_id: 3
    ingredient_name: "원두"
    quantity_unit: "g"
    quantity_value: 15
    notes: "브라질산 원두"
  - id: 7
    item_id: 3
    ingredient_name: "우유"
    quantity_unit: "ml"
    quantity_value: 180
    notes: "스팀 밀크"
  - id: 8
    item_id: 3
    ingredient_name: "시나몬 시럽"
    quantity_unit: "ml"
    quantity_value: 20
    notes: "크리스마스 한정 시럽"
```