"""
사용자 모델
"""
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class BusinessType(str, enum.Enum):
    """사업 유형"""
    CAFE = "cafe"  # 카페
    RESTAURANT = "restaurant"  # 음식점
    RETAIL = "retail"  # 소매업
    BEAUTY = "beauty"  # 미용실
    ONLINE = "online"  # 온라인쇼핑몰
    OTHER = "other"  # 기타


class User(Base):
    """사용자 테이블"""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    business_name = Column(String(200))
    business_type = Column(Enum(BusinessType), default=BusinessType.OTHER)
    phone = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"
