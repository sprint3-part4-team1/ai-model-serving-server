"""
Seasonal Story API Endpoints
시즈널 스토리 생성 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import pytz
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ...schemas.seasonal_story import (
    SeasonalStoryRequest,
    SeasonalStoryResponse,
    MenuStorytellingRequest,
    MenuStorytellingResponse,
    ContextInfo,
    ErrorResponse
)
from ...services.context_collector import context_collector_service
from ...services.story_generator import story_generator_service
from ...logger import app_logger as logger


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

        # 1. 컨텍스트 정보 수집 (메뉴 카테고리 + 매장 타입 포함)
        context = context_collector_service.get_full_context(
            location=request.location,
            lat=request.latitude,
            lon=request.longitude,
            menu_categories=request.menu_categories,
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
                "trends": context.get("trends", [])
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
    "/generate-variants",
    response_model=SeasonalStoryResponse,
    summary="시즈널 스토리 다중 생성 (A/B 테스트)",
    description="동일한 컨텍스트로 여러 버전의 스토리를 생성합니다 (A/B 테스트용).",
    tags=["Seasonal Story"]
)
async def generate_seasonal_story_variants(request: SeasonalStoryRequest):
    """
    시즈널 스토리 다중 버전 생성 (A/B 테스트)

    동일한 컨텍스트로 3가지 버전의 스토리를 생성하여
    가장 효과적인 문구를 선택할 수 있습니다.
    """
    try:
        logger.info(f"Multi-variant story generation requested: {request}")

        # 1. 컨텍스트 정보 수집 (메뉴 카테고리 + 매장 타입 포함)
        context = context_collector_service.get_full_context(
            location=request.location,
            lat=request.latitude,
            lon=request.longitude,
            menu_categories=request.menu_categories,
            store_type=request.store_type
        )

        # 2. 다중 스토리 생성
        stories = story_generator_service.generate_multiple_stories(
            context=context,
            store_name=request.store_name,
            store_type=request.store_type,
            menu_categories=request.menu_categories,
            count=3
        )

        # 3. 응답 생성
        korea_tz = pytz.timezone('Asia/Seoul')
        response_data = {
            "stories": [
                {
                    "variant": f"Version {i+1}",
                    "story": story
                }
                for i, story in enumerate(stories)
            ],
            "context": {
                "weather": context.get("weather"),
                "season": context.get("season"),
                "time_info": context.get("time_info"),
                "trends": context.get("trends", [])
            },
            "store_info": {
                "store_id": request.store_id,
                "store_name": request.store_name,
                "store_type": request.store_type,
                "location": request.location
            },
            "generated_at": datetime.now(korea_tz).isoformat()
        }

        logger.info("Multi-variant stories generated successfully")

        return SeasonalStoryResponse(
            success=True,
            data=response_data
        )

    except Exception as e:
        logger.error(f"Failed to generate multi-variant stories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": 500,
                    "message": "다중 스토리 생성 중 오류가 발생했습니다.",
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
            lon=lon
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
    "/welcome-message/{store_id}",
    response_model=dict,
    summary="환영 문구 생성",
    description="매장의 환영 문구를 생성합니다. 날씨, 계절, 시간대, 트렌드를 반영합니다.",
    responses={
        200: {"description": "성공"},
        500: {"description": "서버 오류"}
    }
)
async def get_welcome_message(
    store_id: int,
    location: str = "Seoul"
):
    """
    메뉴판 상단 환영 문구 생성

    날씨, 계절, 시간대, 트렌드를 반영하여 매력적인 환영 문구를 생성합니다.
    """
    try:
        # backend/app 모듈 import
        from app.models.menu import Store
        from app.core.database import SessionLocal

        logger.info(f"Welcome message requested for store_id={store_id}")

        # DB에서 매장 정보 조회
        db = SessionLocal()
        try:
            store = db.query(Store).filter(Store.id == store_id).first()

            if not store:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Store with id {store_id} not found"
                )

            store_name = store.name
            # 매장 타입 추론 (이름이나 설명에서)
            store_type = "카페"  # 기본값

        finally:
            db.close()

        # 컨텍스트 수집
        context = context_collector_service.get_full_context(
            location=location,
            store_type=store_type
        )

        # 환영 문구 생성
        welcome_message = story_generator_service.generate_welcome_message(
            context=context,
            store_name=store_name,
            store_type=store_type
        )

        logger.info(f"Welcome message generated: {welcome_message}")

        return {
            "success": True,
            "data": {
                "message": welcome_message,
                "store_id": store_id,
                "store_name": store_name,
                "context": {
                    "weather": context.get("weather"),
                    "season": context.get("season"),
                    "time": context.get("time_info", {}).get("period_kr"),
                    "trends": context.get("instagram_trends", [])[:5]
                },
                "generated_at": datetime.now(pytz.timezone('Asia/Seoul')).isoformat()
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate welcome message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": 500,
                    "message": "환영 문구 생성 중 오류가 발생했습니다.",
                    "details": str(e)
                }
            }
        )


@router.get(
    "/menu-highlights/{store_id}",
    response_model=dict,
    summary="메뉴 하이라이트",
    description="시즌/날씨에 맞는 추천 메뉴를 하이라이트합니다.",
    responses={
        200: {"description": "성공"},
        500: {"description": "서버 오류"}
    }
)
async def get_menu_highlights(
    store_id: int,
    location: str = "Seoul",
    max_highlights: int = 3
):
    """
    시즌/날씨에 맞는 메뉴 하이라이트

    현재 날씨, 계절, 트렌드에 가장 잘 맞는 메뉴를 선택하여 추천 이유와 함께 반환합니다.
    """
    try:
        from app.models.menu import Store, Menu, MenuItem
        from app.core.database import SessionLocal

        logger.info(f"Menu highlights requested for store_id={store_id}")

        # DB에서 매장 및 메뉴 정보 조회
        db = SessionLocal()
        try:
            store = db.query(Store).filter(Store.id == store_id).first()

            if not store:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Store with id {store_id} not found"
                )

            # 매장의 메뉴 아이템 조회 (사용 가능한 메뉴만)
            # 사이드와 음료 카테고리 제외
            menu_items = db.query(MenuItem, Menu.name.label("category_name")).join(Menu).filter(
                Menu.store_id == store_id,
                MenuItem.is_available == True
            ).all()

            if not menu_items:
                return {
                    "success": True,
                    "data": {
                        "highlights": [],
                        "message": "조회 가능한 메뉴가 없습니다."
                    }
                }

            # 사이드/음료 제외 키워드
            exclude_keywords = ["사이드", "side", "음료", "drink", "beverage", "드링크", "디저트", "dessert"]

            # 메뉴 정보를 dict로 변환 (사이드/음료 제외)
            menus = []
            for item, category_name in menu_items:
                # 카테고리 이름에 제외 키워드가 포함되어 있으면 스킵
                if any(keyword in category_name.lower() for keyword in exclude_keywords):
                    continue

                menus.append({
                    "id": item.id,
                    "name": item.name,
                    "description": item.description or "",
                    "price": float(item.price) if item.price else 0,
                    "category": category_name
                })

            # 필터링 후 메뉴가 없으면
            if not menus:
                return {
                    "success": True,
                    "data": {
                        "highlights": [],
                        "message": "추천 가능한 메인 메뉴가 없습니다."
                    }
                }

            store_type = "카페"  # 기본값

        finally:
            db.close()

        # 컨텍스트 수집
        context = context_collector_service.get_full_context(
            location=location,
            store_type=store_type
        )

        # 메뉴 하이라이트 생성
        highlights = story_generator_service.generate_menu_highlights(
            context=context,
            menus=menus,
            store_type=store_type,
            max_highlights=max_highlights
        )

        logger.info(f"{len(highlights)} menu highlights generated")

        return {
            "success": True,
            "data": {
                "highlights": highlights,
                "total_menus": len(menus),
                "context": {
                    "weather": context.get("weather"),
                    "season": context.get("season"),
                    "time": context.get("time_info", {}).get("period_kr"),
                    "trends": context.get("instagram_trends", [])[:5]
                },
                "generated_at": datetime.now(pytz.timezone('Asia/Seoul')).isoformat()
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate menu highlights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": 500,
                    "message": "메뉴 하이라이트 생성 중 오류가 발생했습니다.",
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
