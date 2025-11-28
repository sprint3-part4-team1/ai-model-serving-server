"""
메뉴판 관련 모델
온라인 메뉴판 시스템용 DB 모델
"""
from sqlalchemy import Column, Integer, String, Text, DECIMAL, Boolean, DateTime, ForeignKey, Time
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Store(Base):
    """매장 테이블"""
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    address = Column(String(255))
    phone = Column(String(20))
    open_time = Column(Time)
    close_time = Column(Time)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    menus = relationship("Menu", back_populates="store", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Store(id={self.id}, name={self.name})>"


class Menu(Base):
    """메뉴판 테이블"""
    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    store = relationship("Store", back_populates="menus")
    menu_items = relationship("MenuItem", back_populates="menu", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Menu(id={self.id}, name={self.name}, store_id={self.store_id})>"


class MenuItem(Base):
    """메뉴 아이템 테이블"""
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    menu_id = Column(Integer, ForeignKey("menus.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2))
    is_available = Column(Boolean, default=True)
    image_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    menu = relationship("Menu", back_populates="menu_items")
    ingredients = relationship("ItemIngredient", back_populates="menu_item", cascade="all, delete-orphan")
    nutrition_estimate = relationship("NutritionEstimate", back_populates="menu_item", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<MenuItem(id={self.id}, name={self.name}, price={self.price})>"


class ItemIngredient(Base):
    """메뉴 재료 테이블"""
    __tablename__ = "item_ingredients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("menu_items.id", ondelete="CASCADE"), nullable=False)
    ingredient_name = Column(String(100), nullable=False)
    quantity_unit = Column(String(50))
    quantity_value = Column(DECIMAL(10, 2))
    notes = Column(Text)

    # 관계
    menu_item = relationship("MenuItem", back_populates="ingredients")

    def __repr__(self):
        return f"<ItemIngredient(id={self.id}, name={self.ingredient_name})>"


class NutritionEstimate(Base):
    """영양 성분 추정치 테이블"""
    __tablename__ = "nutrition_estimates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("menu_items.id", ondelete="CASCADE"), nullable=False, unique=True)
    calories = Column(DECIMAL(10, 2))
    sugar_g = Column(DECIMAL(10, 2))
    caffeine_mg = Column(DECIMAL(10, 2))
    protein_g = Column(DECIMAL(10, 2))
    fat_g = Column(DECIMAL(10, 2))
    carbs_g = Column(DECIMAL(10, 2))
    confidence = Column(DECIMAL(5, 4))  # 0~1 값
    last_computed_at = Column(DateTime)

    # 관계
    menu_item = relationship("MenuItem", back_populates="nutrition_estimate")

    def __repr__(self):
        return f"<NutritionEstimate(id={self.id}, item_id={self.item_id}, calories={self.calories})>"
