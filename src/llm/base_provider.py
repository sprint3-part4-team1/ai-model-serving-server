"""
LLM Provider 추상 클래스
모든 LLM Provider가 구현해야 하는 인터페이스
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseLLMProvider(ABC):
    """LLM Provider 기본 인터페이스"""
    
    @abstractmethod
    def create_response(self, prompt: str, **kwargs) -> str:
        """
        LLM 응답 생성
        
        Args:
            prompt (str): 입력 프롬프트
            **kwargs: 추가 파라미터 (reasoning, text 등)
        
        Returns:
            str: LLM 응답 텍스트
        """

        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """
        모델 이름 반환
        
        Returns:
            str: 모델 이름 (예: "gpt-5-mini")
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        서비스 가용성 체크
        
        Returns:
            bool: 사용 가능 여부
        """
        pass
    
    @abstractmethod
    def get_cost_per_1k_tokens(self) -> Dict[str, float]:
        """
        토큰당 비용 반환
        
        Returns:
            dict: {"input": 0.0001, "output": 0.0002}
        """
        pass

    def parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        JSON 응답 파싱 (공통 로직)
        
        Args:
            response_text (str): LLM 응답 텍스트
        
        Returns:
            dict: 파싱된 JSON
        """
        import json

        try:
            triple_backtick = "```"

            if triple_backtick + "json" in response_text:
                # ```json ... ```
                parts = response_text.split(triple_backtick + "json", 1)
                if len(parts) > 1:
                    # 뒤쪽에서 다시 ``` 기준으로 잘라냄
                    response_text = parts[1].split(triple_backtick, 1)[0].strip()

            elif triple_backtick in response_text:
                # ``` ... ```
                parts = response_text.split(triple_backtick)
                if len(parts) >= 2:
                    # 두 번째 부분이 코드 블록 내용
                    response_text = parts[1].strip()

            return json.loads(response_text)
        
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 파싱 실패: {str(e)}\n응답: {response_text}")


