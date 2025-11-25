"""
Menu Service
매장 메뉴 정보를 조회하는 서비스
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Optional
from app.core.logging import app_logger as logger


class MenuService:
    """메뉴 조회 서비스"""

    def get_store_menus(
        self,
        db: Session,
        store_id: int,
        limit: int = 10
    ) -> List[Dict]:
        """
        매장의 메뉴 목록 조회

        Args:
            db: 데이터베이스 세션
            store_id: 매장 ID
            limit: 가져올 메뉴 개수 (기본 10개)

        Returns:
            메뉴 리스트 [{"id": 1, "name": "아메리카노", "price": 3500, ...}, ...]
        """
        try:
            # 매장의 메뉴 아이템 조회 (가격 정보 포함)
            query = text("""
                SELECT
                    mi.id,
                    mi.name,
                    mi.description,
                    mi.price,
                    mi.is_available
                FROM menu_items mi
                JOIN menus m ON mi.menu_id = m.id
                WHERE m.store_id = :store_id
                    AND mi.is_available = 1
                ORDER BY mi.id
                LIMIT :limit
            """)

            result = db.execute(
                query,
                {"store_id": store_id, "limit": limit}
            )

            menus = []
            for row in result:
                menus.append({
                    "id": row[0],
                    "name": row[1],
                    "description": row[2] or "",
                    "price": float(row[3]) if row[3] else None,
                    "is_available": bool(row[4])
                })

            logger.info(f"Found {len(menus)} menus for store {store_id}")
            return menus

        except Exception as e:
            logger.error(f"Failed to get store menus: {e}")
            return []

    def get_popular_menus(
        self,
        db: Session,
        store_id: int,
        limit: int = 3
    ) -> List[Dict]:
        """
        인기 메뉴 조회 (현재는 상위 메뉴 반환, 추후 주문량 기반으로 개선 가능)

        Args:
            db: 데이터베이스 세션
            store_id: 매장 ID
            limit: 가져올 메뉴 개수 (기본 3개)

        Returns:
            인기 메뉴 리스트
        """
        # 현재는 단순히 상위 메뉴를 반환
        # 추후 주문량, 평점 등을 고려하여 개선 가능
        return self.get_store_menus(db, store_id, limit)

    def format_menus_for_story(self, menus: List[Dict]) -> str:
        """
        스토리 생성용 메뉴 텍스트 포맷팅

        Args:
            menus: 메뉴 리스트

        Returns:
            "아메리카노(3,500원), 카페라떼(4,000원)" 형식의 문자열
        """
        if not menus:
            return ""

        formatted = []
        for menu in menus:
            name = menu["name"]
            price = menu.get("price")

            if price:
                formatted.append(f"{name}({price:,.0f}원)")
            else:
                formatted.append(name)

        return ", ".join(formatted)


# 싱글톤 인스턴스
menu_service = MenuService()
