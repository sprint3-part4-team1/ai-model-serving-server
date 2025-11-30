"""
GPT-4 Provider
"""

import os
from openai import OpenAI
from .base_provider import BaseLLMProvider
from ..constants import GPT4_MODEL

class GPT4Provider(BaseLLMProvider):
    """GPT-4 Provider"""

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = GPT4_MODEL
        self.client = OpenAI(api_key=self.api_key)

    def create_response(self, prompt, **kwargs) -> str:
        """GPT-4.1 응답 생성"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 1000)
            )
            return response.choices[0].message.content
        
        except Exception as e:
            raise Exception(f"{GPT4_MODEL} API 호출 실패: {str(e)}")
        
    def get_model_name(self) -> str:
        return GPT4_MODEL
    
    def is_available(self) -> bool:
        """Health check"""
        try:
            self.client.models.list()
            return True
        except:
            return False
        
    def get_cost_per_1k_tokens(self) -> dict:
        """비용 정보"""
        return {
            "input": 0.002, # $0.002 per 1K tokens
            "output": 0.008 # $0.008 per 1K tokens
        }