"""
GPT-5.1 API 클라이언트
OpenAI API를 통해 GPT-5.1과 통신하는 모듈
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()


class GPTClient:
    """GPT-5.1 API 연동 클라이언트 (client.responses.create 스타일)"""

    # 새로운 파라미터 구조를 위한 기본값 설정
    DEFAULT_REASONING = {"effort": "low"}
    DEFAULT_TEXT = {"verbosity": "low"}

    def __init__(self, api_key=None, model="gpt-5.1"):
        """
        GPT 클라이언트 초기화

        Args:
            api_key (str, optional): OpenAI API 키. None이면 환경변수에서 로드
            model (str): 사용할 모델 이름 (기본: gpt-5.1)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key가 설정되지 않았습니다. .env 파일을 확인하세요.")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def create_response(self, 
                        input_text: str, 
                        reasoning: dict = None, 
                        text: dict = None):
        """
        GPT-5.1 Responses API (client.responses.create) 호출

        기존의 messages 리스트 대신, 단일 input 문자열을 사용함! 
        
        Args:
            input_text (str): 모델에 전달할 프롬프트 텍스트. (기존 messages의 user/system 역할 병합 필요)
            reasoning (dict, optional): 추론 관련 설정 (e.g., {"effort": "high"})
            text (dict, optional): 텍스트 출력 관련 설정 (e.g., {"verbosity": "high"})

        Returns:
            str: GPT 응답 텍스트 (output_text)
        """
        try:
            _reasoning = reasoning if reasoning is not None else self.DEFAULT_REASONING
            _text = text if text is not None else self.DEFAULT_TEXT

            response = self.client.responses.create(
                model=self.model,
                input=input_text,
                reasoning=_reasoning,
                text=_text,
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


if __name__ == "__main__":
    # 테스트 코드
    client = get_gpt_client()
    test_input = "당신은 유용한 AI 어시스턴트입니다. 사용자에게 '안녕하세요! GPT-5.1 테스트 중입니다.'라는 인사에 대해 답변해 주세요."

    print("--- 1. 기본 응답 테스트 (effort: low, verbosity: low) ---")
    try:
        response_text = client.create_response(input_text=test_input)
        print(f"**GPT-5.1 응답**: {response_text}")
    except Exception as e:
        print(f"에러 발생: {e}")

    # JSON 응답 테스트
    print("\n--- 2. JSON 응답 테스트 ---")
    json_input = "간단한 JSON 객체를 만들어줘. 키는 'status' 값은 'ok'. 오직 JSON만 출력해."
    try:
        response_text_json = client.create_response(
            input_text=json_input,
            reasoning={"effort": "high"}, 
            text={"verbosity": "high"}
        )

        print(f"**GPT-5.1 JSON 원본 응답**: {response_text_json}")

        parsed = client.parse_json_response(response_text_json)
        print(f"**파싱된 JSON 객체**: {parsed}")
    except Exception as e:
        print(f"JSON 응답 테스트 에러 발생: {e}")