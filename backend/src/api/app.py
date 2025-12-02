import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

# backend/app 모듈을 import하기 위한 경로 설정
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from .routes.seasonal_story import router as seasonal_story_router
from .routes.recommendation_router import router as recommendation_router
from .routes.story_router import router as story_router
from .routes.nutrition_router import router as nutrition_router

# backend/app의 라우터들 import
from app.api.endpoints import menu, menu_ocr, menu_generation, ad_copy, text_to_image, background

# .env 파일 로드
load_dotenv()

# API 태그 메타데이터 정의 (순서 제어)
tags_metadata = [
    # === 주요 API ===
    {
        "name": "1️⃣ 매장 관리",
        "description": "매장 CRUD - 매장 생성, 조회, 수정, 삭제"
    },
    {
        "name": "2️⃣ 메뉴판 생성",
        "description": "AI 기반 메뉴판 자동 생성 - 이미지 및 설명 자동 생성"
    },
    {
        "name": "3️⃣ 메뉴 조회",
        "description": "매장별 메뉴 조회 및 AI 필터링"
    },
    {
        "name": "4️⃣ 영양소 분석",
        "description": "메뉴 영양소 분석 및 스토리텔링"
    },
    # === 보류/미사용 API ===
    {
        "name": "🔒 (보류) Seasonal Story",
        "description": "⚠️ 현재 미사용 - 시즈널 스토리 생성"
    },
    {
        "name": "🔒 (보류) Recommendations",
        "description": "⚠️ 현재 미사용 - 메뉴 추천"
    },
    {
        "name": "🔒 (보류) Story",
        "description": "⚠️ 현재 미사용 - 스토리텔링"
    },
    {
        "name": "🔒 (보류) 메뉴판 OCR",
        "description": "⚠️ 현재 미사용 - 메뉴판 이미지 인식"
    },
    {
        "name": "🔒 (보류) 광고 문구",
        "description": "⚠️ 현재 미사용 - 광고 문구 생성"
    },
    {
        "name": "🔒 (보류) 텍스트→이미지",
        "description": "⚠️ 현재 미사용 - 텍스트 기반 이미지 생성"
    },
    {
        "name": "🔒 (보류) 배경 처리",
        "description": "⚠️ 현재 미사용 - 배경 제거/교체"
    },
]

app = FastAPI(
    title="AI Model Serving Server",
    description="소상공인을 위한 AI 기반 광고 콘텐츠 및 메뉴 관리 서비스",
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포 시에는 특정 도메인만 허용하도록 수정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "AI Model Server is running"}

@app.get("/health")
def health_check():
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "service": "AI Model Serving Server",
            "version": "1.0.0"
        }
    }

# Static 파일 서빙 설정
upload_dir = backend_path / "data" / "uploads"
os.makedirs(upload_dir, exist_ok=True)
app.mount("/data/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")

static_dir = backend_path / "data" / "static"
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# === 주요 API 등록 ===
app.include_router(menu.router, prefix="/api/v1/menu", tags=["1️⃣ 매장 관리", "3️⃣ 메뉴 조회"])
app.include_router(menu_generation.router, prefix="/api/v1/menu-generation", tags=["2️⃣ 메뉴판 생성"])
app.include_router(nutrition_router, prefix="/api/v1/nutrition", tags=["4️⃣ 영양소 분석"])

# === 보류/미사용 API 등록 ===
app.include_router(seasonal_story_router, prefix="/api/v1/seasonal-story", tags=["🔒 (보류) Seasonal Story"])
app.include_router(recommendation_router, prefix="/api/v1", tags=["🔒 (보류) Recommendations"])
app.include_router(story_router, prefix="/api/v1", tags=["🔒 (보류) Story"])
app.include_router(menu_ocr.router, prefix="/api/v1/menu-ocr", tags=["🔒 (보류) 메뉴판 OCR"])
app.include_router(ad_copy.router, prefix="/api/v1/ad-copy", tags=["🔒 (보류) 광고 문구"])
app.include_router(text_to_image.router, prefix="/api/v1/text-to-image", tags=["🔒 (보류) 텍스트→이미지"])
app.include_router(background.router, prefix="/api/v1/background", tags=["🔒 (보류) 배경 처리"])


# uvicorn 실행 (개발 환경용)
if __name__ == "__main__":
    port = int(os.getenv("PORT", "9091"))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)

# 실제 실행시 최상위 루트에서,
# python -m uvicorn backend.src.api.app:app --reload --host 0.0.0.0 --port 9091
