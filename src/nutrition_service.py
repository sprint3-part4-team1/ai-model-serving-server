# nutrition_service.py
import os
import json
import logging
from datetime import datetime
from database import get_session
from models import MenuItem, NutritionEstimate

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def compute_nutrition_for_item(item_id: int, max_retries: int = 5):
    session = get_session()
    try:
        menu_item = session.query(MenuItem).filter(MenuItem.id == item_id).first()
        if not menu_item:
            logging.warning(f"MenuItem {item_id} not found")
            return

        existing_estimate = session.query(NutritionEstimate).filter(NutritionEstimate.item_id == item_id).first()
        if existing_estimate:
            logging.info(f"Nutrition estimate already exists for item {item_id}, skipping.")
            return

        ingredients_text = ", ".join([
            f"{ing.ingredient_name} {ing.quantity_value}{ing.quantity_unit}"
            for ing in menu_item.ingredients
        ])

        prompt = ChatPromptTemplate.from_template("""
        다음 재료 목록을 기반으로 칼로리, 당분(g), 카페인(mg), 단백질(g), 지방(g), 탄수화물(g)을 추정해 주세요.
        재료: {ingredients}
        결과는 JSON 형식으로 반환하세요. 예:
        {{
          "calories": 500,
          "sugar_g": 5,
          "caffeine_mg": 0,
          "protein_g": 20,
          "fat_g": 15,
          "carbs_g": 60,
          "confidence": 0.85
        }}
        """)

        llm = ChatOpenAI(
            model="gpt-5-nano",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )

        chain = prompt | llm | StrOutputParser()

        attempt = 0
        nutrition_data = None
        confidence = 0.0

        while attempt < max_retries:
            attempt += 1
            result = chain.invoke({"ingredients": ingredients_text})
            try:
                nutrition_data = json.loads(result)
                confidence = nutrition_data.get("confidence", 0)
            except Exception as e:
                logging.error(f"❌ JSON parsing error on attempt {attempt}: {e}")
                continue

            if confidence >= 0.7:
                break
            else:
                logging.warning(f"Attempt {attempt}: Low confidence ({confidence}) for item {item_id}")
                logging.info(f"Nutrition data (low confidence): {nutrition_data}")

        # 최종 confidence 체크
        if confidence < 0.7:
            logging.error(f"❌ Failed to get high confidence after {max_retries} attempts for item {item_id}. Last data: {nutrition_data}")
            return

        # DB 저장
        estimate = NutritionEstimate(
            item_id=item_id,
            calories=nutrition_data.get("calories"),
            sugar_g=nutrition_data.get("sugar_g"),
            caffeine_mg=nutrition_data.get("caffeine_mg"),
            protein_g=nutrition_data.get("protein_g"),
            fat_g=nutrition_data.get("fat_g"),
            carbs_g=nutrition_data.get("carbs_g"),
            confidence=confidence,
            last_computed_at=datetime.now()
        )

        session.add(estimate)
        session.commit()
        logging.info(f"✅ Nutrition estimates saved for item {item_id} with confidence {confidence}")

    except Exception as e:
        session.rollback()
        logging.error(f"❌ Error: {e}")
    finally:
        session.close()
