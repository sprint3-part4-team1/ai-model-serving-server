import os
from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv

from .routes.seasonal_story import router as seasonal_story_router
from .routes.recommendation_router import router as recommendation_router
from .routes.story_router import router as story_router

# .env 파일 로드
load_dotenv()

app = FastAPI(
    title="AI Model Serving Server",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "AI Model Server is running"}

@app.post("/predict")
def predict(item: dict):
    return {"input": item, "prediction": "dummy_result"}


# 라우터 등록
app.include_router(seasonal_story_router, prefix="/api/v1/seasonal-story", tags=["Seasonal Story"])
app.include_router(recommendation_router, prefix="/api/v1", tags=["Recommendations"])
app.include_router(story_router, prefix="/api/v1", tags=["Story"])


# uvicorn 실행 (개발 환경용)
if __name__ == "__main__":
    port = int(os.getenv("PORT", "9090"))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)

