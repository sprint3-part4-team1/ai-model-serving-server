"""
광고 문구 생성 스키마
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum


class AdCopyTone(str, Enum):
    """광고 문구 톤"""
    PROFESSIONAL = "professional"  # 전문적
    FRIENDLY = "friendly"  # 친근한
    EMOTIONAL = "emotional"  # 감성적
    ENERGETIC = "energetic"  # 활기찬
    LUXURY = "luxury"  # 고급스러운
    CASUAL = "casual"  # 캐주얼한


class AdCopyLength(str, Enum):
    """광고 문구 길이"""
    SHORT = "short"  # 짧게 (1-2문장)
    MEDIUM = "medium"  # 중간 (3-5문장)
    LONG = "long"  # 길게 (6문장 이상)


class AdCopyRequest(BaseModel):
    """광고 문구 생성 요청"""

    # 필수 입력
    product_name: str = Field(..., description="제품/서비스 이름", min_length=1, max_length=200)
    product_description: Optional[str] = Field(None, description="제품/서비스 설명", max_length=1000)

    # 이미지 분석 (선택)
    product_image_url: Optional[str] = Field(None, description="제품 이미지 URL")

    # 스타일 설정
    tone: AdCopyTone = Field(default=AdCopyTone.FRIENDLY, description="광고 문구 톤")
    length: AdCopyLength = Field(default=AdCopyLength.SHORT, description="광고 문구 길이")

    # 타겟 고객
    target_audience: Optional[str] = Field(None, description="타겟 고객층", max_length=200)

    # 핵심 메시지
    key_message: Optional[str] = Field(None, description="강조할 핵심 메시지", max_length=300)

    # 플랫폼
    platform: Optional[str] = Field(
        None,
        description="게시 플랫폼 (예: Instagram, Facebook, 블로그)",
        max_length=50
    )

    # 추가 요청사항
    additional_requirements: Optional[str] = Field(
        None,
        description="추가 요청사항",
        max_length=500
    )

    # 생성 개수
    num_variations: int = Field(
        default=3,
        description="생성할 문구 개수",
        ge=1,
        le=10
    )

    class Config:
        json_schema_extra = {
            "example": {
                "product_name": "수제 초콜릿 케이크",
                "product_description": "벨기에산 다크 초콜릿을 사용한 진한 초콜릿 케이크",
                "tone": "emotional",
                "length": "short",
                "target_audience": "20-30대 여성",
                "key_message": "특별한 날을 더 특별하게",
                "platform": "Instagram",
                "num_variations": 3
            }
        }


class AdCopyVariation(BaseModel):
    """생성된 광고 문구 하나"""
    text: str = Field(..., description="생성된 광고 문구")
    headline: Optional[str] = Field(None, description="헤드라인")
    hashtags: Optional[List[str]] = Field(None, description="추천 해시태그")


class AdCopyResponse(BaseModel):
    """광고 문구 생성 응답"""
    success: bool = True
    generation_id: str = Field(..., description="생성 ID")
    variations: List[AdCopyVariation] = Field(..., description="생성된 문구들")
    model_used: str = Field(..., description="사용된 모델")
    generation_time: float = Field(..., description="생성 소요 시간 (초)")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "generation_id": "123e4567-e89b-12d3-a456-426614174000",
                "variations": [
                    {
                        "text": "특별한 순간을 더욱 달콤하게 만들어줄 수제 초콜릿 케이크. 벨기에산 프리미엄 다크 초콜릿의 진한 풍미를 경험해보세요.",
                        "headline": "달콤한 순간의 완성",
                        "hashtags": ["#수제케이크", "#초콜릿케이크", "#특별한날"]
                    }
                ],
                "model_used": "gpt-4",
                "generation_time": 2.5
            }
        }
