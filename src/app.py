import os
from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv
from story_service import generate_story_for_item

# .env 파일 로드
load_dotenv()

# FastAPI 객체 생성
app = FastAPI(
    title="AI Model Serving Server",
    docs_url="/docs",     # Swagger UI
    redoc_url="/redoc"    # ReDoc
)

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

# uvicorn 실행 (개발 환경용)
if __name__ == "__main__":
    port = int(os.getenv("PORT", 9090))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
