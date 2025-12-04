"""
Seasonal Story API Endpoints (New Structure)
완전히 새로운 구조로 재작성
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime
import pytz
from typing import List, Optional, Dict

from ...schemas.seasonal_story import (
    SeasonalStoryRequest,
    SeasonalStoryResponse,
    MenuStorytellingRequest,
    MenuStorytellingResponse,
    ErrorResponse
)
from ...services.context_collector import context_collector_service
from ...services.story_generator import story_generator_service
from app.models.seasonal_story import SeasonalStory
from app.models.menu import Menu, MenuItem
from app.core.database import get_db
from ...logger import app_logger as logger
from openai import OpenAI
from app.core.config import settings


router = APIRouter()


def check_special_day() -> tuple[bool, str]:
    """특별한 날 체크"""
    today = datetime.now()
    month, day = today.month, today.day

    special_days = {
        (1, 1): "신년",
        (2, 14): "발렌타인데이",
        (3, 14): "화이트데이",
        (11, 11): "빼빼로데이",
        (12, 25): "크리스마스"
    }

    if (month, day) in special_days:
        return True, special_days[(month, day)]

    # 크리스마스 시즌 (12월)
    if month == 12:
        return True, "크리스마스 시즌"

    return False, ""


def get_menu_with_nutrition(db: Session, store_id: int) -> List[Dict]:
    """매장의 메뉴 + 영양 정보 조회"""
    from app.models.menu import NutritionEstimate

    # 사이드/음료 제외 키워드
    exclude_keywords = ["사이드", "side", "음료", "drink", "beverage", "드링크"]

    # 메뉴 + 영양 정보 조회
    results = db.query(
        MenuItem,
        Menu.name.label("category_name"),
        NutritionEstimate.protein_g,
        NutritionEstimate.sugar_g,
        NutritionEstimate.calories
    ).join(
        Menu, MenuItem.menu_id == Menu.id
    ).outerjoin(
        NutritionEstimate, MenuItem.id == NutritionEstimate.item_id
    ).filter(
        Menu.store_id == store_id,
        MenuItem.is_available == True
    ).all()

    # 변환
    menus = []
    for item, category_name, protein_g, sugar_g, calories in results:
        # 사이드/음료 제외
        if any(keyword in category_name.lower() for keyword in exclude_keywords):
            continue

        menus.append({
            "id": item.id,
            "name": item.name,
            "category": category_name,
            "protein_g": float(protein_g) if protein_g else 0,
            "sugar_g": float(sugar_g) if sugar_g else 0,
            "calories": float(calories) if calories else 0
        })

    return menus


def generate_simple_story(
    menu_names: List[str],
    weather: Dict,
    time_info: Dict,
    trends: List[str],
    special_day: str = ""
) -> tuple[str, str]:
    """간단한 광고 문구 생성 (GPT)"""

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    # 메뉴 텍스트
    menu_text = ", ".join(menu_names[:15])

    # 트렌드 텍스트
    trend_text = ", ".join(trends[:3]) if trends else ""

    # 날씨 정보
    weather_desc = weather.get("description", "맑음")
    temperature = weather.get("temperature", 15)

    # 시간 정보
    period_kr = time_info.get("period_kr", "오후")

    # 특별한 날 정보
    special_info = f"\n- 특별한 날: {special_day}" if special_day else ""

    prompt = f"""다음 메뉴 중 하나를 사용하여 감성적이고 풍부한 광고 문구를 작성하세요.

**메뉴 목록:**
{menu_text}

**현재 상황:**
- 날씨: {weather_desc}, {temperature}도
- 시간: {period_kr}{special_info}
{f'- 트렌드: {trend_text}' if trend_text else ''}

**규칙:**
1. 위 메뉴 중 정확히 하나만 선택
2. 메뉴 이름을 그대로 정확히 사용
3. 2-3문장으로 구성, 전체 80-120자 정도
4. 날씨, 시간대, 특별한 날을 자연스럽게 녹여낸 감성적인 표현 사용
5. 메뉴의 특징이나 맛을 상상력 있게 표현
6. 고객이 그 순간 그 메뉴를 먹고 싶게 만드는 스토리텔링

**좋은 예시:**
"추운 겨울 아침, 따뜻한 국물이 생각나는 순간입니다. 뜨끈한 육개장 한 그릇으로 온몸에 활력을 불어넣어보세요. 매콤하고 진한 국물이 추위를 녹여줄 거예요."

응답 형식 (JSON):
{{"story": "광고 문구 (2-3문장, 80-120자)", "menu": "선택한 메뉴 이름"}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 광고 문구 전문가입니다. 제공된 메뉴 이름만 정확히 사용하세요."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=200,
            response_format={"type": "json_object"}
        )

        import json
        result = json.loads(response.choices[0].message.content)
        return result["story"], result["menu"]

    except Exception as e:
        logger.error(f"Failed to generate story: {e}")
        # 폴백: 첫 번째 메뉴 사용
        return f"{weather_desc} {period_kr}, {menu_names[0]}으로 특별한 시간을 보내보세요.", menu_names[0]


