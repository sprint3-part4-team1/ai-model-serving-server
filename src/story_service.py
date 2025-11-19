import os
import json
import logging
from datetime import datetime, timedelta
from database import get_session
from models import MenuItem, NutritionEstimate, Story

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def generate_story_for_item(item_id: int, max_retries: int = 5):
    """
    특정 메뉴 아이템의 재료와 영양 성분 정보를 기반으로
    사실적이고 감성적인 스토리를 생성하여 반환합니다.
    DB에 캐싱하여 24시간 이내에는 기존 스토리를 반환합니다.
    """
    session = get_session()
    try:
        menu_item = session.query(MenuItem).filter(MenuItem.id == item_id).first()
        nutrition = session.query(NutritionEstimate).filter(NutritionEstimate.item_id == item_id).first()
        existing_story = session.query(Story).filter(Story.item_id == item_id).first()

        if not menu_item or not nutrition:
            logging.warning(f"MenuItem {item_id} or NutritionEstimate not found")
            return None

        # 24시간 이내라면 기존 스토리 반환
        if existing_story and existing_story.last_computed_at > datetime.now() - timedelta(hours=24):
            logging.info(f"Returning cached story for item {item_id}")
            return {"content": existing_story.content, "confidence": float(existing_story.confidence)}

        # 재료와 영양 정보 텍스트 준비
        ingredients_text = ", ".join([
            f"{ing.ingredient_name} {ing.quantity_value}{ing.quantity_unit}"
            for ing in menu_item.ingredients
        ])
        nutrition_text = (
            f"칼로리 {nutrition.calories}kcal, "
            f"단백질 {nutrition.protein_g}g, "
            f"지방 {nutrition.fat_g}g, "
            f"탄수화물 {nutrition.carbs_g}g, "
            f"당분 {nutrition.sugar_g}g, "
            f"카페인 {nutrition.caffeine_mg}mg"
        )

        prompt = ChatPromptTemplate.from_template("""
        당신은 음식 스토리텔러입니다.
        메뉴 이름: {menu_name}
        설명: {description}
        재료: {ingredients}
        영양 정보: {nutrition}

        위 정보를 기반으로 사실적이면서 감성적인 스토리를 작성해 주세요.
        고객은 단순 정보가 아니라 '이야기와 감성'을 소비합니다.
        영양 정보는 직접 나열하지 말고, 이를 바탕으로 요리가 주는 느낌이나 가치에 대해 서술하세요.
        결과는 JSON 형식으로 반환하세요. 예:
        {{
          "content": "까르보나라는 로마 노동자들의 간단한 식사에서 시작되어...",
          "confidence": 0.9
        }}
        """)

        llm = ChatOpenAI(
            model="gpt-5-nano",
            temperature=0.4,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        chain = prompt | llm | StrOutputParser()

        attempt = 0
        story_data = None
        confidence = 0.0

        while attempt < max_retries:
            attempt += 1
            result = chain.invoke({
                "menu_name": menu_item.name,
                "description": menu_item.description,
                "ingredients": ingredients_text,
                "nutrition": nutrition_text
            })
            try:
                story_data = json.loads(result)
                confidence = story_data.get("confidence", 0)
            except Exception as e:
                logging.error(f"❌ JSON parsing error on attempt {attempt}: {e}")
                continue

            if confidence >= 0.8:
                break
            else:
                logging.warning(f"Attempt {attempt}: Low confidence ({confidence}) for story of item {item_id}")
                logging.info(f"Story data (low confidence): {story_data}")

        if not story_data:
            return None

        # DB에 저장/업데이트
        if existing_story:
            existing_story.content = story_data.get("content")
            existing_story.confidence = confidence
            existing_story.last_computed_at = datetime.now()
        else:
            new_story = Story(
                item_id=item_id,
                content=story_data.get("content"),
                confidence=confidence,
                last_computed_at=datetime.now()
            )
            session.add(new_story)

        session.commit()
        logging.info(f"✅ Story saved/updated for item {item_id} with confidence {confidence}")
        return story_data

    finally:
        session.close()
