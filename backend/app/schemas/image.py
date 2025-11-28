"""
이미지 생성 스키마
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum


class ImageStyle(str, Enum):
    """이미지 스타일"""
    REALISTIC = "realistic"  # 사실적
    ARTISTIC = "artistic"  # 예술적
    MINIMALIST = "minimalist"  # 미니멀
    VINTAGE = "vintage"  # 빈티지
    MODERN = "modern"  # 모던
    COLORFUL = "colorful"  # 화려한


class AspectRatio(str, Enum):
    """이미지 비율"""
    SQUARE = "1:1"  # 정사각형 (Instagram)
    PORTRAIT = "4:5"  # 세로 (Instagram Story)
    LANDSCAPE = "16:9"  # 가로 (YouTube)
    WIDE = "21:9"  # 와이드 (배너)


class TextToImageRequest(BaseModel):
    """텍스트→이미지 생성 요청"""

    # 필수 입력
    prompt: str = Field(..., description="이미지 생성 프롬프트", min_length=1, max_length=2000)

    # 스타일
    style: Optional[ImageStyle] = Field(default=ImageStyle.REALISTIC, description="이미지 스타일")
    template_id: Optional[str] = Field(None, description="템플릿 ID")

    # 이미지 설정
    aspect_ratio: AspectRatio = Field(default=AspectRatio.SQUARE, description="이미지 비율")
    width: Optional[int] = Field(None, description="이미지 너비", ge=512, le=2048)
    height: Optional[int] = Field(None, description="이미지 높이", ge=512, le=2048)

    # 생성 파라미터
    num_inference_steps: int = Field(
        default=50,
        description="추론 스텝 수 (높을수록 품질↑, 시간↑)",
        ge=20,
        le=100
    )
    guidance_scale: float = Field(
        default=7.5,
        description="가이던스 스케일 (높을수록 프롬프트에 충실)",
        ge=1.0,
        le=20.0
    )
    negative_prompt: Optional[str] = Field(
        default="low quality, blurry, distorted",
        description="네거티브 프롬프트",
        max_length=1000
    )

    # 생성 개수
    num_images: int = Field(default=1, description="생성할 이미지 수", ge=1, le=4)

    # 시드 (재현성)
    seed: Optional[int] = Field(None, description="랜덤 시드")

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "A delicious chocolate cake on a wooden table, professional food photography, natural lighting",
                "style": "realistic",
                "aspect_ratio": "1:1",
                "num_inference_steps": 50,
                "guidance_scale": 7.5,
                "num_images": 2
            }
        }


class ImageToImageRequest(BaseModel):
    """이미지→이미지 변환 요청"""

    # 필수 입력
    image_url: str = Field(..., description="입력 이미지 URL")
    prompt: str = Field(..., description="변환 프롬프트", min_length=1, max_length=2000)

    # 제어 방식
    use_controlnet: bool = Field(default=False, description="ControlNet 사용 여부")
    controlnet_type: Optional[str] = Field(
        default="canny",
        description="ControlNet 타입 (canny, depth, pose, etc.)"
    )

    # 변환 강도
    strength: float = Field(
        default=0.75,
        description="변환 강도 (0.0=원본 유지, 1.0=완전 변환)",
        ge=0.0,
        le=1.0
    )

    # 스타일
    style: Optional[ImageStyle] = Field(default=ImageStyle.REALISTIC, description="이미지 스타일")
    template_id: Optional[str] = Field(None, description="템플릿 ID")

    # 생성 파라미터
    num_inference_steps: int = Field(default=50, ge=20, le=100)
    guidance_scale: float = Field(default=7.5, ge=1.0, le=20.0)
    negative_prompt: Optional[str] = Field(
        default="low quality, blurry, distorted",
        max_length=1000
    )

    # 생성 개수
    num_images: int = Field(default=1, ge=1, le=4)
    seed: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "image_url": "https://example.com/product.jpg",
                "prompt": "Professional product photography with elegant background",
                "use_controlnet": True,
                "controlnet_type": "canny",
                "strength": 0.75,
                "style": "realistic"
            }
        }


class BackgroundRemovalRequest(BaseModel):
    """배경 제거 요청"""
    image_url: str = Field(..., description="입력 이미지 URL")
    return_mask: bool = Field(default=False, description="마스크도 함께 반환")


class BackgroundReplaceRequest(BaseModel):
    """배경 교체 요청"""
    image_url: str = Field(..., description="원본 이미지 URL")
    background_prompt: str = Field(..., description="새 배경 설명", max_length=1000)
    preserve_lighting: bool = Field(default=True, description="조명 보존 여부")
    num_images: int = Field(default=1, ge=1, le=4)


class ImageGenerationResponse(BaseModel):
    """이미지 생성 응답"""
    success: bool = True
    generation_id: str = Field(..., description="생성 ID")
    images: List[str] = Field(..., description="생성된 이미지 URL 목록")
    model_used: str = Field(..., description="사용된 모델")
    parameters: dict = Field(..., description="사용된 파라미터")
    generation_time: float = Field(..., description="생성 소요 시간 (초)")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "generation_id": "123e4567-e89b-12d3-a456-426614174000",
                "images": [
                    "https://storage.example.com/generations/image1.png",
                    "https://storage.example.com/generations/image2.png"
                ],
                "model_used": "stable-diffusion-xl-base-1.0",
                "parameters": {
                    "num_inference_steps": 50,
                    "guidance_scale": 7.5
                },
                "generation_time": 15.3
            }
        }
