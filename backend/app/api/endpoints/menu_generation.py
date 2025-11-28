"""
Menu Generation API Endpoints
메뉴판 생성 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.schemas.menu_generation import (
    MenuGenerationRequest,
    MenuGenerationResponse
)
from app.services.menu_generation_service import menu_generation_service
from app.core.database import get_db
from app.core.logging import app_logger as logger


router = APIRouter()


@router.post(
    "/generate",
    response_model=MenuGenerationResponse,
    summary="AI 기반 메뉴판 생성",
    description="""
    메뉴 카테고리와 아이템을 AI로 자동 생성합니다.

    기능:
    - 메뉴 카테고리 생성 (예: 파스타, 스테이크, 디저트)
    - 메뉴 아이템 생성 (이름, 설명, 가격, 이미지)
    - AI 자동 생성:
      - 메뉴 이름만 입력 → 이미지 + 설명 자동 생성
      - 메뉴 이름 + 이미지 → 설명만 자동 생성
      - 메뉴 이름 + 설명 → 이미지만 자동 생성
    """,
    responses={
        200: {"description": "성공", "model": MenuGenerationResponse},
        400: {"description": "잘못된 요청"},
        500: {"description": "서버 오류"}
    }
)
async def generate_menu(
    request: MenuGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    AI 기반 메뉴판 생성

    메뉴 카테고리와 아이템을 생성하며, 이미지와 설명을 AI로 자동 생성합니다.

    예시 요청:
    ```json
    {
      "store_id": 1,
      "categories": [
        {
          "category_name": "파스타",
          "items": [
            {
              "name": "까르보나라",
              "price": 15000,
              "ingredients": ["파스타면", "베이컨", "크림", "파마산 치즈"]
            },
            {
              "name": "알리오 올리오",
              "price": 13000
            }
          ]
        },
        {
          "category_name": "스테이크",
          "items": [
            {
              "name": "티본 스테이크",
              "price": 35000
            }
          ]
        }
      ],
      "auto_generate_images": true,
      "auto_generate_descriptions": true
    }
    ```
    """
    try:
        logger.info(
            f"메뉴판 생성 요청 - Store: {request.store_id}, "
            f"카테고리: {len(request.categories)}개"
        )

        # 메뉴판 생성
        categories, generation_time = await menu_generation_service.generate_menu(
            db=db,
            request=request
        )

        # 통계 계산
        total_items = sum(len(cat.items) for cat in categories)

        # 응답 데이터 구성
        response_data = {
            "categories": [cat.model_dump() for cat in categories],
            "total_categories": len(categories),
            "total_items": total_items,
            "generation_time": round(generation_time, 2)
        }

        logger.info(
            f"메뉴판 생성 완료 - 카테고리: {len(categories)}개, "
            f"아이템: {total_items}개, 시간: {generation_time:.2f}초"
        )

        return MenuGenerationResponse(
            success=True,
            data=response_data
        )

    except ValueError as e:
        logger.error(f"잘못된 요청: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": 400,
                    "message": "잘못된 요청입니다.",
                    "details": str(e)
                }
            }
        )

    except Exception as e:
        logger.error(f"메뉴판 생성 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": 500,
                    "message": "메뉴판 생성 중 오류가 발생했습니다.",
                    "details": str(e)
                }
            }
        )


@router.get(
    "/health",
    summary="헬스 체크",
    description="메뉴 생성 API 서비스 상태를 확인합니다."
)
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "service": "Menu Generation API",
            "version": "1.0.0"
        }
    }
