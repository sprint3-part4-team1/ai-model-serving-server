"""
샘플 데이터 DB 삽입 스크립트
samples/menu_sample_data_v3.json → MySQL DB
"""

import json
import pymysql
from datetime import datetime
from dotenv import load_dotenv
import os

# 환경변수 로드
load_dotenv()

# DB 연결 정보
DB_CONFIG = {
    'host': os.getenv("DB_HOST"),
    'port': int(os.getenv("DB_PORT", "8004")),
    'user': os.getenv("DB_USER"),
    'password': os.getenv('DB_PASSWORD'), 
    'database': os.getenv('DB_NAME'),
    'charset': 'utf8mb4'
}

def load_sample_data():
    """JSON 샘플 데이터 로드"""
    with open('samples/menu_sample_data_v3.json', 'r', encoding='utf-8') as f:
        return json.load(f)
    
def insert_stores(cursor, stores):
    """Stores 테이블 삽입"""
    print("📍 Stores 데이터 삽입 중...")
    
    for store in stores:
        sql = """
        INSERT INTO stores (name, address, phone, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            address = VALUES(address),
            phone = VALUES(phone),
            updated_at = VALUES(updated_at)
        """
        cursor.execute(sql, (
            store['name'],
            store['address'],
            store['phone'],
            store['created_at'],
            store['updated_at']
        ))
    
    print(f"✅ Stores {len(stores)}개 삽입 완료")


def insert_menus(cursor, menus):
    """Menus 테이블 삽입"""
    print("📋 Menus 데이터 삽입 중...")
    
    for menu in menus:
        sql = """
        INSERT INTO menus (store_id, name, description, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            store_id = VALUES(store_id),
            name = VALUES(name),
            description = VALUES(description),
            updated_at = VALUES(updated_at)
        """
        cursor.execute(sql, (
            menu['store_id'],
            menu['name'],
            menu['description'],
            menu['created_at'],
            menu.get('updated_at', menu['created_at'])
        ))
    
    print(f"✅ Menus {len(menus)}개 삽입 완료")


def insert_menu_items(cursor, menu_items):
    """Menu Items 테이블 삽입"""
    print("🍽️  Menu Items 데이터 삽입 중...")
    
    for item in menu_items:
        sql = """
        INSERT INTO menu_items 
        (menu_id, name, description, price, is_available, image_url, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            menu_id = VALUES(menu_id),
            name = VALUES(name),
            description = VALUES(description),
            price = VALUES(price),
            is_available = VALUES(is_available),
            image_url = VALUES(image_url),
            updated_at = VALUES(updated_at)
        """
        cursor.execute(sql, (
            item['menu_id'],
            item['name'],
            item['description'],
            item['price'],
            item['is_available'],
            item['image_url'],
            item['created_at'],
            item['updated_at']
        ))
    
    print(f"✅ Menu Items {len(menu_items)}개 삽입 완료")


def insert_item_ingredients(cursor, ingredients):
    """Item Ingredients 테이블 삽입"""
    print("🥬 Item Ingredients 데이터 삽입 중...")
    
    for ing in ingredients:
        sql = """
        INSERT INTO item_ingredients 
        (item_id, ingredient_name, quantity_unit, quantity_value, notes)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            item_id = VALUES(item_id),
            ingredient_name = VALUES(ingredient_name),
            quantity_unit = VALUES(quantity_unit),
            quantity_value = VALUES(quantity_value),
            notes = VALUES(notes)
        """
        cursor.execute(sql, (
            ing['item_id'],
            ing['ingredient_name'],
            ing['quantity_unit'],
            ing['quantity_value'],
            ing['notes']
        ))
    
    print(f"✅ Item Ingredients {len(ingredients)}개 삽입 완료")

# 검증용으로 일단
def insert_nutrition_estimates(cursor, estimates):
    """Nutrition Estimates 테이블 삽입"""
    print("🍎 Nutrition Estimates 데이터 삽입 중...")

    sql = """
    INSERT INTO nutrition_estimates 
    (item_id, calories, sugar_g, caffeine_mg, protein_g, fat_g, carbs_g, confidence, last_computed_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        item_id = VALUES(item_id),
        calories = VALUES(calories),
        sugar_g = VALUES(sugar_g),
        caffeine_mg = VALUES(caffeine_mg),
        protein_g = VALUES(protein_g),
        fat_g = VALUES(fat_g),
        carbs_g = VALUES(carbs_g),
        confidence = VALUES(confidence),
        last_computed_at = VALUES(last_computed_at)
    """

    for est in estimates:
        cursor.execute(sql, (
            est['item_id'],
            est.get('calories'),
            est.get('sugar_g'),
            est.get('caffeine_mg'),
            est.get('protein_g'),
            est.get('fat_g'),
            est.get('carbs_g'),
            est.get('confidence'),
            est.get('last_computed_at')
        ))

    print(f"✅ Nutrition Estimates {len(estimates)}개 삽입 완료")

def main():
    """메인 실행"""
    print("=" * 60)
    print("🚀 샘플 데이터 DB 삽입 시작")
    print("=" * 60)
    
    # 1. JSON 데이터 로드
    print("\n📂 샘플 데이터 로드 중...")
    data = load_sample_data()
    print(f"✅ 데이터 로드 완료")
    print(f"   - Stores: {len(data['stores'])}개")
    print(f"   - Menus: {len(data['menus'])}개")
    print(f"   - Menu Items: {len(data['menu_items'])}개")
    print(f"   - Item Ingredients: {len(data['item_ingredients'])}개")
    #print(f"   - Nutrition Estimates: {len(data['nutrition_estimates'])}개")
    
    # 2. DB 연결
    print(f"\n🔌 DB 연결 중... ({DB_CONFIG['host']}:{DB_CONFIG['port']})")
    
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        print("✅ DB 연결 성공")
        
        # 3. 데이터 삽입 (순서 중요! FK 제약 때문에)
        print("\n" + "=" * 60)
        print("📥 데이터 삽입 시작")
        print("=" * 60)
        
        insert_stores(cursor, data['stores'])
        insert_menus(cursor, data['menus'])
        insert_menu_items(cursor, data['menu_items'])
        insert_item_ingredients(cursor, data['item_ingredients'])
        #insert_nutrition_estimates(cursor, data['nutrition_estimates'])
        
        # 4. 커밋
        connection.commit()
        print("\n" + "=" * 60)
        print("✅ 모든 데이터 삽입 완료 및 커밋 성공!")
        print("=" * 60)
        
        # 5. 검증 쿼리
        print("\n🔍 삽입 결과 확인:")
        cursor.execute("SELECT COUNT(*) FROM stores")
        print(f"   - Stores: {cursor.fetchone()[0]}개")
        
        cursor.execute("SELECT COUNT(*) FROM menus")
        print(f"   - Menus: {cursor.fetchone()[0]}개")
        
        cursor.execute("SELECT COUNT(*) FROM menu_items")
        print(f"   - Menu Items: {cursor.fetchone()[0]}개")
        
        cursor.execute("SELECT COUNT(*) FROM item_ingredients")
        print(f"   - Item Ingredients: {cursor.fetchone()[0]}개")

        #cursor.execute("SELECT COUNT(*) FROM nutrition_estimates")
        #print(f"   - Nutrition Estimates: {cursor.fetchone()[0]}개")
        
        
    except pymysql.Error as e:
        print(f"\n❌ DB 오류 발생: {e}")
        connection.rollback()
        
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        connection.rollback()
        
    finally:
        cursor.close()
        connection.close()
        print("\n🔌 DB 연결 종료")


if __name__ == "__main__":
    main()