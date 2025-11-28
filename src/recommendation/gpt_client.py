"""
GPT-5.1 API 클라이언트
OpenAI API를 통해 GPT-5.1과 통신하는 모듈
"""

import os
import json
from openai import OpenAI

from constants import (
    GPT_MODEL,
    DEFAULT_REASONING,
    DEFAULT_TEXT
)

class GPTClient:
    """GPT API 연동 클라이언트 (client.responses.create 스타일)"""

    def __init__(self, api_key=None, model="gpt-5-mini"):
        """
        GPT 클라이언트 초기화

        Args:
            api_key (str): OpenAI API 키 (없으면 환경변수에서 로드)
            model (str): 사용할 모델 (기본값: constants.GPT_MODEL)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or GPT_MODEL
        self.client = OpenAI(api_key=self.api_key)

    def create_response(self, input_text, reasoning=None, text=None):
        """
        GPT 응답 생성
        
        Args:
            input_text (str): 입력 프롬프트
            reasoning (dict): 추론 설정 (기본값: constants.DEFAULT_REASONING)
            text (dict): 텍스트 설정 (기본값: constants.DEFAULT_TEXT)
        
        Returns:
            str: GPT 응답 텍스트
        """
        reasoning = reasoning or DEFAULT_REASONING
        text = text or DEFAULT_TEXT

        try:
            response = self.client.responses.create(
                model=self.model,
                input=input_text,
                reasoning=reasoning,
                text=text,
            )
            return response.output_text

        except Exception as e:
            raise Exception(f"GPT API 호출 실패: {str(e)}")

    def parse_json_response(self, response_text):
        """
        GPT 응답을 JSON으로 파싱

        Args:
            response_text (str): GPT 응답 텍스트

        Returns:
            dict: 파싱된 JSON 객체
        """
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 파싱 실패: {str(e)}\n응답: {response_text}")


# 싱글톤 인스턴스 (전역에서 재사용)
_gpt_client_instance = None


def get_gpt_client():
    """GPT 클라이언트 싱글톤 인스턴스 반환"""
    global _gpt_client_instance
    if _gpt_client_instance is None:
        _gpt_client_instance = GPTClient()
    return _gpt_client_instance
