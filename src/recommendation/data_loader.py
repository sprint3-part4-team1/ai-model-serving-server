"""
데이터 로더 모듈
MySQL DB(SQLAlchemy) 또는 JSON 파일에서 메뉴 데이터 로드
"""
import json
import os
from sqlalchemy.orm import joinedload
from database import get_session
from models import Store, Menu, MenuItem, ItemIngredient, NutritionEstimate


class DataLoader:
    """데이터 로드 담당 클래스 (SQLAlchemy 버전)"""
    
    def __init__(self, source='json', json_path='samples/menu_sample_data_v2.json'):
        """
        데이터 로더 초기화
        
        Args:
            source (str): 데이터 소스 ('json' 또는 'mysql')
            json_path (str): JSON 파일 경로 (source='json'일 때)
        """
        self.source = source
        self.json_path = json_path
        self.session = None
        
        if source == 'mysql':
            self.session = get_session()
    
    def load_from_json(self):
        """
        JSON 파일에서 데이터 로드
        
        Returns:
            dict: 전체 데이터
        """
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # ✅ JSON에도 menu_name 추가
            menus_map = {m['id']: m['name'] for m in data.get('menus', [])}
            for item in data.get('menu_items', []):
                item['menu_name'] = menus_map.get(item['menu_id'], '')
            
            return data
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON 파일을 찾을 수 없습니다: {self.json_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 파싱 오류: {str(e)}")
    
    def load_from_mysql(self, store_id=1):
        """
        MySQL에서 데이터 로드 (SQLAlchemy 사용)
        
        Args:
            store_id (int): 매장 ID
        
        Returns:
            dict: 전체 데이터
        """
        if not self.session:
            raise Exception("MySQL 세션이 설정되지 않았습니다.")
        
        try:
            # Stores
            store = self.session.query(Store).filter(Store.id == store_id).first()
            
            if not store:
                raise Exception(f"Store {store_id}를 찾을 수 없습니다.")
            
            stores = [store]
            
            # Menus
            menus = store.menus
            
            # ✅ Menu 이름 매핑 테이블 생성
            menu_name_map = {menu.id: menu.name for menu in menus}
            
            # Menu Items (menu 정보까지 eager loading)
            menu_items = []
            for menu in menus:
                items = (
                    self.session.query(MenuItem)
                    .filter(MenuItem.menu_id == menu.id)
                    .options(
                        joinedload(MenuItem.nutrition),
                        joinedload(MenuItem.ingredients),
                        joinedload(MenuItem.menu)  # ✅ menu 관계 추가
                    )
                    .all()
                )
                menu_items.extend(items)
            
            # Item Ingredients
            item_ingredients = []
            for item in menu_items:
                item_ingredients.extend(item.ingredients)
            
            # Nutrition Estimates
            nutrition_estimates = [item.nutrition for item in menu_items if item.nutrition]
            
            # ✅ dict 변환 시 menu_name 추가
            menu_items_dict = []
            for item in menu_items:
                item_dict = self._to_dict(item)
                item_dict['menu_name'] = menu_name_map.get(item.menu_id, '')  # ✅ 메뉴 이름 추가
                menu_items_dict.append(item_dict)
            
            return {
                "stores": [self._to_dict(s) for s in stores],
                "menus": [self._to_dict(m) for m in menus],
                "menu_items": menu_items_dict,  # ✅ menu_name 포함
                "item_ingredients": [self._to_dict(ing) for ing in item_ingredients],
                "nutrition_estimates": [self._to_dict(n) for n in nutrition_estimates]
            }
        
        except Exception as e:
            raise Exception(f"MySQL 데이터 로드 실패: {str(e)}")
    
    def _to_dict(self, obj):
        """ORM 객체 → dict 변환"""
        if obj is None:
            return None
        
        result = {}
        for column in obj.__table__.columns:
            value = getattr(obj, column.name)
            # Decimal/datetime 등 JSON 호환 변환
            if hasattr(value, 'isoformat'):
                result[column.name] = value.isoformat()
            elif value is not None:
                # Decimal을 float로 변환
                try:
                    result[column.name] = float(value)
                except (TypeError, ValueError):
                    result[column.name] = value
            else:
                result[column.name] = value
        return result
    
    def load(self, store_id=1):
        """
        설정된 소스에서 데이터 로드
        
        Args:
            store_id (int): 매장 ID (MySQL 사용 시)
        
        Returns:
            dict: 전체 데이터
        """
        if self.source == 'json':
            return self.load_from_json()
        elif self.source == 'mysql':
            return self.load_from_mysql(store_id)
        else:
            raise ValueError(f"지원하지 않는 데이터 소스: {self.source}")
    
    def close(self):
        """데이터베이스 세션 종료"""
        if self.session:
            self.session.close()
            print("✅ MySQL 세션 종료")