"""
Menu API Endpoints
메뉴 필터링 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.schemas.menu import (
    MenuFilterRequest, MenuFilterResponse,
    MenuItemUpdateRequest, MenuItemUpdateResponse,
    StoreCreateRequest, StoreUpdateRequest, StoreResponse
)
from app.services.menu_filter_service import menu_filter_service
from app.core.logging import app_logger as logger
from app.core.database import get_db
from app.models.menu import Menu, MenuItem, Store
import os
import uuid
from pathlib import Path
from datetime import datetime
from typing import List


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

        # 매장 정보 조회
        store = db.query(Store).filter(Store.id == store_id).first()

        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {
                        "code": 404,
                        "message": f"매장을 찾을 수 없습니다. (ID: {store_id})"
                    }
                }
            )

        # 매장의 모든 카테고리(메뉴) 조회
        menus = db.query(Menu).filter(Menu.store_id == store_id).all()

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
                        "is_available": item.is_available,
                        "is_ai_generated_image": item.is_ai_generated_image if hasattr(item, 'is_ai_generated_image') else False,
                        "is_ai_generated_description": item.is_ai_generated_description if hasattr(item, 'is_ai_generated_description') else False,
                        "ingredients": [ing.ingredient_name for ing in item.ingredients] if item.ingredients else [],
                        "nutrition": {
                            "calories": float(item.nutrition_estimate.calories) if item.nutrition_estimate and item.nutrition_estimate.calories else None,
                            "sugar_g": float(item.nutrition_estimate.sugar_g) if item.nutrition_estimate and item.nutrition_estimate.sugar_g else None,
                            "caffeine_mg": float(item.nutrition_estimate.caffeine_mg) if item.nutrition_estimate and item.nutrition_estimate.caffeine_mg else None,
                            "protein_g": float(item.nutrition_estimate.protein_g) if item.nutrition_estimate and item.nutrition_estimate.protein_g else None,
                            "fat_g": float(item.nutrition_estimate.fat_g) if item.nutrition_estimate and item.nutrition_estimate.fat_g else None,
                            "carbs_g": float(item.nutrition_estimate.carbs_g) if item.nutrition_estimate and item.nutrition_estimate.carbs_g else None,
                            "confidence": float(item.nutrition_estimate.confidence) if item.nutrition_estimate and item.nutrition_estimate.confidence else None,
                        } if item.nutrition_estimate else None
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
                "store_name": store.name,
                "store_address": store.address,
                "store_phone": store.phone,
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


@router.put(
    "/item/{item_id}",
    response_model=MenuItemUpdateResponse,
    summary="메뉴 아이템 업데이트",
    description="메뉴 아이템의 정보를 업데이트합니다."
)
async def update_menu_item(
    item_id: int,
    request: MenuItemUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    메뉴 아이템 업데이트

    메뉴 아이템의 이름, 설명, 가격, 이미지 URL을 업데이트합니다.
    """
    try:
        logger.info(f"Updating menu item: item_id={item_id}")

        # 메뉴 아이템 조회
        menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()

        if not menu_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {
                        "code": 404,
                        "message": f"메뉴 아이템을 찾을 수 없습니다. (ID: {item_id})"
                    }
                }
            )

        # 업데이트할 필드만 변경
        if request.name is not None:
            menu_item.name = request.name
        if request.description is not None:
            menu_item.description = request.description
        if request.price is not None:
            menu_item.price = request.price
        if request.image_url is not None:
            menu_item.image_url = request.image_url

        # DB 저장
        db.commit()
        db.refresh(menu_item)

        logger.info(f"Menu item updated successfully: item_id={item_id}")

        return MenuItemUpdateResponse(
            success=True,
            data={
                "id": menu_item.id,
                "name": menu_item.name,
                "description": menu_item.description,
                "price": float(menu_item.price) if menu_item.price else None,
                "image_url": menu_item.image_url
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update menu item: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": 500,
                    "message": "메뉴 아이템 업데이트 중 오류가 발생했습니다.",
                    "details": str(e)
                }
            }
        )


