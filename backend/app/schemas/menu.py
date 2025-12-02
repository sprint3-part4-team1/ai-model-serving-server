"""
Menu Filter Schemas
메뉴 필터링 API의 Request/Response 스키마
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import time


class MenuItem(BaseModel):
    """메뉴 아이템"""
    id: int = Field(..., description="메뉴 ID")
    name: str = Field(..., description="메뉴 이름")
    category: str = Field(..., description="카테고리 (커피, 디저트, 브런치 등)")
    price: int = Field(..., description="가격")
    description: Optional[str] = Field(None, description="설명")
    ingredients: Optional[List[str]] = Field(None, description="재료 리스트")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "아메리카노",
                "category": "커피",
                "price": 4500,
                "description": "깊고 진한 에스프레소의 맛",
                "ingredients": ["에스프레소", "물"]
            }
        }


class MenuFilterRequest(BaseModel):
    """메뉴 필터링 요청"""
    query: str = Field(..., description="고객 요청 (자연어)", min_length=1)
    menus: List[MenuItem] = Field(..., description="필터링할 메뉴 리스트")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "칼로리 낮은 음료 추천",
                "menus": [
                    {
                        "id": 1,
                        "name": "아메리카노",
                        "category": "커피",
                        "price": 4500,
                        "description": "깊고 진한 에스프레소의 맛",
                        "ingredients": ["에스프레소", "물"]
                    },
                    {
                        "id": 2,
                        "name": "카페라떼",
                        "category": "커피",
                        "price": 5000,
                        "description": "부드러운 우유와 에스프레소의 조화",
                        "ingredients": ["에스프레소", "우유"]
                    }
                ]
            }
        }


class MenuFilterResponse(BaseModel):
    """메뉴 필터링 응답"""
    success: bool = Field(True, description="성공 여부")
    data: dict = Field(..., description="필터링 결과")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "filtered_menus": [
                        {
                            "id": 1,
                            "name": "아메리카노",
                            "category": "커피",
                            "price": 4500,
                            "reason": "저칼로리 음료로 적합합니다"
                        }
                    ],
                    "explanation": "아메리카노는 우유가 들어가지 않아 칼로리가 낮습니다.",
                    "total_count": 1
                }
            }
        }


class MenuItemUpdateRequest(BaseModel):
    """메뉴 아이템 업데이트 요청"""
    name: Optional[str] = Field(None, description="메뉴 이름")
    description: Optional[str] = Field(None, description="메뉴 설명")
    price: Optional[float] = Field(None, description="가격")
    image_url: Optional[str] = Field(None, description="이미지 URL (상대경로)")
    ingredients: Optional[List[str]] = Field(None, description="재료 목록")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "아메리카노",
                "description": "깊고 진한 에스프레소의 맛",
                "price": 4500,
                "image_url": "/data/uploads/menu_images/americano.jpg"
            }
        }


class MenuItemUpdateResponse(BaseModel):
    """메뉴 아이템 업데이트 응답"""
    success: bool = Field(True, description="성공 여부")
    data: dict = Field(..., description="업데이트된 메뉴 정보")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "id": 1,
                    "name": "아메리카노",
                    "description": "깊고 진한 에스프레소의 맛",
                    "price": 4500,
                    "image_url": "/data/uploads/menu_images/americano.jpg"
                }
            }
        }


# ============ Store (매장) 관련 스키마 ============

class StoreCreateRequest(BaseModel):
    """매장 생성 요청"""
    name: str = Field(..., description="매장 이름", min_length=1, max_length=100)
    address: Optional[str] = Field(None, description="매장 주소", max_length=255)
    phone: Optional[str] = Field(None, description="전화번호", max_length=20)
    open_time: Optional[str] = Field(None, description="오픈 시간 (HH:MM 형식)")
    close_time: Optional[str] = Field(None, description="마감 시간 (HH:MM 형식)")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "맛있는 파스타집",
                "address": "서울시 강남구 테헤란로 123",
                "phone": "02-1234-5678",
                "open_time": "11:00",
                "close_time": "22:00"
            }
        }


class StoreUpdateRequest(BaseModel):
    """매장 업데이트 요청"""
    name: Optional[str] = Field(None, description="매장 이름", min_length=1, max_length=100)
    address: Optional[str] = Field(None, description="매장 주소", max_length=255)
    phone: Optional[str] = Field(None, description="전화번호", max_length=20)
    open_time: Optional[str] = Field(None, description="오픈 시간 (HH:MM 형식)")
    close_time: Optional[str] = Field(None, description="마감 시간 (HH:MM 형식)")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "맛있는 파스타집",
                "address": "서울시 강남구 테헤란로 123",
                "phone": "02-1234-5678",
                "open_time": "11:00",
                "close_time": "22:00"
            }
        }


class StoreResponse(BaseModel):
    """매장 응답"""
    id: int = Field(..., description="매장 ID")
    name: str = Field(..., description="매장 이름")
    address: Optional[str] = Field(None, description="매장 주소")
    phone: Optional[str] = Field(None, description="전화번호")
    open_time: Optional[str] = Field(None, description="오픈 시간")
    close_time: Optional[str] = Field(None, description="마감 시간")
    created_at: str = Field(..., description="생성 일시")
    updated_at: str = Field(..., description="수정 일시")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "맛있는 파스타집",
                "address": "서울시 강남구 테헤란로 123",
                "phone": "02-1234-5678",
                "open_time": "11:00",
                "close_time": "22:00",
                "created_at": "2024-11-27T10:00:00",
                "updated_at": "2024-11-27T10:00:00"
            }
        }
