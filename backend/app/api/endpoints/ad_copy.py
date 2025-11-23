"""
광고 문구 생성 API 엔드포인트
"""
from fastapi import APIRouter, HTTPException, status
from app.schemas.ad_copy import AdCopyRequest, AdCopyResponse
from app.services.openai_service import openai_service
from app.core.logging import app_logger as logger
import uuid


router = APIRouter()


@router.post("/generate", response_model=AdCopyResponse, status_code=status.HTTP_200_OK)
async def generate_ad_copy(request: AdCopyRequest):
    """
    광고 문구 생성

    소상공인을 위한 AI 기반 광고 문구 자동 생성 API입니다.
    제품/서비스 정보를 입력하면 효과적인 광고 문구를 생성합니다.

    **주요 기능**:
    - 다양한 톤과 스타일 지원 (전문적, 친근한, 감성적 등)
    - 타겟 고객 맞춤형 문구 생성
    - 플랫폼별 최적화 (Instagram, Facebook, 블로그 등)
    - 이미지 분석 기반 문구 생성 (선택사항)
    - 헤드라인 및 해시태그 자동 생성

    **사용 예시**:
    ```json
    {
      "product_name": "수제 초콜릿 케이크",
      "product_description": "벨기에산 다크 초콜릿을 사용한 진한 초콜릿 케이크",
      "tone": "emotional",
      "length": "short",
      "target_audience": "20-30대 여성",
      "platform": "Instagram",
      "num_variations": 3
    }
    ```
    """
    try:
        logger.info(f"광고 문구 생성 요청 - 제품: {request.product_name}")

        # OpenAI 서비스로 문구 생성
        variations, generation_time, model_used = await openai_service.generate_ad_copy(request)

        # 생성 ID 생성
        generation_id = str(uuid.uuid4())

        # 응답 생성
        response = AdCopyResponse(
            success=True,
            generation_id=generation_id,
            variations=variations,
            model_used=model_used,
            generation_time=generation_time
        )

        logger.info(f"광고 문구 생성 성공 - ID: {generation_id}, 개수: {len(variations)}")

        return response

    except Exception as e:
        logger.exception(f"광고 문구 생성 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"광고 문구 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/examples", status_code=status.HTTP_200_OK)
async def get_examples():
    """
    광고 문구 생성 예시

    다양한 업종별 광고 문구 생성 예시를 제공합니다.
    """
    examples = [
        {
            "industry": "카페",
            "request": {
                "product_name": "시그니처 라떼",
                "tone": "friendly",
                "length": "short"
            },
            "sample_output": "따뜻한 하루의 시작, 우리 카페의 시그니처 라떼와 함께하세요. ☕"
        },
        {
            "industry": "음식점",
            "request": {
                "product_name": "수제 떡볶이",
                "tone": "energetic",
                "length": "medium"
            },
            "sample_output": "매콤달콤한 비법 소스가 살아있는 수제 떡볶이! 매일 새벽 만드는 신선한 떡으로 쫄깃한 식감을 자랑합니다."
        },
        {
            "industry": "소매업",
            "request": {
                "product_name": "핸드메이드 가죽 지갑",
                "tone": "luxury",
                "length": "short"
            },
            "sample_output": "장인의 손길이 닿은 프리미엄 가죽 지갑. 당신의 품격을 높여드립니다."
        }
    ]

    return {
        "success": True,
        "examples": examples
    }


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """광고 문구 생성 서비스 헬스 체크"""
    return {
        "success": True,
        "service": "ad_copy_generation",
        "status": "healthy",
        "model": openai_service.model
    }
