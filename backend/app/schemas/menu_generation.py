"""
메뉴판 생성 API Schemas
메뉴 카테고리와 아이템을 AI로 생성하는 API의 Request/Response 스키마
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal


class MenuItemCreate(BaseModel):
    """메뉴 아이템 생성 요청"""
    name: str = Field(..., description="메뉴 이름 (필수)", min_length=1, max_length=100)
    price: Optional[Decimal] = Field(None, description="가격 (선택)", ge=0)
    image_url: Optional[str] = Field(None, description="이미지 URL (선택, 없으면 AI가 생성)")
    description: Optional[str] = Field(None, description="메뉴 설명 (선택, 없으면 AI가 생성)")
    ingredients: Optional[List[str]] = Field(None, description="재료 리스트 (선택)")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "까르보나라 파스타",
                "price": 15000,
                "image_url": None,
                "description": None,
                "ingredients": ["파스타면", "베이컨", "크림", "파마산 치즈", "달걀"]
            }
        }


class MenuCategoryCreate(BaseModel):
    """메뉴 카테고리 생성 요청"""
    category_name: str = Field(..., description="카테고리 이름 (예: 파스타, 스테이크)", min_length=1, max_length=100)
    category_description: Optional[str] = Field(None, description="카테고리 설명 (선택)")
    items: List[MenuItemCreate] = Field(..., description="메뉴 아이템 리스트", min_items=1)

    class Config:
        json_schema_extra = {
            "example": {
                "category_name": "파스타",
                "category_description": "정통 이탈리안 파스타",
                "items": [
                    {
                        "name": "까르보나라 파스타",
                        "price": 15000,
                        "ingredients": ["파스타면", "베이컨", "크림", "파마산 치즈"]
                    },
                    {
                        "name": "알리오 올리오",
                        "price": 13000
                    }
                ]
            }
        }


class MenuGenerationRequest(BaseModel):
    """메뉴판 생성 요청"""
    store_id: int = Field(..., description="매장 ID", gt=0)
    categories: List[MenuCategoryCreate] = Field(..., description="메뉴 카테고리 리스트", min_items=1)
    auto_generate_images: bool = Field(True, description="이미지 자동 생성 여부 (기본: True)")
    auto_generate_descriptions: bool = Field(True, description="설명 자동 생성 여부 (기본: True)")
    image_style: Optional[str] = Field("food photography, professional, appetizing", description="이미지 생성 스타일")

    class Config:
        json_schema_extra = {
            "example": {
                "store_id": 1,
                "categories": [
                    {
                        "category_name": "파스타",
                        "items": [
                            {"name": "까르보나라", "price": 15000},
                            {"name": "알리오 올리오", "price": 13000}
                        ]
                    },
                    {
                        "category_name": "스테이크",
                        "items": [
                            {"name": "티본 스테이크", "price": 35000},
                            {"name": "안심 스테이크", "price": 32000}
                        ]
                    }
                ],
                "auto_generate_images": True,
                "auto_generate_descriptions": True
            }
        }


class GeneratedMenuItem(BaseModel):
    """생성된 메뉴 아이템"""
    id: int = Field(..., description="메뉴 아이템 ID")
    name: str = Field(..., description="메뉴 이름")
    description: Optional[str] = Field(None, description="메뉴 설명")
    price: Optional[Decimal] = Field(None, description="가격")
    image_url: Optional[str] = Field(None, description="이미지 URL")
    is_ai_generated_image: bool = Field(False, description="AI가 이미지를 생성했는지 여부")
    is_ai_generated_description: bool = Field(False, description="AI가 설명을 생성했는지 여부")


class GeneratedMenuCategory(BaseModel):
    """생성된 메뉴 카테고리"""
    id: int = Field(..., description="메뉴 카테고리 ID")
    name: str = Field(..., description="카테고리 이름")
    description: Optional[str] = Field(None, description="카테고리 설명")
    items: List[GeneratedMenuItem] = Field(..., description="생성된 메뉴 아이템 리스트")


class MenuGenerationResponse(BaseModel):
    """메뉴판 생성 응답"""
    success: bool = Field(True, description="성공 여부")
    data: dict = Field(..., description="생성 결과")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "categories": [
                        {
                            "id": 1,
                            "name": "파스타",
                            "description": "정통 이탈리안 파스타",
                            "items": [
                                {
                                    "id": 1,
                                    "name": "까르보나라",
                                    "description": "크림과 베이컨이 조화로운 정통 이탈리안 파스타",
                                    "price": 15000,
                                    "image_url": "/static/uploads/carbonara_123.jpg",
                                    "is_ai_generated_image": True,
                                    "is_ai_generated_description": True
                                }
                            ]
                        }
                    ],
                    "total_categories": 1,
                    "total_items": 1,
                    "generation_time": 12.5
                }
            }
        }
