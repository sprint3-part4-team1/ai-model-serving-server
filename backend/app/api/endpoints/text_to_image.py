"""
텍스트→이미지 생성 API 엔드포인트
"""
from fastapi import APIRouter, HTTPException, status
from app.schemas.image import TextToImageRequest, ImageGenerationResponse
from app.services.sd_service import sd_service
from app.utils.image_utils import save_images
from app.core.logging import app_logger as logger
import uuid


router = APIRouter()


@router.post("/generate", response_model=ImageGenerationResponse, status_code=status.HTTP_200_OK)
async def generate_text_to_image(request: TextToImageRequest):
    """
    텍스트→이미지 생성

    생성형 AI를 활용하여 텍스트 설명으로 고품질 이미지를 생성합니다.

    **주요 기능**:
    - Stable Diffusion XL 활용
    - 6가지 스타일 프리셋 (Realistic, Artistic, Minimalist, Vintage, Modern, Colorful)
    - 다양한 종횡비 지원 (1:1, 4:5, 16:9, 21:9)
    - 최대 2048x2048 고해상도
    - 프롬프트 자동 향상

    **생성 파라미터**:
    - `num_inference_steps`: 20-100 (높을수록 품질↑, 시간↑)
    - `guidance_scale`: 1.0-20.0 (높을수록 프롬프트에 충실)
    - `negative_prompt`: 원하지 않는 요소 제외

    **성능**:
    - GPU: 15-30초/이미지
    - CPU: 2-5분/이미지

    **사용 예시**:
    ```json
    {
      "prompt": "A delicious chocolate cake on a wooden table",
      "style": "realistic",
      "aspect_ratio": "1:1",
      "num_inference_steps": 50,
      "guidance_scale": 7.5,
      "num_images": 2
    }
    ```
    """
    try:
        logger.info(f"텍스트→이미지 생성 요청 - 프롬프트: {request.prompt[:100]}...")

        # Stable Diffusion 서비스로 이미지 생성
        images, generation_time, parameters = await sd_service.generate_text_to_image(request)

        # 이미지 파일 저장 및 URL 생성
        image_urls = save_images(images)

        if not image_urls:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="이미지 저장 실패"
            )

        # 생성 ID 생성
        generation_id = str(uuid.uuid4())

        # 응답 생성
        response = ImageGenerationResponse(
            success=True,
            generation_id=generation_id,
            images=image_urls,
            model_used="stable-diffusion-xl-base-1.0",
            parameters=parameters,
            generation_time=generation_time
        )

        logger.info(
            f"텍스트→이미지 생성 성공 - ID: {generation_id}, "
            f"개수: {len(image_urls)}, 시간: {generation_time:.2f}초"
        )

        return response

    except Exception as e:
        logger.exception(f"텍스트→이미지 생성 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이미지 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/styles", status_code=status.HTTP_200_OK)
async def get_available_styles():
    """
    사용 가능한 스타일 목록 조회

    6가지 이미지 스타일 프리셋의 상세 정보를 반환합니다.
    """
    styles = [
        {
            "id": "realistic",
            "name": "사실적 (Realistic)",
            "description": "전문 제품 사진 스타일. 스튜디오 조명, 고해상도, 선명한 디테일",
            "use_case": "제품 사진, 광고용 이미지",
            "example_prompt": "professional product photography, studio lighting"
        },
        {
            "id": "artistic",
            "name": "예술적 (Artistic)",
            "description": "일러스트 스타일. 창의적인 구성, 생동감 있는 색상",
            "use_case": "창의적인 광고, SNS 콘텐츠",
            "example_prompt": "artistic illustration, creative design"
        },
        {
            "id": "minimalist",
            "name": "미니멀 (Minimalist)",
            "description": "깔끔한 구성. 단순한 배경, 현대적이고 세련됨",
            "use_case": "브랜드 이미지, 고급 제품",
            "example_prompt": "minimalist design, clean composition"
        },
        {
            "id": "vintage",
            "name": "빈티지 (Vintage)",
            "description": "레트로 감성. 필름 그레인, 따뜻한 톤",
            "use_case": "클래식한 느낌, 감성적 광고",
            "example_prompt": "vintage style, retro aesthetic"
        },
        {
            "id": "modern",
            "name": "모던 (Modern)",
            "description": "현대적 디자인. 깔끔한 선, 세련되고 전문적",
            "use_case": "테크 제품, 현대적 브랜드",
            "example_prompt": "modern design, contemporary style"
        },
        {
            "id": "colorful",
            "name": "화려함 (Colorful)",
            "description": "생동감 있는 색상. 시선을 끄는 디자인, 높은 채도",
            "use_case": "주목도가 필요한 광고, 젊은 타겟",
            "example_prompt": "vibrant colors, eye-catching design"
        }
    ]

    return {
        "success": True,
        "styles": styles,
        "total": len(styles)
    }


@router.get("/aspect-ratios", status_code=status.HTTP_200_OK)
async def get_aspect_ratios():
    """
    지원하는 종횡비 목록 조회

    다양한 플랫폼에 최적화된 이미지 비율을 제공합니다.
    """
    ratios = [
        {
            "id": "1:1",
            "name": "정사각형 (1:1)",
            "dimensions": "1024 x 1024",
            "use_case": "Instagram 피드, 프로필 이미지",
            "platform": "Instagram"
        },
        {
            "id": "4:5",
            "name": "세로 (4:5)",
            "dimensions": "896 x 1152",
            "use_case": "Instagram Story, 모바일 광고",
            "platform": "Instagram, Mobile"
        },
        {
            "id": "16:9",
            "name": "가로 (16:9)",
            "dimensions": "1344 x 768",
            "use_case": "YouTube 썸네일, 블로그 헤더",
            "platform": "YouTube, Blog"
        },
        {
            "id": "21:9",
            "name": "와이드 (21:9)",
            "dimensions": "1536 x 640",
            "use_case": "웹사이트 배너, 광고 배너",
            "platform": "Website"
        }
    ]

    return {
        "success": True,
        "aspect_ratios": ratios,
        "total": len(ratios)
    }


@router.get("/examples", status_code=status.HTTP_200_OK)
async def get_examples():
    """
    이미지 생성 예시

    다양한 업종별 이미지 생성 예시를 제공합니다.
    """
    examples = [
        {
            "industry": "카페",
            "request": {
                "prompt": "A cup of latte with beautiful latte art on a wooden table",
                "style": "realistic",
                "aspect_ratio": "1:1"
            },
            "description": "라떼 아트가 있는 커피 제품 사진"
        },
        {
            "industry": "베이커리",
            "request": {
                "prompt": "Fresh croissants and pastries in a rustic bakery setting",
                "style": "vintage",
                "aspect_ratio": "4:5"
            },
            "description": "빈티지 감성의 베이커리 제품 사진"
        },
        {
            "industry": "패션",
            "request": {
                "prompt": "Minimalist fashion product display with clean background",
                "style": "minimalist",
                "aspect_ratio": "1:1"
            },
            "description": "미니멀한 패션 제품 디스플레이"
        },
        {
            "industry": "뷰티",
            "request": {
                "prompt": "Cosmetic products with flowers and natural lighting",
                "style": "colorful",
                "aspect_ratio": "4:5"
            },
            "description": "화려한 색감의 화장품 광고"
        }
    ]

    return {
        "success": True,
        "examples": examples
    }


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """텍스트→이미지 생성 서비스 헬스 체크"""
    return {
        "success": True,
        "service": "text_to_image_generation",
        "status": "healthy",
        "model": "stable-diffusion-xl-base-1.0"
    }
