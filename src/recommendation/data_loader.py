"""
데이터 로더 모듈
MySQL DB(SQLAlchemy) 또는 JSON 파일에서 메뉴 데이터 로드
"""

import json
import os
from sqlalchemy import text
from src.database import get_session


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
            stores_query = text("SELECT * FROM stores WHERE id = :store_id")
            stores_result = self.session.execute(stores_query, {"store_id": store_id})
            stores = [dict(row._mapping) for row in stores_result]

            # Menus
            menus_query = text("SELECT * FROM menus WHERE store_id = :store_id")
            menus_result = self.session.execute(menus_query, {"store_id": store_id})
            menus = [dict(row._mapping) for row in menus_result]

            # Menu Items
            if menus:
                menu_ids = [m['id'] for m in menus]
                placeholders = ','.join([':menu_id_' + str(i) for i in range(len(menu_ids))])
                params = {f'menu_id_{i}': mid for i, mid in enumerate(menu_ids)}

                items_query = text(f"SELECT * FROM menu_items WHERE menu_id IN ({placeholders})")
                items_result = self.session.execute(items_query, params)
                menu_items = [dict(row._mapping) for row in items_result]

                # Item Ingredients
                if menu_items:
                    item_ids = [item['id'] for item in menu_items]
                    placeholders = ','.join([':item_id_' + str(i) for i in range(len(item_ids))])
                    params = {f'item_id_{i}': iid for i, iid in enumerate(item_ids)}

                    ingredients_query = text(f"SELECT * FROM item_ingredients WHERE item_id IN ({placeholders})")
                    ingredients_result = self.session.execute(ingredients_query, params)
                    item_ingredients = [dict(row._mapping) for row in ingredients_result]

                    # Nutrition Estimates
                    nutrition_query = text(f"SELECT * FROM nutrition_estimates WHERE item_id IN ({placeholders})")
                    nutrition_result = self.session.execute(nutrition_query, params)
                    nutrition_estimates = [dict(row._mapping) for row in nutrition_result]
                else:
                    item_ingredients = []
                    nutrition_estimates = []
            else:
                menu_items = []
                item_ingredients = []
                nutrition_estimates = []

            return {
                "stores": stores,
                "menus": menus,
                "menu_items": menu_items,
                "item_ingredients": item_ingredients,
                "nutrition_estimates": nutrition_estimates
            }

        except Exception as e:
            raise Exception(f"MySQL 데이터 로드 실패: {str(e)}")

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


# 간단한 테스트
if __name__ == "__main__":
    print("=== JSON 테스트 ===")
    loader_json = DataLoader(source='json')
    data = loader_json.load()
    print(f"메뉴 아이템 수: {len(data['menu_items'])}개")
    print(f"영양소 정보 수: {len(data['nutrition_estimates'])}개")

    print("\n=== MySQL 테스트 ===")
    try:
        loader_mysql = DataLoader(source='mysql')
        data_mysql = loader_mysql.load(store_id=1)
        print(f"메뉴 아이템 수: {len(data_mysql['menu_items'])}개")
        print(f"영양소 정보 수: {len(data_mysql['nutrition_estimates'])}개")
        loader_mysql.close()
    except Exception as e:
        print(f"MySQL 테스트 실패: {e}")
