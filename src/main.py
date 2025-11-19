"""
FastAPI Main Application
시즈널 스토리 API 서버 메인 애플리케이션
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.seasonal_story import router as seasonal_story_router
from .logger import app_logger as logger

# FastAPI 앱 생성
app = FastAPI(
    title="Seasonal Story API",
    description="날씨, 계절, 시간대, 트렌드 기반 감성 스토리 생성 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정 (프론트엔드 연동용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영 환경에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(
    seasonal_story_router,
    prefix="/api/v1/seasonal-story",
    tags=["Seasonal Story"]
)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "service": "Seasonal Story API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "service": "Seasonal Story API"
    }


@app.on_event("startup")
async def startup_event():
    """서버 시작 시 실행"""
    logger.info("Seasonal Story API Server starting...")
    logger.info("Documentation available at /docs")


@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료 시 실행"""
    logger.info("Seasonal Story API Server shutting down...")
