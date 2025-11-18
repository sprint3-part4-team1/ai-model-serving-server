import os
from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv

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

# uvicorn 실행 (개발 환경용)
if __name__ == "__main__":
    port = int(os.getenv("PORT", 9090))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
