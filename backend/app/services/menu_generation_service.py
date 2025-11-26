"""
Menu Generation Service
메뉴 카테고리와 아이템을 AI로 생성하는 서비스
"""

from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Tuple
import time
import asyncio
import os
from pathlib import Path
from openai import OpenAI
import json

from app.core.config import settings
from app.core.logging import app_logger as logger
from app.models.menu import Menu, MenuItem, ItemIngredient
from app.schemas.menu_generation import (
    MenuGenerationRequest,
    MenuCategoryCreate,
    MenuItemCreate,
    GeneratedMenuCategory,
    GeneratedMenuItem
)


class MenuGenerationService:
    """메뉴 생성 서비스"""

    def __init__(self):
        """서비스 초기화"""
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        logger.info("Menu Generation Service 초기화 완료")

    async def generate_menu(
        self,
        db: Session,
        request: MenuGenerationRequest
    ) -> Tuple[List[GeneratedMenuCategory], float]:
        """
        메뉴판 생성 (카테고리 + 아이템)

        Args:
            db: 데이터베이스 세션
            request: 메뉴 생성 요청

        Returns:
            (생성된 카테고리 리스트, 생성 시간)
        """
        start_time = time.time()
        logger.info(f"메뉴판 생성 시작 - Store ID: {request.store_id}, 카테고리 수: {len(request.categories)}")

        try:
            generated_categories = []

            for category_req in request.categories:
                # 카테고리 생성
                menu_category = await self._create_category(
                    db=db,
                    store_id=request.store_id,
                    category_req=category_req
                )

                # 메뉴 아이템 생성
                generated_items = await self._create_menu_items(
                    db=db,
                    menu_id=menu_category.id,
                    items_req=category_req.items,
                    auto_generate_images=request.auto_generate_images,
                    auto_generate_descriptions=request.auto_generate_descriptions,
                    image_style=request.image_style
                )

                # 결과 객체 생성
                generated_category = GeneratedMenuCategory(
                    id=menu_category.id,
                    name=menu_category.name,
                    description=menu_category.description,
                    items=generated_items
                )
                generated_categories.append(generated_category)

            # 변경사항 커밋
            db.commit()

            generation_time = time.time() - start_time
            logger.info(f"메뉴판 생성 완료 - {len(generated_categories)}개 카테고리, {generation_time:.2f}초")

            return generated_categories, generation_time

        except Exception as e:
            db.rollback()
            logger.error(f"메뉴판 생성 실패: {e}")
            raise

    async def _create_category(
        self,
        db: Session,
        store_id: int,
        category_req: MenuCategoryCreate
    ) -> Menu:
        """메뉴 카테고리 생성"""
        logger.info(f"카테고리 생성: {category_req.category_name}")

        menu = Menu(
            store_id=store_id,
            name=category_req.category_name,
            description=category_req.category_description
        )
        db.add(menu)
        db.flush()  # ID 생성을 위해 flush

        logger.info(f"카테고리 생성 완료: ID={menu.id}, Name={menu.name}")
        return menu

    async def _create_menu_items(
        self,
        db: Session,
        menu_id: int,
        items_req: List[MenuItemCreate],
        auto_generate_images: bool,
        auto_generate_descriptions: bool,
        image_style: Optional[str]
    ) -> List[GeneratedMenuItem]:
        """메뉴 아이템 리스트 생성"""
        logger.info(f"메뉴 아이템 생성 시작 - {len(items_req)}개")

        generated_items = []

        for item_req in items_req:
            generated_item = await self._create_menu_item(
                db=db,
                menu_id=menu_id,
                item_req=item_req,
                auto_generate_image=auto_generate_images and not item_req.image_url,
                auto_generate_description=auto_generate_descriptions and not item_req.description,
                image_style=image_style
            )
            generated_items.append(generated_item)

        logger.info(f"메뉴 아이템 생성 완료 - {len(generated_items)}개")
        return generated_items

    async def _create_menu_item(
        self,
        db: Session,
        menu_id: int,
        item_req: MenuItemCreate,
        auto_generate_image: bool,
        auto_generate_description: bool,
        image_style: Optional[str]
    ) -> GeneratedMenuItem:
        """개별 메뉴 아이템 생성"""
        logger.info(f"메뉴 아이템 생성: {item_req.name}")

        is_ai_generated_image = False
        is_ai_generated_description = False
        image_url = item_req.image_url
        description = item_req.description

        # AI로 설명 생성
        if auto_generate_description:
            description = await self._generate_description(
                menu_name=item_req.name,
                ingredients=item_req.ingredients
            )
            is_ai_generated_description = True
            logger.info(f"AI 설명 생성 완료: {description[:50]}...")

        # AI로 이미지 생성 (현재는 placeholder, 추후 Stable Diffusion 연동)
        if auto_generate_image:
            image_url = await self._generate_image(
                menu_name=item_req.name,
                description=description,
                image_style=image_style
            )
            is_ai_generated_image = True
            logger.info(f"AI 이미지 생성 완료: {image_url}")

        # 메뉴 아이템 DB 저장
        menu_item = MenuItem(
            menu_id=menu_id,
            name=item_req.name,
            description=description,
            price=item_req.price,
            image_url=image_url,
            is_available=True
        )
        db.add(menu_item)
        db.flush()  # ID 생성을 위해 flush

        # 재료 정보 저장
        if item_req.ingredients:
            for ingredient_name in item_req.ingredients:
                ingredient = ItemIngredient(
                    item_id=menu_item.id,
                    ingredient_name=ingredient_name
                )
                db.add(ingredient)

        # 결과 객체 생성
        generated_item = GeneratedMenuItem(
            id=menu_item.id,
            name=menu_item.name,
            description=menu_item.description,
            price=menu_item.price,
            image_url=menu_item.image_url,
            is_ai_generated_image=is_ai_generated_image,
            is_ai_generated_description=is_ai_generated_description
        )

        logger.info(f"메뉴 아이템 DB 저장 완료: ID={menu_item.id}")
        return generated_item

    async def _generate_description(
        self,
        menu_name: str,
        ingredients: Optional[List[str]] = None
    ) -> str:
        """
        OpenAI로 메뉴 설명 생성

        Args:
            menu_name: 메뉴 이름
            ingredients: 재료 리스트 (선택)

        Returns:
            생성된 설명
        """
        logger.info(f"메뉴 설명 생성 시작: {menu_name}")

        try:
            # 프롬프트 구성
            prompt = f"""메뉴 이름: {menu_name}"""
            if ingredients:
                prompt += f"\n재료: {', '.join(ingredients)}"

            prompt += """

위 메뉴에 대한 매력적인 설명을 2-3문장으로 작성해주세요.
설명은 다음 조건을 만족해야 합니다:
1. 고객의 식욕을 자극하는 표현 사용
2. 메뉴의 특징과 맛을 구체적으로 설명
3. 너무 길지 않고 간결하게 (2-3문장)
4. 자연스럽고 친근한 톤

JSON 형식으로 응답하세요:
{
  "description": "메뉴 설명"
}
"""

            # OpenAI API 호출
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 레스토랑 메뉴 설명을 작성하는 전문가입니다. 항상 JSON 형식으로만 응답합니다."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=200,
                response_format={"type": "json_object"}
            )

            # 응답 파싱
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            description = result.get("description", "")

            logger.info(f"메뉴 설명 생성 완료: {description[:50]}...")
            return description

        except Exception as e:
            logger.error(f"메뉴 설명 생성 실패: {e}")
            # Fallback: 기본 설명 반환
            return f"{menu_name} - 신선한 재료로 만든 정성스러운 요리"

    async def _generate_image(
        self,
        menu_name: str,
        description: Optional[str],
        image_style: Optional[str]
    ) -> Optional[str]:
        """
        이미지 생성 (현재는 placeholder, 추후 Stable Diffusion 연동)

        Args:
            menu_name: 메뉴 이름
            description: 메뉴 설명
            image_style: 이미지 스타일

        Returns:
            이미지 URL (현재는 None)
        """
        logger.info(f"이미지 생성 요청: {menu_name}")

        # TODO: Stable Diffusion 서비스 연동
        # 현재는 이미지 생성을 스킵하고 None 반환
        # 추후 sd_service.py를 활용하여 이미지 생성 구현

        # 예시 코드 (추후 구현):
        # from app.services.sd_service import sd_service
        # prompt = f"{menu_name}, {description}, {image_style}"
        # image_data = await sd_service.generate_image(prompt)
        # image_path = self._save_image(image_data, menu_name)
        # return f"/static/uploads/{image_path}"

        logger.info("이미지 생성 스킵 (추후 구현 예정)")
        return None

    def _save_image(self, image_data: bytes, menu_name: str) -> str:
        """
        이미지 파일 저장

        Args:
            image_data: 이미지 바이너리 데이터
            menu_name: 메뉴 이름

        Returns:
            저장된 파일명
        """
        # 파일명 생성 (특수문자 제거)
        safe_name = "".join(c for c in menu_name if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = f"menu_{safe_name}_{int(time.time())}.jpg"

        # 저장 경로
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / filename

        # 파일 저장
        with open(file_path, 'wb') as f:
            f.write(image_data)

        logger.info(f"이미지 저장 완료: {filename}")
        return filename


# 싱글톤 인스턴스
menu_generation_service = MenuGenerationService()
