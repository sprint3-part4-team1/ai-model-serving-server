"""
데이터 로더 모듈 (SQLAlchemy ORM 버전)
models.py 기반
"""

import json
import os
from sqlalchemy.orm import joinedload
from database import get_session
from models import Store, Menu, MenuItem, ItemIngredient, NutritionEstimate
from pathlib import Path


class DataLoader:
    """데이터 로드 (ORM 버전)"""

    def __init__(self, source='json', json_path=None):
        """
        데이터 로더 초기화

        Args:
            source (str): 데이터 소스 ('json' 또는 'mysql')
            json_path (str): JSON 파일 경로 (source='json'일 때)
        """
        self.source = source
        self.session = None
        base_dir = Path(__file__).resolve().parent  # 임시로 json에서 테스트
        self.json_path = base_dir.parent.parent / 'samples' / 'menu_sample_data_v2.json'


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
            return data
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON 파일을 찾을 수 없습니다: {self.json_path}")

    def load_from_mysql(self, store_id=1):
        """
        MySQL에서 ORM으로 로드

        Args:
            store_id (int): 매장 ID

        Returns:
            dict: 전체 데이터
        """
        if not self.session:
            raise Exception("MySQL 세션 없음")

        try:
            # 가게 조회
            store = self.session.query(Store).filter(Store.id == store_id).first()

            if not store:
                raise Exception(f"Store {store_id} 없음")
            
            # 메뉴 조회
            menus = store.menus

            # 메뉴 아이템 조회 (nutrition까지 eager loading)
            menu_items = []
            for menu in menus:
                items = (
                    self.session.query(MenuItem)
                    .filter(MenuItem.menu_id == menu.id)
                    .options(
                        joinedload(MenuItem.nutrition),
                        joinedload(MenuItem.ingredients)
                    )
                    .all()
                )
                menu_items.extend(items)

            # dict로 변환
            return {
                "stores": [self._to_dict(store)],
                "menus": [self._to_dict(m) for m in menus],
                "menu_items": [self._to_dict(item) for item in menu_items],
                "item_ingredients": [
                    self._to_dict(ing) 
                    for item in menu_items 
                    for ing in item.ingredients
                ],
                "nutrition_estimates": [
                    self._to_dict(item.nutrition)
                    for item in menu_items
                    if item.nutrition
                ]
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
                result[column.name] = float(value) if isinstance(value, type(value)) and hasattr(value, '__float__') else value
            else:
                result[column.name] = value
        return result
    
    def load(self, store_id=1):
        """데이터 로드"""
        if self.source == 'json':
            return self.load_from_json()
        elif self.source == 'mysql':
            return self.load_from_mysql(store_id)
        else:
            raise ValueError(f"지원하지 않는 소스: {self.source}")
        
    def close(self):
        """세션 종료"""
        if self.session:
            self.session.close()