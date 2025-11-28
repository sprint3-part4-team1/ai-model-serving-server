"""
생성 기록 모델
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, Integer, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class GenerationType(str, enum.Enum):
    """생성 유형"""
    AD_COPY = "ad_copy"  # 광고 문구
    TEXT_TO_IMAGE = "text_to_image"  # 텍스트→이미지
    IMAGE_TO_IMAGE = "image_to_image"  # 이미지→이미지
    BACKGROUND_REMOVAL = "background_removal"  # 배경 제거
    BACKGROUND_REPLACE = "background_replace"  # 배경 교체
    STYLE_TRANSFER = "style_transfer"  # 스타일 변환


class GenerationStatus(str, enum.Enum):
    """생성 상태"""
    PENDING = "pending"  # 대기중
    PROCESSING = "processing"  # 처리중
    COMPLETED = "completed"  # 완료
    FAILED = "failed"  # 실패


class Generation(Base):
    """생성 기록 테이블"""
    __tablename__ = "generations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    type = Column(Enum(GenerationType), nullable=False, index=True)
    status = Column(Enum(GenerationStatus), default=GenerationStatus.PENDING, index=True)

    # 입력 데이터
    input_text = Column(Text)  # 텍스트 입력
    input_image_url = Column(String(500))  # 입력 이미지 URL
    reference_image_url = Column(String(500))  # 참조 이미지 URL

    # 출력 데이터
    output_text = Column(Text)  # 생성된 텍스트
    output_image_url = Column(String(500))  # 생성된 이미지 URL

    # 메타데이터
    model_used = Column(String(200))  # 사용된 모델
    parameters = Column(JSON)  # 생성 파라미터 (JSON)
    template_id = Column(String(36), ForeignKey("templates.id"), nullable=True)

    # 성능 메트릭
    generation_time = Column(Float)  # 생성 소요 시간 (초)
    error_message = Column(Text)  # 에러 메시지

    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime)

    # 관계
    project = relationship("Project", back_populates="generations")
    template = relationship("Template")

    def __repr__(self):
        return f"<Generation(id={self.id}, type={self.type}, status={self.status})>"
