"""
Menu API Endpoints
메뉴 필터링 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.schemas.menu import MenuFilterRequest, MenuFilterResponse
from app.services.menu_filter_service import menu_filter_service
from app.core.logging import app_logger as logger
from app.core.database import get_db
from app.models.menu import Menu, MenuItem


router = APIRouter()


@router.post(
    "/filter",
    response_model=MenuFilterResponse,
    summary="AI 기반 메뉴 필터링",
    description="자연어 쿼리를 기반으로 메뉴를 필터링하고 추천합니다.",
    responses={
        200: {"description": "성공", "model": MenuFilterResponse},
        500: {"description": "서버 오류"}
    }
)
async def filter_menus(request: MenuFilterRequest):
    """
    AI 기반 메뉴 필터링

    고객의 자연어 요청을 이해하고, 적합한 메뉴를 필터링하여 반환합니다.

    예시 쿼리:
    - "칼로리 낮은 음료 추천"
    - "달콤한 디저트 찾기"
    - "저렴한 커피 추천"
    - "건강한 브런치 메뉴"
    """
    try:
        logger.info(f"Menu filter requested: query='{request.query}'")

        # 메뉴 리스트를 딕셔너리로 변환
        menus_dict = [menu.model_dump() for menu in request.menus]

        # 필터링 수행
        result = menu_filter_service.filter_menus(
            query=request.query,
            menus=menus_dict
        )

        logger.info("Menu filter completed successfully")

        return MenuFilterResponse(
            success=True,
            data=result
        )

    except Exception as e:
        logger.error(f"Failed to filter menus: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": 500,
                    "message": "메뉴 필터링 중 오류가 발생했습니다.",
                    "details": str(e)
                }
            }
        )


@router.get(
    "/store/{store_id}",
    summary="매장별 메뉴 조회",
    description="특정 매장의 전체 메뉴를 카테고리별로 조회합니다."
)
async def get_store_menus(store_id: int, db: Session = Depends(get_db)):
    """
    매장별 메뉴 조회

    매장 ID를 기반으로 해당 매장의 모든 메뉴를 카테고리별로 반환합니다.
    """
    try:
        logger.info(f"Fetching menus for store_id: {store_id}")

        # 매장의 모든 카테고리(메뉴) 조회
        menus = db.query(Menu).filter(Menu.store_id == store_id).all()

        if not menus:
            return {
                "success": True,
                "data": {
                    "store_id": store_id,
                    "categories": []
                }
            }

        # 카테고리별로 메뉴 아이템 구성
        categories = []
        for menu in menus:
            # 해당 카테고리의 메뉴 아이템들 조회
            items = db.query(MenuItem).filter(MenuItem.menu_id == menu.id).all()

            category_data = {
                "id": menu.id,
                "name": menu.name,
                "description": menu.description,
                "items": [
                    {
                        "id": item.id,
                        "name": item.name,
                        "description": item.description,
                        "price": float(item.price) if item.price else None,
                        "image_url": item.image_url,
                        "is_available": item.is_available
                    }
                    for item in items
                ]
            }
            categories.append(category_data)

        logger.info(f"Found {len(categories)} categories for store_id: {store_id}")

        return {
            "success": True,
            "data": {
                "store_id": store_id,
                "categories": categories
            }
        }

    except Exception as e:
        logger.error(f"Failed to fetch menus for store {store_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": 500,
                    "message": "메뉴 조회 중 오류가 발생했습니다.",
                    "details": str(e)
                }
            }
        )


@router.get(
    "/health",
    summary="헬스 체크",
    description="메뉴 API 서비스 상태를 확인합니다."
)
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "service": "Menu Filter API",
            "version": "1.0.0"
        }
    }