@router.post(
    "/item/{item_id}/upload-image",
    summary="메뉴 이미지 직접 업로드",
    description="메뉴 아이템의 이미지를 직접 업로드합니다."
)
async def upload_menu_image(
    item_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    메뉴 이미지 업로드

    이미지 파일을 업로드하여 메뉴 아이템에 연결합니다.
    """
    try:
        logger.info(f"Uploading image for menu item: item_id={item_id}, filename={file.filename}")

        # 메뉴 아이템 확인
        menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
        if not menu_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {
                        "code": 404,
                        "message": f"메뉴 아이템을 찾을 수 없습니다. (ID: {item_id})"
                    }
                }
            )

        # 파일 확장자 확인
        allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error": {
                        "code": 400,
                        "message": f"지원하지 않는 파일 형식입니다. 허용된 형식: {', '.join(allowed_extensions)}"
                    }
                }
            )

        # 저장 경로 설정
        upload_dir = Path("backend/data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)

        # 고유한 파일명 생성
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = upload_dir / unique_filename

        # 파일 저장
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # 상대 경로로 변환 (API 응답용)
        relative_path = f"/data/uploads/{unique_filename}"

        # DB 업데이트
        menu_item.image_url = relative_path
        db.commit()
        db.refresh(menu_item)

        logger.info(f"Image uploaded successfully: {relative_path}")

        return {
            "success": True,
            "data": {
                "id": menu_item.id,
                "image_url": relative_path,
                "filename": unique_filename
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload image: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": 500,
                    "message": "이미지 업로드 중 오류가 발생했습니다.",
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


# ============ Store (매장) CRUD API ============

@router.post(
    "/store",
    summary="매장 생성",
    description="새로운 매장을 생성합니다."
)
async def create_store(
    request: StoreCreateRequest,
    db: Session = Depends(get_db)
):
    """
    매장 생성

    새로운 매장 정보를 DB에 저장합니다.
    """
    try:
        logger.info(f"Creating new store: {request.name}")

        # 시간 문자열을 time 객체로 변환
        open_time_obj = None
        close_time_obj = None

        if request.open_time:
            try:
                hour, minute = request.open_time.split(":")
                open_time_obj = datetime.strptime(f"{hour}:{minute}", "%H:%M").time()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="오픈 시간 형식이 올바르지 않습니다. HH:MM 형식으로 입력해주세요."
                )

        if request.close_time:
            try:
                hour, minute = request.close_time.split(":")
                close_time_obj = datetime.strptime(f"{hour}:{minute}", "%H:%M").time()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="마감 시간 형식이 올바르지 않습니다. HH:MM 형식으로 입력해주세요."
                )

        # 새 매장 생성
        new_store = Store(
            name=request.name,
            address=request.address,
            phone=request.phone,
            open_time=open_time_obj,
            close_time=close_time_obj
        )

        db.add(new_store)
        db.commit()
        db.refresh(new_store)

        logger.info(f"Store created successfully: id={new_store.id}, name={new_store.name}")

        return {
            "success": True,
            "data": {
                "id": new_store.id,
                "name": new_store.name,
                "address": new_store.address,
                "phone": new_store.phone,
                "open_time": new_store.open_time.strftime("%H:%M") if new_store.open_time else None,
                "close_time": new_store.close_time.strftime("%H:%M") if new_store.close_time else None,
                "created_at": new_store.created_at.isoformat(),
                "updated_at": new_store.updated_at.isoformat()
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create store: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": 500,
                    "message": "매장 생성 중 오류가 발생했습니다.",
                    "details": str(e)
                }
            }
        )


@router.get(
    "/stores",
    summary="매장 목록 조회",
    description="전체 매장 목록을 조회합니다."
)
async def get_stores(db: Session = Depends(get_db)):
    """
    매장 목록 조회

    등록된 모든 매장을 조회합니다.
    """
    try:
        logger.info("Fetching all stores")

        stores = db.query(Store).all()

        store_list = [
            {
                "id": store.id,
                "name": store.name,
                "address": store.address,
                "phone": store.phone,
                "open_time": store.open_time.strftime("%H:%M") if store.open_time else None,
                "close_time": store.close_time.strftime("%H:%M") if store.close_time else None,
                "created_at": store.created_at.isoformat(),
                "updated_at": store.updated_at.isoformat()
            }
            for store in stores
        ]

        logger.info(f"Found {len(store_list)} stores")

        return {
            "success": True,
            "data": {
                "stores": store_list,
                "total": len(store_list)
            }
        }

    except Exception as e:
        logger.error(f"Failed to fetch stores: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": 500,
                    "message": "매장 조회 중 오류가 발생했습니다.",
                    "details": str(e)
                }
            }
        )


@router.get(
    "/store/{store_id}",
    summary="매장 상세 조회",
    description="특정 매장의 상세 정보를 조회합니다."
)
async def get_store(store_id: int, db: Session = Depends(get_db)):
    """
    매장 상세 조회

    매장 ID로 특정 매장의 정보를 조회합니다.
    """
    try:
        logger.info(f"Fetching store: id={store_id}")

        store = db.query(Store).filter(Store.id == store_id).first()

        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {
                        "code": 404,
                        "message": f"매장을 찾을 수 없습니다. (ID: {store_id})"
                    }
                }
            )

        return {
            "success": True,
            "data": {
                "id": store.id,
                "name": store.name,
                "address": store.address,
                "phone": store.phone,
                "open_time": store.open_time.strftime("%H:%M") if store.open_time else None,
                "close_time": store.close_time.strftime("%H:%M") if store.close_time else None,
                "created_at": store.created_at.isoformat(),
                "updated_at": store.updated_at.isoformat()
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch store {store_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": 500,
                    "message": "매장 조회 중 오류가 발생했습니다.",
                    "details": str(e)
                }
            }
        )


@router.put(
    "/store/{store_id}",
    summary="매장 정보 수정",
    description="매장 정보를 수정합니다."
)
async def update_store(
    store_id: int,
    request: StoreUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    매장 정보 수정

    매장의 정보를 업데이트합니다.
    """
    try:
        logger.info(f"Updating store: id={store_id}")

        store = db.query(Store).filter(Store.id == store_id).first()

        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {
                        "code": 404,
                        "message": f"매장을 찾을 수 없습니다. (ID: {store_id})"
                    }
                }
            )

        # 업데이트할 필드만 변경
        if request.name is not None:
            store.name = request.name
        if request.address is not None:
            store.address = request.address
        if request.phone is not None:
            store.phone = request.phone

        if request.open_time is not None:
            try:
                hour, minute = request.open_time.split(":")
                store.open_time = datetime.strptime(f"{hour}:{minute}", "%H:%M").time()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="오픈 시간 형식이 올바르지 않습니다. HH:MM 형식으로 입력해주세요."
                )

        if request.close_time is not None:
            try:
                hour, minute = request.close_time.split(":")
                store.close_time = datetime.strptime(f"{hour}:{minute}", "%H:%M").time()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="마감 시간 형식이 올바르지 않습니다. HH:MM 형식으로 입력해주세요."
                )

        db.commit()
        db.refresh(store)

        logger.info(f"Store updated successfully: id={store_id}")

        return {
            "success": True,
            "data": {
                "id": store.id,
                "name": store.name,
                "address": store.address,
                "phone": store.phone,
                "open_time": store.open_time.strftime("%H:%M") if store.open_time else None,
                "close_time": store.close_time.strftime("%H:%M") if store.close_time else None,
                "created_at": store.created_at.isoformat(),
                "updated_at": store.updated_at.isoformat()
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update store {store_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": 500,
                    "message": "매장 수정 중 오류가 발생했습니다.",
                    "details": str(e)
                }
            }
        )


@router.delete(
    "/store/{store_id}",
    summary="매장 삭제",
    description="매장을 삭제합니다. 매장의 모든 메뉴도 함께 삭제됩니다."
)
async def delete_store(store_id: int, db: Session = Depends(get_db)):
    """
    매장 삭제

    매장을 삭제합니다. CASCADE로 인해 매장의 모든 메뉴도 함께 삭제됩니다.
    """
    try:
        logger.info(f"Deleting store: id={store_id}")

        store = db.query(Store).filter(Store.id == store_id).first()

        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {
                        "code": 404,
                        "message": f"매장을 찾을 수 없습니다. (ID: {store_id})"
                    }
                }
            )

        db.delete(store)
        db.commit()

        logger.info(f"Store deleted successfully: id={store_id}")

        return {
            "success": True,
            "data": {
                "message": f"매장 ID {store_id}가 성공적으로 삭제되었습니다."
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete store {store_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": 500,
                    "message": "매장 삭제 중 오류가 발생했습니다.",
                    "details": str(e)
                }
            }
        )
