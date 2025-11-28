"""
메뉴판 OCR 및 Repaint 스키마
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MenuOCRRequest(BaseModel):
    """메뉴판 OCR 요청"""
    crop_mode: bool = Field(default=True, description="이미지 크롭 모드")
    save_results: bool = Field(default=True, description="결과 저장 여부")

    class Config:
        json_schema_extra = {
            "example": {
                "crop_mode": True,
                "save_results": True
            }
        }


class BoundingBox(BaseModel):
    """바운딩 박스 정보"""
    x: float
    y: float
    width: float
    height: float
    text: str


class MenuOCRResponse(BaseModel):
    """메뉴판 OCR 응답"""
    success: bool = True
    ocr_id: str = Field(..., description="OCR 결과 ID")
    schema_content: str = Field(..., description="추출된 스키마 (mmd 형식)")
    result_image_url: str = Field(..., description="바운딩 박스가 그려진 결과 이미지 URL")
    extracted_images: List[str] = Field(default=[], description="추출된 이미지 URL 목록")
    bounding_boxes: List[BoundingBox] = Field(default=[], description="바운딩 박스 정보")
    processing_time: float = Field(..., description="처리 시간 (초)")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "ocr_id": "ocr_123",
                "schema_content": "# 메뉴\n## 커피\n- 아메리카노: 4500원\n",
                "result_image_url": "/static/ocr/result_with_boxes.jpg",
                "extracted_images": ["/static/ocr/images/0.jpg"],
                "bounding_boxes": [],
                "processing_time": 5.2,
                "created_at": "2025-11-20T10:00:00"
            }
        }


class MenuRepaintRequest(BaseModel):
    """메뉴판 Repaint 요청"""
    ocr_id: str = Field(..., description="OCR 결과 ID")
    schema_content: Optional[str] = Field(None, description="수정된 스키마 내용 (없으면 원본 사용)")

    class Config:
        json_schema_extra = {
            "example": {
                "ocr_id": "ocr_123",
                "schema_content": "# 메뉴\n## 커피\n- 아메리카노: 4500원\n"
            }
        }


class MenuRepaintResponse(BaseModel):
    """메뉴판 Repaint 응답"""
    success: bool = True
    repaint_id: str = Field(..., description="Repaint 결과 ID")
    result_image_url: str = Field(..., description="재생성된 메뉴판 이미지 URL")
    processing_time: float = Field(..., description="처리 시간 (초)")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "repaint_id": "repaint_123",
                "result_image_url": "/static/repaint/result_repaint.jpg",
                "processing_time": 3.1,
                "created_at": "2025-11-20T10:05:00"
            }
        }
