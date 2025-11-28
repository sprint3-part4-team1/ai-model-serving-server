"""
메뉴판 OCR 및 Repaint API 엔드포인트
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from pathlib import Path
import shutil
import uuid

from app.schemas.menu_ocr import (
    MenuOCRRequest,
    MenuOCRResponse,
    MenuRepaintRequest,
    MenuRepaintResponse,
)
from app.services.menu_ocr_service_simple import menu_ocr_service
from app.core.logging import app_logger as logger
from app.core.config import settings

router = APIRouter()


@router.post("/ocr", response_model=MenuOCRResponse, status_code=status.HTTP_200_OK)
async def process_menu_ocr(
    image: UploadFile = File(..., description="메뉴판 이미지"),
    crop_mode: bool = True,
    save_results: bool = True,
):
    """
    메뉴판 OCR 처리

    메뉴판 이미지에서 텍스트와 구조를 추출합니다.

    **기능**:
    - PaddleOCR을 사용한 텍스트 인식
    - 메뉴 구조 파싱 (제목, 항목, 가격 등)
    - 바운딩 박스 시각화
    - 스키마 생성 (mmd 형식)

    **사용 예시**:
    ```bash
    curl -X POST "http://localhost:9090/api/v1/menu-ocr/ocr" \\
      -F "image=@menu.png" \\
      -F "crop_mode=true"
    ```
    """
    try:
        logger.info(f"메뉴판 OCR 요청 - 파일명: {image.filename}")

        # 임시 파일 저장
        upload_dir = Path(settings.STATIC_DIR) / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)

        temp_file_id = str(uuid.uuid4())
        temp_file_path = upload_dir / f"{temp_file_id}_{image.filename}"

        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # OCR 처리
        request = MenuOCRRequest(crop_mode=crop_mode, save_results=save_results)
        result = await menu_ocr_service.process_menu_ocr(str(temp_file_path), request)

        logger.info(f"메뉴판 OCR 완료 - ID: {result.ocr_id}")

        return result

    except Exception as e:
        logger.exception(f"메뉴판 OCR 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"메뉴판 OCR 처리 중 오류가 발생했습니다: {str(e)}"
        )
    finally:
        # 임시 파일 삭제 (선택적)
        # if temp_file_path.exists():
        #     temp_file_path.unlink()
        pass


@router.post("/repaint", response_model=MenuRepaintResponse, status_code=status.HTTP_200_OK)
async def process_menu_repaint(request: MenuRepaintRequest):
    """
    메뉴판 재생성

    OCR로 추출한 스키마를 기반으로 메뉴판 이미지를 재생성합니다.
    스키마를 수정하여 메뉴 내용을 변경할 수 있습니다.

    **기능**:
    - 수정된 스키마로 메뉴판 이미지 재생성
    - 원본 레이아웃 유지
    - 텍스트 치환 및 위치 조정

    **사용 예시**:
    ```json
    {
      "ocr_id": "abc123",
      "schema_content": "# 카페 메뉴\\n## 커피\\n- 아메리카노: 4500원"
    }
    ```
    """
    try:
        logger.info(f"메뉴판 Repaint 요청 - OCR ID: {request.ocr_id}")

        result = await menu_ocr_service.process_menu_repaint(request)

        logger.info(f"메뉴판 Repaint 완료 - ID: {result.repaint_id}")

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.exception(f"메뉴판 Repaint 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"메뉴판 Repaint 처리 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """메뉴판 OCR 서비스 헬스 체크"""
    return {
        "success": True,
        "service": "menu_ocr",
        "status": "healthy",
        "paddle_ocr_available": menu_ocr_service.paddle_ocr is not None
    }
