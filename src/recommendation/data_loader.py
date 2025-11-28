"""
데이터 로더 모듈
MySQL DB(SQLAlchemy) 또는 JSON 파일에서 메뉴 데이터 로드
"""
import json
import os
import time
from typing import Dict, Any, List

from database import get_session
from sqlalchemy.orm import joinedload
from models import Store, Menu, MenuItem, ItemIngredient, NutritionEstimate
from constants import BASE_DIR

class DataLoader:
    """데이터 로드 담당 클래스 (SQLAlchemy 버전)"""
    
    def __init__(self, source='json'):
        """
        데이터 로더 초기화
        
        Args:
            source (str): 데이터 소스 ('json' 또는 'mysql')
            json_path (str): JSON 파일 경로 (source='json'일 때)
        """
        self.source = source
        self.session = None

        # ✅ 캐싱 레이어
        self._cache = {}
        self._cache_timestamp = {}
        self._cache_ttl = 300  # 5분
        
    def load(self, store_id=1) -> Dict[str, Any]:
        """
        데이터 로드 (캐싱 지원)
        
        Args:
            store_id (int): 매장 ID
        
        Returns:
            dict: {
                'menu_items': [...],
                'nutrition_estimates': [...],
                'menus': [...]
            }
        """
        cache_key = f"{self.source}_{store_id}"
        
        # ✅ 캐시 확인
        if cache_key in self._cache:
            # TTL 체크
            if time.time() - self._cache_timestamp[cache_key] < self._cache_ttl:
                print(f"✅ 캐시에서 로드: {cache_key}")
                return self._cache[cache_key]
        
        # 캐시 없음 → DB 조회
        print(f"🔄 DB에서 로드: {cache_key}")
        
        if self.source == 'mysql':
            data = self.load_from_mysql(store_id)
        else:
            data = self.load_from_json()
        
        # ✅ 캐시 저장
        self._cache[cache_key] = data
        self._cache_timestamp[cache_key] = time.time()
        
        return data

    def load_from_mysql(self, store_id=1):
        """
        MySQL에서 데이터 로드 (최적화된 버전)
        JOIN을 사용하여 한 번에 모든 데이터 로드
        
        Args:
            store_id (int): 매장 ID
        
        Returns:
            dict: 전체 데이터
        """
        session = get_session()

        try:
            # ✅ JOIN으로 한 번에 가져오기!
            query = (
                session.query(
                    MenuItem,
                    Menu.name.label('menu_name'),
                    Menu.id.label('menu_id'),
                    NutritionEstimate
                )
                .join(Menu, MenuItem.menu_id == Menu.id)
                .outerjoin(NutritionEstimate, MenuItem.id == NutritionEstimate.item_id)
                .filter(Menu.store_id == store_id)
                .filter(MenuItem.is_available == True)
            )

            results = query.all()

            # 데이터 변환
            menu_items = []
            nutrition_estimates = []
            menus_dict = {}

            for item, menu_name, menu_id, nutrition in results:
                # MenuItem 데이터
                menu_items.append({
                    'id': item.id,
                    'menu_id': item.menu_id,
                    'name': item.name,
                    'description': item.description,
                    'price': float(item.price),
                    'is_available': item.is_available,
                    'image_url': item.image_url,
                    'created_at': item.created_at.isoformat() if item.created_at else None,
                    'updated_at': item.updated_at.isoformat() if item.updated_at else None,
                    'menu_name': menu_name  # ✅ JOIN으로 가져온 데이터!
                })

                # Nutrition 데이터
                if nutrition:
                    nutrition_estimates.append({
                        'id': nutrition.id,
                        'item_id': nutrition.item_id,
                        'calories': nutrition.calories,
                        'sugar_g': nutrition.sugar_g,
                        'caffeine_mg': nutrition.caffeine_mg,
                        'protein_g': nutrition.protein_g,
                        'fat_g': nutrition.fat_g,
                        'carbs_g': nutrition.carbs_g,
                        'confidence': nutrition.confidence,
                        'last_computed_at': nutrition.last_computed_at.isoformat() if nutrition.last_computed_at else None
                    })

                # Menu 데이터 (중복 제거)
                if menu_id not in menus_dict:
                    menus_dict[menu_id] = {
                        'id': menu_id,
                        'name': menu_name
                    }

            return {
                'menu_items': menu_items,
                'nutrition_estimates': nutrition_estimates,
                'menus': list(menus_dict.values())
            }
        
        finally:
            session.close()
    
    def load_from_json(self) -> Dict[str, Any]:
        """
        JSON 파일에서 데이터 로드
        
        Returns:
            dict: 메뉴 데이터
        """

        json_path = os.path.join(BASE_DIR, 'samples', 'menu_sample_data_v2')

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)   
            return data
        
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON 파일을 찾을 수 없습니다: {self.json_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 파싱 오류: {str(e)}")
    
    def clear_cache(self, store_id: int = None):
        """
        캐시 삭제

        Args:
            store_id(int): 특정 매장 캐시만 삭제 (None이면 전체 삭제)
        """
        if store_id is None:
            self._cache.clear()
            self._cache_timestamp.clear()
            print("✅ 전체 캐시 삭제")
        else:
            cache_key = f"{self.source}_{store_id}"
            if cache_key in self._cache:
                del self._cache[cache_key]
                del self._cache_timestamp[cache_key]
                print(f"✅ 캐시 삭제: {cache_key}")

    def get_cache_info(self) -> Dict[str, Any]:
        """
        캐시 정보 반환

        Returns:
            dict: 캐시 통계
        """
        cache_info = {}
        current_time = time.time()

        for key, timestamp in self._cache_timestamp.items():
            age = current_time - timestamp
            remaining_ttl = max(0, self._cache_ttl - age)

            cache_info[key] = {
                'age': f"{age:.1f}s",
                'remaining_ttl': f"{remaining_ttl:.1f}s",
                'expired': remaining_ttl == 0
            }
        
        return cache_info
    
    def close(self):
        """리소스 정리"""
        if self.session:
            self.session.close()
            self.session = None
            print("✅ MySQL 세션 종료")
