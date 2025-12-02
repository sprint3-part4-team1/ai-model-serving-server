"""
메뉴 → 재료 → 영양소 자동 분석 시스템
"""

from typing import List, Dict, Any
from datetime import datetime
import json

from ..database import get_session
from ..models import Store, MenuItem, ItemIngredient, NutritionEstimate
from ..llm import get_llm_router




class NutritionAnalyzer:
    """
    메뉴 정보로부터 재료와 영양소를 자동 유추하는 클래스
    """

    def __init__(self, batch_size=10):
        """
        Args:
            batch_size (int): 한 번에 처리할 메뉴 개수
        """
        self.llm_router = get_llm_router()
        self.batch_size = batch_size
    
    def analyze_store(self, store_id: int):
        """
        매장의 모든 메뉴를 분석하여 재료와 영양소 정보 생성
        
        Args:
            store_id (int): 매장 ID
        """
        print(f"\n{'='*80}")
        print(f"🔬 매장 {store_id} 영양 분석 시작")
        print(f"{'='*80}\n")
        
        # 1. DB에서 메뉴 전체 로드
        session = get_session()
        try:
            store = session.query(Store).filter_by(id=store_id).first()
            if not store:
                raise Exception(f"매장 {store_id}를 찾을 수 없습니다.")
            
            # 매장의 모든 메뉴 아이템 가져오기
            menu_items = []
            for menu in store.menus:
                items = session.query(MenuItem).filter_by(menu_id=menu.id).all()
                menu_items.extend(items)
            
            print(f"📊 총 {len(menu_items)}개 메뉴 발견")
            
            # 2. 배치 단위로 분석
            total_batches = (len(menu_items) + self.batch_size - 1) // self.batch_size
            
            for i in range(0, len(menu_items), self.batch_size):
                batch = menu_items[i:i + self.batch_size]
                batch_num = i // self.batch_size + 1
                
                print(f"\n[배치 {batch_num}/{total_batches}] {len(batch)}개 메뉴 분석 중...")
                
                # Step 1: 재료 유추
                self._analyze_ingredients(session, batch)
                
                # Step 2: 영양소 유추
                self._analyze_nutrition(session, batch)
            
            print(f"\n{'='*80}")
            print(f"✅ 매장 {store_id} 분석 완료!")
            print(f"{'='*80}\n")
        
        finally:
            session.close()
    
    def _analyze_ingredients(self, session, menu_items: List[MenuItem]):
        """
        Step 1: 메뉴명/설명 → 재료 유추
        
        Args:
            session: DB 세션
            menu_items: 메뉴 아이템 리스트
        """
        print("  📝 Step 1: 재료 분석 중...")
        
        # 메뉴 정보 준비
        menus_data = []
        for item in menu_items:
            menus_data.append({
                "id": item.id,
                "name": item.name,
                "description": item.description or "",
                "category": item.menu.name if item.menu else "기타"
            })
        
        # 프롬프트 작성
        prompt = f"""당신은 음식 재료 분석 전문가입니다.

다음은 매장의 메뉴 리스트입니다.
각 메뉴의 이름, 설명, 카테고리를 참고하여 주요 재료를 유추하세요.

메뉴 리스트:
{json.dumps(menus_data, ensure_ascii=False, indent=2)}

다음 JSON 배열 형식으로 반환하세요:
[
  {{
    "item_id": 메뉴 ID,
    "ingredients": [
      {{
        "ingredient_name": "재료명",
        "quantity_value": 예상 수량 (숫자),
        "quantity_unit": "단위 (g/ml/개/EA 등)",
        "notes": "참고사항 (선택)"
      }}
    ]
  }}
]

규칙:
- 주요 재료 3-7개 정도만 포함
- 수량은 1인분 기준 예상값
- 카페음료는 에스프레소샷, 우유, 시럽 등 포함
- 음식은 주재료, 부재료, 양념 등 포함
- confidence 필드는 제외 (재료 분석이므로)

순수 JSON만 반환하세요.
"""
        
        try:
            # LLM 호출
            result = self.llm_router.create_response(
                prompt,
                reasoning={"effort": "medium"},
                text={"verbosity": "low"}
            )
            
            # JSON 파싱
            parsed = self.llm_router.parse_json_response(result)
            ingredients_data = parsed['data']
            
            # DB 저장
            saved_count = 0
            for item_data in ingredients_data:
                item_id = item_data['item_id']
                
                # 기존 재료 삭제 (갱신)
                session.query(ItemIngredient).filter_by(item_id=item_id).delete()
                
                # 새 재료 저장
                for ing in item_data.get('ingredients', []):
                    ingredient = ItemIngredient(
                        item_id=item_id,
                        ingredient_name=ing['ingredient_name'],
                        quantity_value=float(ing.get('quantity_value', 0)),
                        quantity_unit=ing.get('quantity_unit', 'g'),
                        notes=ing.get('notes', '')
                    )
                    session.add(ingredient)
                    saved_count += 1
            
            session.commit()
            print(f"  ✅ 재료 {saved_count}개 저장 완료")
            
        except Exception as e:
            session.rollback()
            print(f"  ❌ 재료 분석 실패: {e}")
            import traceback
            traceback.print_exc()
    
    def _analyze_nutrition(self, session, menu_items: List[MenuItem]):
        """
        Step 2: 재료 → 영양소 유추
        
        Args:
            session: DB 세션
            menu_items: 메뉴 아이템 리스트
        """
        print("  🔬 Step 2: 영양소 분석 중...")
        
        # 메뉴+재료 정보 준비
        menus_with_ingredients = []
        for item in menu_items:
            # 재료 정보 가져오기 (방금 저장한 것)
            ingredients = session.query(ItemIngredient).filter_by(item_id=item.id).all()
            
            ingredients_list = [
                f"{ing.ingredient_name} {ing.quantity_value}{ing.quantity_unit}"
                for ing in ingredients
            ]
            
            menus_with_ingredients.append({
                "id": item.id,
                "name": item.name,
                "description": item.description or "",
                "category": item.menu.name if item.menu else "기타",
                "ingredients": ingredients_list
            })
        
        # 프롬프트 작성
        prompt = f"""당신은 영양학 전문가입니다.

다음은 메뉴와 재료 정보입니다.
각 메뉴의 영양소를 유추하여 계산하세요.

메뉴 + 재료 리스트:
{json.dumps(menus_with_ingredients, ensure_ascii=False, indent=2)}

다음 JSON 배열 형식으로 반환하세요:
[
  {{
    "item_id": 메뉴 ID,
    "calories": 예상 칼로리 (kcal),
    "protein_g": 단백질 (g),
    "fat_g": 지방 (g),
    "carbs_g": 탄수화물 (g),
    "sugar_g": 당류 (g),
    "caffeine_mg": 카페인 (mg, 커피/차/초콜릿만),
    "confidence": 신뢰도 (0.0-1.0)
  }}
]

규칙:
- 1인분 기준
- 재료와 수량을 참고하여 정확히 계산
- 카페인 없으면 0
- confidence는 계산 확실도 (재료가 명확하면 0.8-0.9, 애매하면 0.5-0.7)

순수 JSON만 반환하세요.
"""
        
        try:
            # LLM 호출
            result = self.llm_router.create_response(
                prompt,
                reasoning={"effort": "medium"},
                text={"verbosity": "low"}
            )
            
            # JSON 파싱
            parsed = self.llm_router.parse_json_response(result)
            nutrition_data = parsed['data']
            
            # DB 저장
            saved_count = 0
            for item_data in nutrition_data:
                existing = session.query(NutritionEstimate).filter_by(
                    item_id=item_data['item_id']
                ).first()

                if existing:
                    # 업데이트
                    existing.calories = float(item_data.get('calories', 0))
                    existing.protein_g = float(item_data.get('protein_g', 0))
                    existing.fat_g = float(item_data.get('fat_g', 0))
                    existing.carbs_g = float(item_data.get('carbs_g', 0))
                    existing.sugar_g = float(item_data.get('sugar_g', 0))
                    existing.caffeine_mg = float(item_data.get('caffeine_mg', 0))
                    existing.confidence = float(item_data.get('confidence', 0))
                    existing.last_computed_at = datetime.now()
                else:
                    # 새로 생성
                    estimate = NutritionEstimate(
                        item_id=item_data['item_id'],
                        calories=float(item_data.get('calories', 0)),
                        protein_g=float(item_data.get('protein_g', 0)),
                        fat_g=float(item_data.get('fat_g', 0)),
                        carbs_g=float(item_data.get('carbs_g', 0)),
                        sugar_g=float(item_data.get('sugar_g', 0)),
                        caffeine_mg=float(item_data.get('caffeine_mg', 0)),
                        confidence=float(item_data.get('confidence', 0)),
                        last_computed_at=datetime.now()
                    )
                    session.add(estimate)
                    
            saved_count += 1
            
            session.commit()
            print(f"  ✅ 영양소 {saved_count}개 저장 완료")
            
        except Exception as e:
            session.rollback()
            print(f"  ❌ 영양소 분석 실패: {e}")
            import traceback
            traceback.print_exc()


# 사용 예시
if __name__ == "__main__":
    analyzer = NutritionAnalyzer(batch_size=10)  # 10개씩 처리
    
    # 매장 1번 분석
    analyzer.analyze_store(store_id=2)