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
    store_id = Column(Integer, nullable=True, index=True)
    store_name = Column(String(100), nullable=True)
    store_type = Column(String(50), nullable=True)
    story_content = Column(Text, nullable=False)
    weather_condition = Column(String(50), nullable=True)
    temperature = Column(DECIMAL(5, 2), nullable=True)
    season = Column(String(20), nullable=True)
    time_period = Column(String(20), nullable=True)
    google_trends = Column(JSON, nullable=True)
    instagram_trends = Column(JSON, nullable=True)
    selected_trends = Column(JSON, nullable=True)
    menu_items = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<SeasonalStory(id={self.id}, store_name={self.store_name}, created_at={self.created_at})>"

    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            "id": self.id,
            "store_id": self.store_id,
            "store_name": self.store_name,
            "store_type": self.store_type,
            "story_content": self.story_content,
            "weather_condition": self.weather_condition,
            "temperature": float(self.temperature) if self.temperature else None,
            "season": self.season,
            "time_period": self.time_period,
            "google_trends": self.google_trends,
            "instagram_trends": self.instagram_trends,
            "selected_trends": self.selected_trends,
            "menu_items": self.menu_items,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
