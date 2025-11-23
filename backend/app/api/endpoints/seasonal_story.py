"""
Seasonal Story API Endpoints
시즈널 스토리 생성 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import pytz

from app.schemas.seasonal_story import (
    SeasonalStoryRequest,
    SeasonalStoryResponse,
    MenuStorytellingRequest,
    MenuStorytellingResponse,
    ContextInfo,
    ErrorResponse
)
from app.services.context_collector import context_collector_service
from app.services.story_generator import story_generator_service
from app.core.logging import app_logger as logger


router = APIRouter()


@router.post(
    "/generate",
    response_model=SeasonalStoryResponse,
    summary="시즈널 스토리 생성",
    description="날씨, 계절, 시간대, 트렌드를 반영한 감성적인 추천 문구를 생성합니다.",
    responses={
        200: {"description": "성공", "model": SeasonalStoryResponse},
        500: {"description": "서버 오류", "model": ErrorResponse}
    }
)
async def generate_seasonal_story(request: SeasonalStoryRequest):
    """
    시즈널 스토리 생성

    현재 날씨, 계절, 시간대, 트렌드 정보를 수집하여
    LLM 기반으로 감성적인 추천 문구를 생성합니다.
    """
    try:
        logger.info(f"Seasonal story generation requested: {request}")

        # 1. 컨텍스트 정보 수집 (매장 타입 기반)
        context = context_collector_service.get_full_context(
            location=request.location,
            lat=request.latitude,
            lon=request.longitude,
            include_all_trends=True,
            store_type=request.store_type
        )

        # 2. 스토리 생성
        story = story_generator_service.generate_story(
            context=context,
            store_name=request.store_name,
            store_type=request.store_type,
            menu_categories=request.menu_categories
        )

        # 3. 응답 생성
        korea_tz = pytz.timezone('Asia/Seoul')
        response_data = {
            "story": story,
            "context": {
                "weather": context.get("weather"),
                "season": context.get("season"),
                "time_info": context.get("time_info"),
                "trends": context.get("trends", []),
                "google_trends": context.get("google_trends", []),
                "instagram_trends": context.get("instagram_trends", [])
            },
            "store_info": {
                "store_id": request.store_id,
                "store_name": request.store_name,
                "store_type": request.store_type,
                "location": request.location
            },
            "generated_at": datetime.now(korea_tz).isoformat()
        }

        logger.info("Seasonal story generated successfully")

        return SeasonalStoryResponse(
            success=True,
            data=response_data
        )

    except Exception as e:
        logger.error(f"Failed to generate seasonal story: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": 500,
                    "message": "스토리 생성 중 오류가 발생했습니다.",
                    "details": str(e)
                }
            }
        )


@router.post(
    "/menu-storytelling",
    response_model=MenuStorytellingResponse,
    summary="메뉴 스토리텔링 생성",
    description="메뉴 클릭 시 보여줄 스토리텔링 문구를 생성합니다.",
    responses={
        200: {"description": "성공", "model": MenuStorytellingResponse},
        500: {"description": "서버 오류", "model": ErrorResponse}
    }
)
async def generate_menu_storytelling(request: MenuStorytellingRequest):
    """
    메뉴 스토리텔링 생성

    메뉴 이름, 재료, 원산지, 역사 정보를 바탕으로
    감성적인 스토리텔링 문구를 생성합니다.
    """
    try:
        logger.info(f"Menu storytelling generation requested: {request}")

        # 스토리텔링 생성
        storytelling = story_generator_service.generate_menu_storytelling(
            menu_name=request.menu_name,
            ingredients=request.ingredients,
            origin=request.origin,
            history=request.history
        )

        # 응답 생성
        korea_tz = pytz.timezone('Asia/Seoul')
        response_data = {
            "storytelling": storytelling,
            "menu_id": request.menu_id,
            "menu_name": request.menu_name,
            "generated_at": datetime.now(korea_tz).isoformat()
        }

        logger.info("Menu storytelling generated successfully")

        return MenuStorytellingResponse(
            success=True,
            data=response_data
        )

    except Exception as e:
        logger.error(f"Failed to generate menu storytelling: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": 500,
                    "message": "메뉴 스토리텔링 생성 중 오류가 발생했습니다.",
                    "details": str(e)
                }
            }
        )


@router.get(
    "/context",
    response_model=dict,
    summary="현재 컨텍스트 정보 조회",
    description="현재 날씨, 계절, 시간대, 트렌드 정보를 조회합니다.",
    responses={
        200: {"description": "성공"},
        500: {"description": "서버 오류"}
    }
)
async def get_current_context(
    location: str = "Seoul",
    lat: float = None,
    lon: float = None
):
    """
    현재 컨텍스트 정보 조회

    스토리 생성 없이 현재 컨텍스트 정보만 조회합니다.
    테스트 및 디버깅 용도로 사용할 수 있습니다.
    """
    try:
        logger.info(f"Context info requested for location: {location}")

        # 컨텍스트 정보 수집
        context = context_collector_service.get_full_context(
            location=location,
            lat=lat,
            lon=lon,
            include_all_trends=True
        )

        logger.info("Context info retrieved successfully")

        return {
            "success": True,
            "data": context
        }

    except Exception as e:
        logger.error(f"Failed to get context info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": 500,
                    "message": "컨텍스트 정보 조회 중 오류가 발생했습니다.",
                    "details": str(e)
                }
            }
        )


@router.get(
    "/health",
    summary="헬스 체크",
    description="시즈널 스토리 API 서비스 상태를 확인합니다."
)
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "service": "Seasonal Story API",
            "version": "1.0.0"
        }
    }
