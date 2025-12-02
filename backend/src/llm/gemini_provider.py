"""
Gemini 2.5 Flash Provider
"""

import os
import google.generativeai as genai
from .base_provider import BaseLLMProvider
from ..constants import GEMINI_MODEL


class GeminiProvider(BaseLLMProvider):
    """Gemini Provider"""

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GENINI_API_KEY")
        self.model = GEMINI_MODEL
        self.client = genai.Client(api_key=self.api_key)

    def create_response(self, prompt, **kwargs) -> str:
        """Gemini 응답 생성"""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            return response.text
        
        except Exception as e:
            raise Exception(f"{GEMINI_MODEL} API 호출 실패: {str(e)}")
        
    def get_model_name(self) -> str:
        return GEMINI_MODEL
    
    def is_available(self) -> bool:
        """Health check"""
        try:
            # 간단한 테스트 요청
            response = self.client.models.generate_content(
                model=self.model,
                contents="test"
            )
            return True
        except:
            return False
        
    def get_cost_per_1k_tokens(self) -> dict:
        """비용 정보"""
        return{
            "input": 0.0003,   # $0.0003 per 1K tokens
            "output": 0.0025   # $0.0025 per 1K tokens
        }
