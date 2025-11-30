"""
FastAPI 메인 애플리케이션
소상공인 광고 콘텐츠 생성 서비스
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import time
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import app_logger as logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행되는 이벤트"""
    # 시작 시
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} 시작")
    logger.info(f"환경: {settings.ENVIRONMENT}")
    logger.info(f"디버그 모드: {settings.DEBUG}")

    # 필요한 디렉토리 확인
    settings.ensure_directories()
    logger.info("필수 디렉토리 확인 완료")

    yield

    # 종료 시
    logger.info(f"👋 {settings.APP_NAME} 종료")


# FastAPI 앱 생성
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="소상공인을 위한 AI 기반 광고 콘텐츠 자동 생성 서비스",
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)


# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# Gzip 압축 미들웨어
app.add_middleware(GZipMiddleware, minimum_size=1000)


# 요청 로깅 미들웨어
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """모든 HTTP 요청 로깅"""
    start_time = time.time()

    # 요청 정보 로깅
    logger.info(f"➡️  {request.method} {request.url.path}")

    # 요청 처리
    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # 응답 정보 로깅
        logger.info(
            f"⬅️  {request.method} {request.url.path} "
            f"- Status: {response.status_code} "
            f"- Time: {process_time:.3f}s"
        )

        # 응답 헤더에 처리 시간 추가
        response.headers["X-Process-Time"] = str(process_time)
        return response

    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"❌ {request.method} {request.url.path} "
            f"- Error: {str(e)} "
            f"- Time: {process_time:.3f}s"
        )
        raise


# 전역 예외 핸들러
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP 예외 처리"""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """요청 검증 예외 처리"""
    logger.error(f"Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": 422,
                "message": "입력 데이터 검증 실패",
                "details": exc.errors(),
            }
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """일반 예외 처리"""
    logger.exception(f"Unexpected Error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": 500,
                "message": "서버 내부 오류가 발생했습니다.",
                "details": str(exc) if settings.DEBUG else None,
            }
        },
    )


# 헬스 체크 엔드포인트
@app.get("/health", tags=["System"])
async def health_check():
    """서비스 상태 확인"""
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        }
    }


@app.get("/", tags=["System"])
async def root():
    """루트 엔드포인트"""
    return {
        "success": True,
        "data": {
            "message": f"Welcome to {settings.APP_NAME}",
            "version": settings.APP_VERSION,
            "docs": "/api/docs",
            "health": "/health",
        }
    }


# 정적 파일 서빙 설정
from fastapi.staticfiles import StaticFiles
import os

# 업로드 디렉토리 생성
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# 정적 파일 마운트 (/data/uploads로 통일)
app.mount("/data/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Static 디렉토리 마운트
os.makedirs(settings.STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

# API 라우터 등록
from app.api.endpoints import ad_copy, text_to_image, background, seasonal_story, menu, menu_ocr, menu_generation
app.include_router(ad_copy.router, prefix="/api/v1/ad-copy", tags=["광고 문구 생성"])
app.include_router(text_to_image.router, prefix="/api/v1/text-to-image", tags=["텍스트→이미지"])
app.include_router(background.router, prefix="/api/v1/background", tags=["배경 처리"])
app.include_router(seasonal_story.router, prefix="/api/v1/seasonal-story", tags=["시즈널 스토리"])
app.include_router(menu.router, prefix="/api/v1/menu", tags=["메뉴 필터링"])
app.include_router(menu_ocr.router, prefix="/api/v1/menu-ocr", tags=["메뉴판 OCR/Repaint"])
app.include_router(menu_generation.router, prefix="/api/v1/menu-generation", tags=["메뉴판 생성"])

# 추후 추가할 라우터들
# from app.api.endpoints import image_to_image, templates
# app.include_router(image_to_image.router, prefix="/api/v1/image-to-image", tags=["이미지→이미지"])
# app.include_router(templates.router, prefix="/api/v1/templates", tags=["템플릿"])


if __name__ == "__main__":
    import uvicorn

    logger.info(f"서버 시작: http://{settings.HOST}:{settings.PORT}")

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
