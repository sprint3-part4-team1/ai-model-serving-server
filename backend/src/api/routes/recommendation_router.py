from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ...recommendation.recommendation_service import RecommendationService

router = APIRouter()

# Request/Response 모델 정의 (Pydantic)
class RecommendationRequest(BaseModel):
    """추천 요청 모델"""
    customer_request: str
    source: Optional[str] = "mysql"
    store_id: Optional[int] = 1

    class Config:
        schema_extra = {
            "example": {
                "customer_request": "칼로리 낮은 음료 추천해줘",
                "source": "mysql",
                "store_id": 1
            }
        }

# 추천 시스템 엔드포인트
@router.post("/recommendations")
def get_recommendations(request: RecommendationRequest):
    """
    고객 요청 기반 메뉴 추천 🍽️

    **사용 예시:**
    ```json
    {
        "customer_request": "칼로리 낮은 음료 추천해줘",
        "source": "mysql",
        "store_id": 1
    }
    ```

    **응답:**
    - success: 성공 여부
    - total_found: 발견된 메뉴 수
    - recommendations: 추천 메뉴 리스트 (최대 3개)
    """
    service = RecommendationService()

    try:
        result = service.get_recommendations(
            customer_request=request.customer_request,
            source=request.source,
            store_id=request.store_id
        )

        if not result['success']:
            raise HTTPException(status_code=500, detail=result['error'])

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        service.close()

# 추천 결과 포맷팅 엔드포인트 
@router.post("/recommendations/formatted")
def get_recommendations_formatted(request: RecommendationRequest):
    """
    고객 요청 기반 메뉴 추천 (포맷팅된 텍스트 반환)

    **사용 예시:**
    ```json
    {
        "customer_request": "고단백 메뉴 찾아줘",
        "source": "mysql",
        "store_id": 1
    }
    ```

    **응답:**
    - formatted_text: 보기 좋게 포맷팅된 텍스트
    - raw_data: 원본 데이터 (선택적)
    """
    service = RecommendationService()

    try:
        result = service.get_recommendations(
            customer_request=request.customer_request,
            source=request.source,
            store_id=request.store_id
        )

        if not result['success']:
            raise HTTPException(status_code=500, detail=result['error'])

        formatted_text = service.format_output(result)

        return {
            "formatted_text": formatted_text,
            "raw_data": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        service.close()