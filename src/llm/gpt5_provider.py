"""
GPT-5 Provider
"""
import os
from openai import OpenAI
from llm.base_provider import BaseLLMProvider

from constants import GPT5_MODEL, DEFAULT_REASONING, DEFAULT_TEXT


class GPT5Provider(BaseLLMProvider):
    """GPT-5 Provider"""

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = GPT5_MODEL
        self.client = OpenAI(api_key=self.api_key)

    def create_response(self, prompt: str, **kwargs) -> str:
        """GPT-5 응답 생성"""
        reasoning = kwargs.get('reasoning', DEFAULT_REASONING)
        text = kwargs.get('text', DEFAULT_TEXT)

        try:
            response = self.client.responses.create(
                model=self.model,
                input=prompt,
                reasoning=reasoning,
                text=text
            )
            return response.output_text
        
        except Exception as e:
            raise Exception(f"{GPT5_MODEL} API 호출 실패: {str(e)}")
        
    def get_model_name(self) -> str:
        return GPT5_MODEL
    
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
            "input": 0.00025,   # $0.00025 per 1K tokens
            "output": 0.002     # $0.002 per 1K tokens
        }