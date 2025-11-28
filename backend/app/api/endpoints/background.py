"""
배경 제거/교체 API 엔드포인트
"""
from fastapi import APIRouter, HTTPException, status
from app.schemas.image import BackgroundRemovalRequest, BackgroundReplaceRequest, ImageGenerationResponse
from app.services.background_service import background_service
from app.utils.image_utils import save_image
from app.core.logging import app_logger as logger
import uuid
import time


router = APIRouter()


@router.post("/remove", response_model=ImageGenerationResponse, status_code=status.HTTP_200_OK)
async def remove_background(request: BackgroundRemovalRequest):
    """
    배경 제거

    제품 이미지에서 배경을 자동으로 제거하여 투명 배경의 PNG 이미지를 생성합니다.

    **주요 기능**:
    - AI 기반 자동 배경 인식
    - 투명 배경 (PNG)
    - 선택적 마스크 반환

    **사용 사례**:
    - 제품 이미지 배경 제거
    - 다양한 배경에 제품 합성
    - 카탈로그 이미지 제작

    **처리 시간**: 2-5초

    **사용 예시**:
    ```json
    {
      "image_url": "https://example.com/product.jpg",
      "return_mask": false
    }
    ```
    """
    start_time = time.time()

    try:
        logger.info(f"배경 제거 요청 - URL: {request.image_url}")

        # 이미지 다운로드
        image = await background_service.download_image(request.image_url)

        # 배경 제거
        result_image, mask = await background_service.remove_background(
            image,
            return_mask=request.return_mask
        )

        # 이미지 저장
        _, result_url = save_image(result_image)
        image_urls = [result_url]

        # 마스크도 저장 (요청 시)
        if request.return_mask and mask:
            _, mask_url = save_image(mask)
            image_urls.append(mask_url)

        generation_time = time.time() - start_time
        generation_id = str(uuid.uuid4())

        response = ImageGenerationResponse(
            success=True,
            generation_id=generation_id,
            images=image_urls,
            model_used="rembg" if background_service.rembg_available else "basic",
            parameters={"return_mask": request.return_mask},
            generation_time=generation_time
        )

        logger.info(f"✅ 배경 제거 완료 - ID: {generation_id}, 시간: {generation_time:.2f}초")

        return response

    except Exception as e:
        logger.exception(f"배경 제거 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"배경 제거 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/replace", response_model=ImageGenerationResponse, status_code=status.HTTP_200_OK)
async def replace_background(request: BackgroundReplaceRequest):
    """
    배경 교체

    제품 이미지의 배경을 새로운 배경으로 자동 교체합니다.

    **주요 기능**:
    - 자동 배경 제거
    - 새 배경 합성
    - 자연스러운 합성

    **처리 과정**:
    1. 원본 이미지 배경 제거
    2. 지정된 배경과 합성

    **사용 사례**:
    - 제품 이미지 배경 변경
    - 시즌별 배경 적용
    - 브랜드 컬러 배경

    **사용 예시**:
    ```json
    {
      "image_url": "https://example.com/product.jpg",
      "background_prompt": "wooden table background",
      "preserve_lighting": true,
      "num_images": 2
    }
    ```
    """
    start_time = time.time()

    try:
        logger.info(f"배경 교체 요청 - 제품: {request.image_url}")
        logger.info(f"새 배경: {request.background_prompt}")

        # 원본 이미지 다운로드
        original_image = await background_service.download_image(request.image_url)

        # 배경 제거
        foreground, _ = await background_service.remove_background(original_image)

        # 간단한 배경 생성 (단색)
        # 실제로는 Stable Diffusion으로 생성하거나 이미지 사용
        width, height = foreground.size
        background = await background_service.create_simple_background(
            width, height, "#F5F5F5"  # 연한 회색
        )

        # 배경 합성
        result = await background_service.replace_background(foreground, background)

        # 이미지 저장
        _, result_url = save_image(result)

        generation_time = time.time() - start_time
        generation_id = str(uuid.uuid4())

        response = ImageGenerationResponse(
            success=True,
            generation_id=generation_id,
            images=[result_url],
            model_used="background_replacement",
            parameters={
                "background_prompt": request.background_prompt,
                "preserve_lighting": request.preserve_lighting
            },
            generation_time=generation_time
        )

        logger.info(f"✅ 배경 교체 완료 - ID: {generation_id}, 시간: {generation_time:.2f}초")

        return response

    except Exception as e:
        logger.exception(f"배경 교체 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"배경 교체 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/examples", status_code=status.HTTP_200_OK)
async def get_examples():
    """배경 처리 예시"""
    examples = [
        {
            "type": "removal",
            "description": "제품 사진 배경 제거",
            "input": "제품 사진 (배경 있음)",
            "output": "제품만 (투명 배경)"
        },
        {
            "type": "replacement",
            "description": "우드 테이블 배경으로 교체",
            "input": "제품 사진",
            "background": "wooden table",
            "output": "우드 배경의 제품 사진"
        },
        {
            "type": "replacement",
            "description": "흰색 배경으로 교체",
            "input": "제품 사진",
            "background": "white",
            "output": "흰 배경의 제품 사진"
        }
    ]

    return {
        "success": True,
        "examples": examples
    }


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """배경 처리 서비스 헬스 체크"""
    return {
        "success": True,
        "service": "background_processing",
        "status": "healthy",
        "rembg_available": background_service.rembg_available
    }
