"""
Menu Filter Schemas
메뉴 필터링 API의 Request/Response 스키마
"""

from pydantic import BaseModel, Field
from typing import List, Optional


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
