"""
Seasonal Story API Endpoints
시즈널 스토리 생성 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import pytz
import time

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
from app.services.menu_service import menu_service
from app.models.seasonal_story import SeasonalStory
from app.core.database import get_db
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
async def generate_seasonal_story(
    request: SeasonalStoryRequest,
    db: Session = Depends(get_db)
):
    """
    시즈널 스토리 생성

    현재 날씨, 계절, 시간대, 트렌드 정보를 수집하여
    LLM 기반으로 감성적인 추천 문구를 생성합니다.
    """
    start_time = time.time()

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

        # 2. 메뉴 정보 조회 (store_id가 있는 경우)
        menu_items = []
        menu_text = None
        if request.store_id:
            try:
                menu_items = menu_service.get_popular_menus(db, request.store_id, limit=5)
                if menu_items:
                    menu_text = menu_service.format_menus_for_story(menu_items)
                    logger.info(f"Retrieved {len(menu_items)} menus for store {request.store_id}")
            except Exception as e:
                logger.warning(f"Failed to get menus for store {request.store_id}: {e}")

        # 3. 스토리 생성
        story = story_generator_service.generate_story(
            context=context,
            store_name=request.store_name,
            store_type=request.store_type,
            menu_categories=request.menu_categories,
            selected_trends=request.selected_trends,
            menu_text=menu_text  # 메뉴 정보 전달
        )

        # 4. DB에 저장
        try:
            seasonal_story = SeasonalStory(
                store_id=request.store_id,
                store_name=request.store_name,
                store_type=request.store_type,
                story_content=story,
                weather_condition=context.get("weather", {}).get("condition"),
                temperature=context.get("weather", {}).get("temperature"),
                season=context.get("season"),
                time_period=context.get("time_info", {}).get("period"),
                google_trends=context.get("google_trends", []),
                instagram_trends=context.get("instagram_trends", []),
                selected_trends=request.selected_trends,
                menu_items=[{"id": m["id"], "name": m["name"], "price": m["price"]} for m in menu_items] if menu_items else None
            )
            db.add(seasonal_story)
            db.commit()
            db.refresh(seasonal_story)
            logger.info(f"Seasonal story saved to DB with ID: {seasonal_story.id}")
        except Exception as e:
            logger.error(f"Failed to save story to DB: {e}")
            db.rollback()

        # 5. 응답 생성
        korea_tz = pytz.timezone('Asia/Seoul')
        generation_time = time.time() - start_time

        response_data = {
            "story": story,
            "context": {
                "weather": context.get("weather"),
                "season": context.get("season"),
                "time_info": context.get("time_info"),
                "trends": context.get("trends", []),
                "google_trends": context.get("google_trends", []),
                "instagram_trends": context.get("instagram_trends", []),
                "google_trends_status": context.get("google_trends_status"),
                "instagram_trends_status": context.get("instagram_trends_status")
            },
            "store_info": {
                "store_id": request.store_id,
                "store_name": request.store_name,
                "store_type": request.store_type,
                "location": request.location
            },
            "menu_items": menu_items if menu_items else [],
            "generated_at": datetime.now(korea_tz).isoformat(),
            "generation_time": round(generation_time, 2)
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
            include_all_trends=True,
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
            menu_items = db.query(MenuItem).join(Menu).filter(
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

            # 메뉴 정보를 dict로 변환
            menus = []
            for item in menu_items:
                menus.append({
                    "id": item.id,
                    "name": item.name,
                    "description": item.description or "",
                    "price": float(item.price) if item.price else 0,
                    "category": ""  # 카테고리 정보가 있다면 추가
                })

            store_type = "카페"  # 기본값

        finally:
            db.close()

        # 컨텍스트 수집
        context = context_collector_service.get_full_context(
            location=location,
            include_all_trends=True,
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