def create_highlights(
    menus: List[Dict],
    featured_menu: str,
    context: Dict
) -> List[Dict]:
    """3개 슬롯 생성"""

    highlights = []

    # 1번: 오늘의 추천 (광고 문구에 사용된 메뉴)
    featured = next((m for m in menus if m["name"] == featured_menu), None)
    if featured:
        # 구체적인 날씨/시간 기반 추천 이유 생성
        weather_desc = context.get("weather", {}).get("description", "맑음")
        temperature = context.get("weather", {}).get("temperature", 15)
        period_kr = context.get("time_info", {}).get("period_kr", "오후")

        # 온도에 따른 표현
        if temperature < 0:
            temp_desc = "영하의 추운 날씨"
        elif temperature < 10:
            temp_desc = "쌀쌀한 날씨"
        elif temperature < 20:
            temp_desc = "선선한 날씨"
        elif temperature < 28:
            temp_desc = "따뜻한 날씨"
        else:
            temp_desc = "더운 날씨"

        reason = f"{temp_desc} {period_kr}에는 {featured['name']}을(를) 추천합니다"

        highlights.append({
            "type": "today",
            "menu_id": featured["id"],
            "menu_name": featured["name"],
            "reason": reason,
            "context_info": {
                "weather": weather_desc,
                "temperature": temperature,
                "season": context.get("season", ""),
                "period": period_kr
            }
        })

    # 2번: 고단백 추천 (단백질 10g 초과)
    high_protein_menus = [m for m in menus if m["protein_g"] > 10]
    if high_protein_menus:
        best_protein = max(high_protein_menus, key=lambda x: x["protein_g"])
        highlights.append({
            "type": "high_protein",
            "menu_id": best_protein["id"],
            "menu_name": best_protein["name"],
            "protein_g": round(best_protein["protein_g"], 1),
            "reason": f"단백질 {round(best_protein['protein_g'], 1)}g 함유로 근육 건강에 좋습니다"
        })
    else:
        highlights.append({
            "type": "high_protein",
            "menu_id": None,
            "menu_name": None,
            "protein_g": None,
            "reason": None
        })

    # 3번: 달콤 추천 (당류 10g 초과)
    sweet_menus = [m for m in menus if m["sugar_g"] > 10]
    if sweet_menus:
        best_sweet = max(sweet_menus, key=lambda x: x["sugar_g"])
        highlights.append({
            "type": "sweet",
            "menu_id": best_sweet["id"],
            "menu_name": best_sweet["name"],
            "sugar_g": round(best_sweet["sugar_g"], 1),
            "reason": f"당류 {round(best_sweet['sugar_g'], 1)}g으로 달콤한 맛을 즐기실 수 있습니다"
        })
    else:
        highlights.append({
            "type": "sweet",
            "menu_id": None,
            "menu_name": None,
            "sugar_g": None,
            "reason": None
        })

    return highlights


def find_similar_story(
    db: Session,
    store_id: int,
    temperature: float,
    is_weekend: bool,
    is_special_day: bool
) -> Optional[SeasonalStory]:
    """유사한 조건의 저장된 스토리 찾기 (GPT 폴백)"""

    # 온도 범위: ±5도
    temp_min = temperature - 5
    temp_max = temperature + 5

    similar = db.query(SeasonalStory).filter(
        SeasonalStory.store_id == store_id,
        SeasonalStory.temperature.between(temp_min, temp_max),
        SeasonalStory.is_weekend == (1 if is_weekend else 0),
        SeasonalStory.is_special_day == (1 if is_special_day else 0)
    ).order_by(
        func.abs(SeasonalStory.temperature - temperature)
    ).first()

    return similar


