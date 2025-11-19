import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
from dotenv import load_dotenv
from story_service import generate_story_for_item
from recommendation.recommendation_service import RecommendationService
from api.seasonal_story import router as seasonal_story_router

# .env 파일 로드
load_dotenv()

# FastAPI 객체 생성
app = FastAPI(
    title="AI Model Serving Server",
    docs_url="/docs",     # Swagger UI
    redoc_url="/redoc"    # ReDoc
)

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

# 기본 엔드포인트
@app.get("/")
def read_root():
    return {"status": "ok", "message": "AI Model Server is running"}

# 예시 엔드포인트: 모델 서빙
@app.post("/predict")
def predict(item: dict):
    # 실제 모델 로직은 여기서 처리
    return {"input": item, "prediction": "dummy_result"}

@app.get("/items/{item_id}/story")
def get_item_story(item_id: int):
    """
    특정 메뉴 아이템의 스토리를 반환합니다.
    - DB에 스토리가 없으면 LLM으로 생성 후 저장
    - DB에 스토리가 있으면 24시간 이내면 캐시 반환
    - 24시간 지나면 LLM으로 다시 생성 후 업데이트
    """
    story_data = generate_story_for_item(item_id)
    return story_data

# 추천 시스템 엔드포인트
@app.post("/recommendations")
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
@app.post("/recommendations/formatted")
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


# Seasonal Story 라우터 등록
app.include_router(
    seasonal_story_router,
    prefix="/api/v1/seasonal-story",
    tags=["Seasonal Story"]
)


# uvicorn 실행 (개발 환경용)
if __name__ == "__main__":
    port = int(os.getenv("PORT", 9090))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
