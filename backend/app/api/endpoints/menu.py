"""
Menu API Endpoints
메뉴 필터링 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas.menu import MenuFilterRequest, MenuFilterResponse
from app.services.menu_filter_service import menu_filter_service
from app.core.logging import app_logger as logger


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
