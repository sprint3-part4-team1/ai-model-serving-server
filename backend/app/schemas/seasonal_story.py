"""
Seasonal Story Schemas
시즈널 스토리 생성 API의 Request/Response 스키마
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class SeasonalStoryRequest(BaseModel):
    """시즈널 스토리 생성 요청"""

    store_id: Optional[int] = Field(None, description="매장 ID")
    store_name: Optional[str] = Field(None, description="매장 이름")
    store_type: str = Field("카페", description="매장 타입 (카페, 레스토랑 등)")
    location: str = Field("Seoul", description="위치 (도시 이름)")
    latitude: Optional[float] = Field(None, description="위도")
    longitude: Optional[float] = Field(None, description="경도")
    menu_categories: Optional[List[str]] = Field(
        None,
        description="메뉴 카테고리 (예: ['커피', '디저트'])"
    )
    selected_trends: Optional[List[str]] = Field(
        None,
        description="사용자가 선택한 트렌드 키워드 (우선적으로 반영됨)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "store_id": 1,
                "store_name": "서울카페",
                "store_type": "카페",
                "location": "Seoul",
                "menu_categories": ["커피", "디저트"]
            }
        }


class MenuStorytellingRequest(BaseModel):
    """메뉴 스토리텔링 생성 요청"""

    menu_id: Optional[int] = Field(None, description="메뉴 ID")
    menu_name: str = Field(..., description="메뉴 이름")
    ingredients: List[str] = Field(..., description="재료 리스트")
    origin: Optional[str] = Field(None, description="원산지")
    history: Optional[str] = Field(None, description="메뉴 역사")

    class Config:
        json_schema_extra = {
            "example": {
                "menu_id": 1,
                "menu_name": "아메리카노",
                "ingredients": ["에스프레소", "물"],
                "origin": "이탈리아",
                "history": "제2차 세계대전 중 미군이 에스프레소에 물을 타서 마신 것이 유래"
            }
        }


class ContextInfo(BaseModel):
    """컨텍스트 정보"""

    weather: Dict[str, Any] = Field(..., description="날씨 정보")
    season: str = Field(..., description="계절 (spring/summer/autumn/winter)")
    time_info: Dict[str, Any] = Field(..., description="시간대 정보")
    trends: List[str] = Field([], description="트렌드 키워드")
    location: str = Field(..., description="위치")


class SeasonalStoryResponse(BaseModel):
    """시즈널 스토리 생성 응답"""

    success: bool = Field(True, description="성공 여부")
    data: Dict[str, Any] = Field(..., description="응답 데이터")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "story": "비 오는 가을 오후, 따뜻한 아메리카노 한 잔과 함께 여유를 느껴보세요.",
                    "context": {
                        "weather": {
                            "condition": "rain",
                            "description": "비",
                            "temperature": 15.0
                        },
                        "season": "autumn",
                        "time_info": {
                            "period": "afternoon",
                            "period_kr": "오후"
                        }
                    },
                    "generated_at": "2025-11-18T14:30:00+09:00"
                }
            }
        }


class MenuStorytellingResponse(BaseModel):
    """메뉴 스토리텔링 응답"""

    success: bool = Field(True, description="성공 여부")
    data: Dict[str, Any] = Field(..., description="응답 데이터")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "storytelling": "이탈리아에서 시작된 에스프레소에 물을 더해 탄생한 아메리카노. 깊고 진한 커피 본연의 맛을 느낄 수 있습니다.",
                    "menu_name": "아메리카노",
                    "generated_at": "2025-11-18T14:30:00+09:00"
                }
            }
        }


class WelcomeMessageRequest(BaseModel):
    """환영 문구 생성 요청"""

    store_id: int = Field(..., description="매장 ID")
    location: Optional[str] = Field("Seoul", description="위치 (도시 이름)")

    class Config:
        json_schema_extra = {
            "example": {
                "store_id": 1,
                "location": "Seoul"
            }
        }


class MenuHighlightRequest(BaseModel):
    """메뉴 하이라이트 요청"""

    store_id: int = Field(..., description="매장 ID")
    location: Optional[str] = Field("Seoul", description="위치")
    max_highlights: Optional[int] = Field(3, description="최대 하이라이트 개수")

    class Config:
        json_schema_extra = {
            "example": {
                "store_id": 1,
                "location": "Seoul",
                "max_highlights": 3
            }
        }


class ErrorResponse(BaseModel):
    """에러 응답"""

    success: bool = Field(False, description="성공 여부")
    error: Dict[str, Any] = Field(..., description="에러 정보")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": {
                    "code": 500,
                    "message": "스토리 생성 중 오류가 발생했습니다.",
                    "details": None
                }
            }
        }