@router.post(
    "/generate",
    response_model=SeasonalStoryResponse,
    summary="시즈널 스토리 생성 (신규 구조)",
    responses={
        200: {"description": "성공", "model": SeasonalStoryResponse},
        500: {"description": "서버 오류", "model": ErrorResponse}
    }
)
async def generate_seasonal_story(
    request: SeasonalStoryRequest,
    db: Session = Depends(get_db)
):
    """
    시즈널 스토리 생성 (완전히 새로운 구조)

    1. 매장 메뉴 + 영양 정보 조회
    2. 광고 문구 생성 (메뉴 이름 포함)
    3. 3개 슬롯 생성 (오늘의 추천, 고단백, 달콤)
    4. 중복 방지 저장
    """

    try:
        logger.info(f"[NEW] Seasonal story requested for store_id={request.store_id}")

        # 1. 매장 메뉴 + 영양 정보 조회
        menus = get_menu_with_nutrition(db, request.store_id)

        if not menus:
            raise HTTPException(
                status_code=400,
                detail="매장에 조회 가능한 메뉴가 없습니다."
            )

        menu_names = [m["name"] for m in menus]
        logger.info(f"✅ Found {len(menus)} menus: {', '.join(menu_names[:5])}...")

        # 2. 컨텍스트 수집
        context = context_collector_service.get_full_context(
            location=request.location,
            lat=request.latitude,
            lon=request.longitude
        )

        # 특별한 날 체크
        is_special, special_day_name = check_special_day()
        is_weekend = datetime.now().weekday() >= 5

        # 3. 광고 문구 생성
        story, featured_menu = generate_simple_story(
            menu_names=menu_names,
            weather=context.get("weather", {}),
            time_info=context.get("time_info", {}),
            trends=context.get("trends", []),
            special_day=special_day_name if is_special else ""
        )

        logger.info(f"📝 Story: {story} (Featured: {featured_menu})")

        # 4. 3개 슬롯 생성
        highlights = create_highlights(menus, featured_menu, context)

        # 5. 중복 방지 저장
        existing = db.query(SeasonalStory).filter(
            and_(
                SeasonalStory.store_id == request.store_id,
                SeasonalStory.featured_menu_name == featured_menu,
                SeasonalStory.story_content == story
            )
        ).first()

        if not existing:
            new_story = SeasonalStory(
                store_id=request.store_id,
                store_name=request.store_name,
                featured_menu_name=featured_menu,
                story_content=story,
                weather_condition=context.get("weather", {}).get("condition"),
                temperature=context.get("weather", {}).get("temperature"),
                season=context.get("season"),
                time_period=context.get("time_info", {}).get("period"),
                is_special_day=1 if is_special else 0,
                is_weekend=1 if is_weekend else 0,
                trend_keywords=context.get("trends", [])[:5]
            )
            db.add(new_story)
            db.commit()
            logger.info(f"💾 Story saved to DB (ID: {new_story.id})")
        else:
            logger.info(f"⚠️ Duplicate story not saved")

        # 6. 응답 생성
        korea_tz = pytz.timezone('Asia/Seoul')
        response_data = {
            "story": story,
            "highlights": highlights,
            "context": {
                "weather": context.get("weather"),
                "season": context.get("season"),
                "time_info": context.get("time_info"),
                "trends": context.get("trends", [])[:5],
                "special_day": special_day_name if is_special else None,
                "is_weekend": is_weekend
            },
            "store_info": {
                "store_id": request.store_id,
                "store_name": request.store_name,
                "location": request.location
            },
            "generated_at": datetime.now(korea_tz).isoformat()
        }

        return SeasonalStoryResponse(
            success=True,
            data=response_data
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate story: {e}")
        import traceback
        traceback.print_exc()

        # GPT 실패 시 폴백: DB에서 유사한 스토리 찾기
        try:
            similar = find_similar_story(
                db=db,
                store_id=request.store_id,
                temperature=context.get("weather", {}).get("temperature", 15),
                is_weekend=is_weekend,
                is_special_day=is_special
            )

            if similar:
                logger.info(f"🔄 Using similar story from DB (ID: {similar.id})")
                response_data = {
                    "story": similar.story_content,
                    "highlights": [],  # 하이라이트는 생략
                    "context": context,
                    "generated_at": datetime.now(pytz.timezone('Asia/Seoul')).isoformat(),
                    "fallback": True
                }
                return SeasonalStoryResponse(success=True, data=response_data)
        except Exception as fallback_error:
            logger.error(f"Fallback also failed: {fallback_error}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": 500,
                    "message": "스토리 생성 중 오류가 발생했습니다.",
                    "details": str(e)
                }
            }
        )


@router.post(
    "/menu-storytelling",
    response_model=MenuStorytellingResponse,
    summary="메뉴 스토리텔링 생성",
    description="메뉴 클릭 시 보여줄 스토리텔링 문구를 생성합니다.",
    responses={
        200: {"description": "성공", "model": MenuStorytellingResponse},
        500: {"description": "서버 오류", "model": ErrorResponse}
    }
)
async def generate_menu_storytelling(request: MenuStorytellingRequest):
    """
    메뉴 스토리텔링 생성

    메뉴 이름, 재료, 원산지, 역사 정보를 바탕으로
    감성적인 스토리텔링 문구를 생성합니다.
    """
    try:
        logger.info(f"Menu storytelling generation requested: {request}")

        # 스토리텔링 생성
        storytelling = story_generator_service.generate_menu_storytelling(
            menu_name=request.menu_name,
            ingredients=request.ingredients,
            origin=request.origin,
            history=request.history
        )

        # 응답 생성
        korea_tz = pytz.timezone('Asia/Seoul')
        response_data = {
            "storytelling": storytelling,
            "menu_id": request.menu_id,
            "menu_name": request.menu_name,
            "generated_at": datetime.now(korea_tz).isoformat()
        }

        logger.info("Menu storytelling generated successfully")

        return MenuStorytellingResponse(
            success=True,
            data=response_data
        )

    except Exception as e:
        logger.error(f"Failed to generate menu storytelling: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": 500,
                    "message": "메뉴 스토리텔링 생성 중 오류가 발생했습니다.",
                    "details": str(e)
                }
            }
        )
