"""
Seasonal Story 모델
시즈널 스토리 DB 모델
"""
from sqlalchemy import Column, Integer, String, Text, DECIMAL, DateTime, JSON
from datetime import datetime
from app.core.database import Base


class SeasonalStory(Base):
    """시즈널 스토리 테이블"""
    __tablename__ = "seasonal_stories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, nullable=False, index=True)
    store_name = Column(String(100), nullable=True)
    featured_menu_name = Column(String(100), nullable=True)  # 광고 문구에 사용된 메뉴
    story_content = Column(Text, nullable=False)
    weather_condition = Column(String(50), nullable=True)
    temperature = Column(DECIMAL(5, 2), nullable=True)
    season = Column(String(20), nullable=True)
    time_period = Column(String(20), nullable=True)
    is_special_day = Column(Integer, default=0)  # 0: 평일, 1: 특별한 날
    is_weekend = Column(Integer, default=0)  # 0: 평일, 1: 주말
    trend_keywords = Column(JSON, nullable=True)  # 간단한 키워드만
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<SeasonalStory(id={self.id}, store_name={self.store_name}, created_at={self.created_at})>"

    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            "id": self.id,
            "store_id": self.store_id,
            "store_name": self.store_name,
            "featured_menu_name": self.featured_menu_name,
            "story_content": self.story_content,
            "weather_condition": self.weather_condition,
            "temperature": float(self.temperature) if self.temperature else None,
            "season": self.season,
            "time_period": self.time_period,
            "is_special_day": bool(self.is_special_day),
            "is_weekend": bool(self.is_weekend),
            "trend_keywords": self.trend_keywords,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
