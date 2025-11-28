"""
OpenAI API 서비스
"""
import asyncio
from typing import List, Optional
import time
from openai import AsyncOpenAI
import base64
import httpx

from app.core.config import settings
from app.core.logging import app_logger as logger
from app.schemas.ad_copy import (
    AdCopyRequest,
    AdCopyVariation,
    AdCopyTone,
    AdCopyLength
)


class OpenAIService:
    """OpenAI API 서비스 클래스"""

    def __init__(self):
        """OpenAI 클라이언트 초기화"""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o"  # GPT-4o: JSON 형식 지원, 빠른 속도
        logger.info(f"OpenAI 서비스 초기화 완료 - 모델: {self.model}")

    def _build_system_prompt(self, request: AdCopyRequest) -> str:
        """시스템 프롬프트 생성"""
        tone_descriptions = {
            AdCopyTone.PROFESSIONAL: "전문적이고 신뢰감 있는",
            AdCopyTone.FRIENDLY: "친근하고 따뜻한",
            AdCopyTone.EMOTIONAL: "감성적이고 공감을 이끌어내는",
            AdCopyTone.ENERGETIC: "활기차고 역동적인",
            AdCopyTone.LUXURY: "고급스럽고 세련된",
            AdCopyTone.CASUAL: "편안하고 자연스러운"
        }

        length_descriptions = {
            AdCopyLength.SHORT: "1-2문장의 간결한",
            AdCopyLength.MEDIUM: "3-5문장의 적당한 길이의",
            AdCopyLength.LONG: "6문장 이상의 상세한"
        }

        system_prompt = f"""당신은 소상공인을 위한 전문 광고 카피라이터입니다.
다음 조건에 맞는 효과적인 광고 문구를 작성해주세요:

**톤**: {tone_descriptions[request.tone]}
**길이**: {length_descriptions[request.length]}
"""

        if request.target_audience:
            system_prompt += f"**타겟 고객**: {request.target_audience}\n"

        if request.platform:
            system_prompt += f"**게시 플랫폼**: {request.platform}\n"

        system_prompt += """
**작성 가이드라인**:
1. 제품/서비스의 핵심 가치를 명확히 전달
2. 고객의 감정에 호소하는 표현 사용
3. 행동을 유도하는 Call-to-Action 포함
4. 소상공인의 진정성과 정성을 강조
5. 플랫폼 특성에 맞는 표현 사용
6. 과장되지 않고 진솔한 표현
7. 기억에 남는 독창적인 메시지

**중요**: 반드시 JSON 형식으로 응답하세요.
"""
        return system_prompt

    def _build_user_prompt(self, request: AdCopyRequest, image_description: Optional[str] = None) -> str:
        """사용자 프롬프트 생성"""
        user_prompt = f"""**제품/서비스명**: {request.product_name}
"""

        if request.product_description:
            user_prompt += f"**설명**: {request.product_description}\n"

        if image_description:
            user_prompt += f"**이미지 분석**: {image_description}\n"

        if request.key_message:
            user_prompt += f"**핵심 메시지**: {request.key_message}\n"

        if request.additional_requirements:
            user_prompt += f"**추가 요청사항**: {request.additional_requirements}\n"

        user_prompt += f"""
{request.num_variations}개의 효과적인 광고 문구를 작성해주세요.

JSON 형식으로 응답하세요:
{{
  "variations": [
    {{
      "text": "실제 고객에게 보여줄 완전한 광고 문구를 여기에 작성하세요",
      "headline": "헤드라인 (선택사항)",
      "hashtags": ["태그1", "태그2"]
    }}
  ]
}}

예시 (참고용):
{{
  "variations": [
    {{
      "text": "가을 하늘처럼 맑은 날, 따뜻한 커피 한 잔의 여유를 느껴보세요. 우리 카페에서 특별한 순간을 만들어드립니다.",
      "headline": "가을, 커피 한 잔의 여유",
      "hashtags": ["#가을카페", "#커피타임", "#힐링"]
    }}
  ]
}}

**주의**: text 필드에는 완전한 문장으로 된 광고 문구를 작성하세요. 단순한 번호나 키워드가 아닌, 고객을 설득하는 완전한 광고 문구여야 합니다.
"""

        return user_prompt

    async def _analyze_image(self, image_url: str) -> Optional[str]:
        """이미지 분석 (GPT-4 Vision 활용)"""
        try:
            logger.info(f"이미지 분석 시작: {image_url}")

            # 이미지 다운로드
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url, timeout=30)
                response.raise_for_status()
                image_data = response.content

            # Base64 인코딩
            image_base64 = base64.b64encode(image_data).decode('utf-8')

            # GPT-4 Vision으로 이미지 분석
            response = await self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 이미지를 분석하여 광고 문구 작성에 도움이 되는 정보를 추출하는 전문가입니다."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "이 제품 이미지를 분석하여 다음 정보를 추출해주세요:\n1. 제품의 외관과 특징\n2. 색상과 디자인 스타일\n3. 전체적인 분위기와 느낌\n4. 광고에서 강조할 만한 시각적 요소"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )

            description = response.choices[0].message.content
            logger.info(f"이미지 분석 완료: {description[:100]}...")
            return description

        except Exception as e:
            logger.error(f"이미지 분석 실패: {str(e)}")
            return None

    def _parse_response(self, content: str, num_variations: int) -> List[AdCopyVariation]:
        """GPT 응답을 AdCopyVariation 리스트로 파싱"""
        import json

        try:
            # JSON 파싱
            data = json.loads(content)
            variations = []

            for var_data in data.get("variations", []):
                variation = AdCopyVariation(
                    text=var_data.get("text", ""),
                    headline=var_data.get("headline"),
                    hashtags=var_data.get("hashtags", [])
                )
                if variation.text:
                    variations.append(variation)

            return variations

        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {e}")
            # Fallback: 전체 텍스트를 하나의 variation으로
            return [AdCopyVariation(text=content.strip())]

    async def generate_ad_copy(self, request: AdCopyRequest) -> tuple[List[AdCopyVariation], float, str]:
        """
        광고 문구 생성

        Returns:
            (variations, generation_time, model_used)
        """
        start_time = time.time()

        try:
            logger.info(f"광고 문구 생성 시작 - 제품: {request.product_name}")

            # 이미지가 있으면 분석
            image_description = None
            if request.product_image_url:
                image_description = await self._analyze_image(request.product_image_url)

            # 프롬프트 생성
            system_prompt = self._build_system_prompt(request)
            user_prompt = self._build_user_prompt(request, image_description)

            logger.debug(f"시스템 프롬프트: {system_prompt[:200]}...")
            logger.debug(f"사용자 프롬프트: {user_prompt[:200]}...")

            # GPT API 호출
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.9,  # 창의성 높게
                max_tokens=2000,
                top_p=0.95,
                frequency_penalty=0.3,
                presence_penalty=0.3,
                response_format={"type": "json_object"}  # JSON 응답 강제
            )

            # 응답 파싱
            content = response.choices[0].message.content
            logger.debug(f"GPT 응답: {content[:500]}...")

            variations = self._parse_response(content, request.num_variations)

            # 요청한 개수만큼 없으면 로그 출력 (fallback 제거)
            if len(variations) < request.num_variations:
                logger.warning(f"생성된 문구 개수 부족: {len(variations)}/{request.num_variations}")

            generation_time = time.time() - start_time
            logger.info(f"광고 문구 생성 완료 - {len(variations)}개, {generation_time:.2f}초")

            return variations, generation_time, self.model

        except Exception as e:
            logger.exception(f"광고 문구 생성 실패: {str(e)}")
            raise


# 전역 서비스 인스턴스
openai_service = OpenAIService()
