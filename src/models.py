# models.py
from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Store(Base):
    __tablename__ = "stores"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    address = Column(String)
    phone = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    
    menus = relationship("Menu", back_populates="store")

class Menu(Base):
    __tablename__ = "menus"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("stores.id"))
    name = Column(String)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    
    store = relationship("Store", back_populates="menus")
    menu_items = relationship("MenuItem", back_populates="menu")

class MenuItem(Base):
    __tablename__ = "menu_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    menu_id = Column(Integer, ForeignKey("menus.id"))
    name = Column(String)
    description = Column(String)
    price = Column(DECIMAL)
    is_available = Column(Boolean)
    image_url = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    
    menu = relationship("Menu", back_populates="menu_items")
    ingredients = relationship("ItemIngredient", back_populates="menu_item")
    nutrition = relationship("NutritionEstimate", back_populates="menu_item", uselist=False)

class ItemIngredient(Base):
    __tablename__ = "item_ingredients"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("menu_items.id"))
    ingredient_name = Column(String)
    quantity_unit = Column(String)
    quantity_value = Column(DECIMAL)
    notes = Column(String)
    
    menu_item = relationship("MenuItem", back_populates="ingredients")

class NutritionEstimate(Base):
    __tablename__ = "nutrition_estimates"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("menu_items.id"))
    calories = Column(DECIMAL)
    sugar_g = Column(DECIMAL)
    caffeine_mg = Column(DECIMAL)
    protein_g = Column(DECIMAL)
    fat_g = Column(DECIMAL)
    carbs_g = Column(DECIMAL)
    confidence = Column(DECIMAL)
    last_computed_at = Column(DateTime, default=datetime.now)
    
    menu_item = relationship("MenuItem", back_populates="nutrition")

class Story(Base):
    __tablename__ = "stories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("menu_items.id"), unique=True)
    content = Column(String)
    confidence = Column(DECIMAL)
    last_computed_at = Column(DateTime, default=datetime.now)

    menu_item = relationship("MenuItem", back_populates="story")