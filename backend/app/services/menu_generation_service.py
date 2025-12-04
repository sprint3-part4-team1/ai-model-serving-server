"""
Menu Generation Service
메뉴 카테고리와 아이템을 AI로 생성하는 서비스
"""

from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Tuple
import time
import asyncio
import os
import sys
from pathlib import Path
from openai import OpenAI
import json
from PIL import Image
import io

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
from app.services.sd_service import sd_service
from app.schemas.image import TextToImageRequest, ImageStyle, AspectRatio

# Add backend/src to Python path for nutrition module
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from src.nutrition.nutrition_analyzer import NutritionAnalyzer


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
            # ✅ 1. 해당 매장의 기존 메뉴 아이템 전체 조회 (이미지/설명 재사용을 위해)
            existing_items = db.query(MenuItem).join(Menu).filter(
                Menu.store_id == request.store_id
            ).all()

            # 메뉴 이름으로 빠르게 찾기 위한 딕셔너리 (이미지/설명 재사용용)
            existing_items_dict = {
                item.name: {
                    'image_url': item.image_url,
                    'description': item.description,
                    'is_ai_generated_image': item.is_ai_generated_image,
                    'is_ai_generated_description': item.is_ai_generated_description
                }
                for item in existing_items
            }
            logger.info(f"기존 메뉴 아이템 {len(existing_items_dict)}개 데이터 백업 완료")

            # ✅ 2. 기존 메뉴 카테고리 및 아이템 삭제 (중복 방지)
            existing_menus = db.query(Menu).filter(Menu.store_id == request.store_id).all()
            if existing_menus:
                logger.info(f"기존 카테고리 {len(existing_menus)}개 삭제 중...")
                for menu in existing_menus:
                    # 카테고리에 속한 메뉴 아이템과 재료 삭제
                    db.query(MenuItem).filter(MenuItem.menu_id == menu.id).delete()
                # 카테고리 삭제
                db.query(Menu).filter(Menu.store_id == request.store_id).delete()
                db.flush()
                logger.info("기존 메뉴 데이터 삭제 완료")

            generated_categories = []

            for category_req in request.categories:
                # 카테고리 생성
                menu_category = await self._create_category(
                    db=db,
                    store_id=request.store_id,
                    category_req=category_req
                )

                # 메뉴 아이템 생성 (기존 아이템 재사용)
                generated_items = await self._create_menu_items(
                    db=db,
                    menu_id=menu_category.id,
                    store_id=request.store_id,
                    items_req=category_req.items,
                    auto_generate_images=request.auto_generate_images,
                    auto_generate_descriptions=request.auto_generate_descriptions,
                    image_style=request.image_style,
                    existing_items_dict=existing_items_dict
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

            # 🆕 영양소 분석 자동 실행
            try:
                logger.info(f"🔬 영양소 분석 시작 - Store ID: {request.store_id}")
                analyzer = NutritionAnalyzer(batch_size=10)
                analyzer.analyze_store(request.store_id)
                logger.info(f"✅ 영양소 분석 완료")
            except Exception as e:
                logger.error(f"⚠️ 영양소 분석 실패 (메뉴 생성은 완료됨): {e}")
                # 영양소 분석 실패해도 메뉴 생성은 성공으로 처리

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
        store_id: int,
        items_req: List[MenuItemCreate],
        auto_generate_images: bool,
        auto_generate_descriptions: bool,
        image_style: Optional[str],
        existing_items_dict: Dict[str, Dict]
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
                image_style=image_style,
                existing_items_dict=existing_items_dict
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
        image_style: Optional[str],
        existing_items_dict: Dict[str, Dict]
    ) -> GeneratedMenuItem:
        """개별 메뉴 아이템 생성"""
        logger.info(f"메뉴 아이템 생성: {item_req.name}")

        is_ai_generated_image = False
        is_ai_generated_description = False
        image_url = item_req.image_url
        description = item_req.description
        price = item_req.price

        # ✅ 기존 메뉴 아이템이 있는지 확인
        existing_item = existing_items_dict.get(item_req.name)

        if existing_item:
            # 기존 데이터 재사용
            logger.info(f"✅ 기존 메뉴 재사용: {item_req.name}")

            # 기존 데이터에서 description, image_url 가져오기
            if not description and existing_item.get('description'):
                description = existing_item['description']
                is_ai_generated_description = existing_item.get('is_ai_generated_description', False)
                logger.info(f"  - 설명 재사용: {description[:50] if description else 'None'}...")

            if not image_url and existing_item.get('image_url'):
                image_url = existing_item['image_url']
                is_ai_generated_image = existing_item.get('is_ai_generated_image', False)
                logger.info(f"  - 이미지 재사용: {image_url}")
        else:
            # 신규 메뉴 아이템 - AI로 생성
            logger.info(f"🆕 신규 메뉴 생성: {item_req.name}")

            # AI로 설명 생성
            if auto_generate_description and not description:
                description = await self._generate_description(
                    menu_name=item_req.name,
                    ingredients=item_req.ingredients
                )
                is_ai_generated_description = True
                logger.info(f"  - AI 설명 생성 완료: {description[:50]}...")

            # AI로 이미지 생성
            if auto_generate_image and not image_url:
                image_url = await self._generate_image(
                    menu_name=item_req.name,
                    description=description,
                    image_style=image_style
                )
                is_ai_generated_image = True
                logger.info(f"  - AI 이미지 생성 완료: {image_url}")

        # 메뉴 아이템 DB 저장 (항상 새로운 레코드 생성)
        menu_item = MenuItem(
            menu_id=menu_id,
            name=item_req.name,
            description=description,
            price=price,
            image_url=image_url,
            is_available=True,
            is_ai_generated_image=is_ai_generated_image,
            is_ai_generated_description=is_ai_generated_description
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
        Stable Diffusion으로 메뉴 이미지 생성

        Args:
            menu_name: 메뉴 이름
            description: 메뉴 설명
            image_style: 이미지 스타일

        Returns:
            이미지 URL
        """
        logger.info(f"메뉴 이미지 생성 시작: {menu_name}")

        try:
            # 음식 사진 프롬프트 생성
            prompt = f"professional food photography of {menu_name}"

            if description:
                # 설명에서 핵심 키워드 추출 (간단히 처리)
                prompt += f", {description[:100]}"

            prompt += ", appetizing, well-plated, restaurant quality, high resolution"

            # 이미지 스타일 설정 (기본값: realistic)
            style = ImageStyle.REALISTIC
            if image_style:
                try:
                    style = ImageStyle(image_style.lower())
                except ValueError:
                    logger.warning(f"Unknown style '{image_style}', using 'realistic'")

            # Stable Diffusion 요청 생성
            sd_request = TextToImageRequest(
                prompt=prompt,
                style=style,
                aspect_ratio=AspectRatio.SQUARE,  # 1:1 정사각형 (메뉴판에 적합)
                num_inference_steps=30,  # 빠른 생성을 위해 30 steps
                guidance_scale=7.5,
                num_images=1
            )

            logger.info(f"SD 이미지 생성 중 - Prompt: {prompt[:100]}...")

            # Stable Diffusion으로 이미지 생성
            images, generation_time, parameters = await sd_service.generate_text_to_image(sd_request)

            if not images or len(images) == 0:
                logger.error("이미지 생성 실패: 빈 결과")
                return None

            # 첫 번째 이미지 저장
            image = images[0]
            filename = self._save_image(image, menu_name)

            # URL 생성 (Static 마운트 경로와 일치시킴)
            # filename은 "menu_images/xxx.jpg" 형식으로 반환됨
            image_url = f"/data/uploads/{filename}"

            logger.info(f"메뉴 이미지 생성 완료: {image_url} ({generation_time:.2f}초)")
            return image_url

        except Exception as e:
            logger.error(f"메뉴 이미지 생성 실패: {e}")
            # 이미지 생성 실패 시 None 반환 (메뉴 생성은 계속 진행)
            return None

    def _save_image(self, image: Image.Image, menu_name: str) -> str:
        """
        이미지 파일 저장

        Args:
            image: PIL Image 객체
            menu_name: 메뉴 이름

        Returns:
            저장된 파일 경로 (menu_images/xxx.jpg)
        """
        # 파일명 생성 (특수문자 제거)
        safe_name = "".join(c for c in menu_name if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = f"menu_{safe_name}_{int(time.time())}.jpg"

        # 저장 경로 (menu_images 폴더에 저장)
        upload_dir = Path(settings.UPLOAD_DIR) / "menu_images"
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / filename

        # PIL Image를 JPEG로 저장
        image.save(file_path, format='JPEG', quality=95, optimize=True)

        logger.info(f"이미지 저장 완료: menu_images/{filename}")
        return f"menu_images/{filename}"


# 싱글톤 인스턴스
menu_generation_service = MenuGenerationService()
