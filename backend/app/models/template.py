"""
템플릿 모델
"""
from sqlalchemy import Column, String, Text, DateTime, Boolean, JSON
from datetime import datetime
import uuid

from app.core.database import Base


class Template(Base):
    """스타일 템플릿 테이블"""
    __tablename__ = "templates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False, unique=True)
    description = Column(Text)
    category = Column(String(100))  # 카테고리 (예: 음식, 패션, 뷰티 등)

    # 스타일 정보
    style_prompt = Column(Text)  # 스타일 프롬프트
    negative_prompt = Column(Text)  # 네거티브 프롬프트
    lora_model_path = Column(String(500))  # LoRA 모델 경로
    lora_weight = Column(String(10), default="0.8")  # LoRA 가중치

    # 생성 파라미터
    parameters = Column(JSON)  # 추가 파라미터 (JSON)

    # 프리뷰
    preview_image_url = Column(String(500))  # 프리뷰 이미지 URL
    thumbnail_url = Column(String(500))  # 썸네일 URL

    # 상태
    is_active = Column(Boolean, default=True)  # 활성화 상태
    is_premium = Column(Boolean, default=False)  # 프리미엄 템플릿 여부

    # 통계
    usage_count = Column(String(10), default="0")  # 사용 횟수

    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Template(id={self.id}, name={self.name}, category={self.category})>"
