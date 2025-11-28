"""
LLM Router
우선순위에 따라 모델 선택 및 Fallback 처리
"""

import time
from enum import Enum
from typing import Dict, Any, Optional
import json

from .gpt5_provider import GPT5Provider
from .gpt4_provider import GPT4Provider
from .gemini_provider import GeminiProvider


class ModelPriority(Enum):
    """모델 우선 순위"""
    PRIMARY = 1    # GPT-5.1
    SECONDARY = 2  # GPT-4.1
    TERTIARY = 3   # Gemini 2.5 Flash

class LLMRouter:
    """
    LLM 라우터
    - 우선순위에 따라 모델 선택
    - 자동 Fallback
    - 성능 메트릭 수집
    """

    def __init__(self):
        self.providers = {
            ModelPriority.PRIMARY: GPT5Provider(),
            ModelPriority.SECONDARY: GPT4Provider(),
            ModelPriority.TERTIARY: GeminiProvider()
        }
        self.metrics = [] # 성능 측정 데이터

    def create_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        우선순위에 따라 모델 호출
        실패 시 자동 Fallback
        
        Args:
            prompt (str): 입력 프롬프트
            **kwargs: 모델별 추가 파라미터
        
        Returns:
            dict: {
                "response": "LLM 응답",
                "model_used": "gpt-5-mini",
                "elapsed_time": 1.23,
                "success": True
            }
        """
        errors = []

        for priority in ModelPriority:
            provider = self.providers[priority]
            model_name = provider.get_model_name()

            # Health check
            if not provider.is_available():
                error_msg = f"{model_name} 사용 불가"
                print(f"⚠️ {error_msg}")
                errors.append(error_msg)
                continue

            try:
                print(f"🔄 {model_name} 호출 중...")
                start_time = time.time()

                response = provider.create_response(prompt, **kwargs)

                elapsed = time.time() - start_time

                # 메트릭 저장
                metric = {
                    "model": model_name,
                    "elapsed_time": elapsed,
                    "success": True,
                    "timestamp": time.time(),
                    "priority": priority.value
                }
                self.log_metric(metric)

                print(f"✅ {model_name} 응답 성공 ({elapsed:.2f}s)")

                return {
                    "response": response,
                    "model_used": model_name,
                    "elapsed_time": elapsed,
                    "success": True
                }
            
            except Exception as e:
                error_msg = f"{model_name} 실패: {str(e)}"
                print(f"❌ {error_msg}")
                errors.append(error_msg)

                # 실패 메트릭 저장
                self.log_metric({
                    "model": model_name,
                    "success": False,
                    "error": str(e),
                    "timestamp": time.time(),
                    "priority": priority.value
                })

                continue
                
        # 모든 모델 실패
        raise Exception(f"모든 LLM 모델 사용 불가. 에러: {errors}")
    
    def parse_json_response(self, response_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        LLM 응답을 JSON으로 파싱
        
        Args:
            response_dict: create_response()의 반환값
        
        Returns:
            dict: 파싱된 JSON + 메타데이터
        """
        response_text = response_dict['response']
        model_used = response_dict['model_used']

        # 사용한 provider로 파싱
        for provider in self.providers.values():
            if provider.get_model_name() == model_used:
                parsed = provider.parse_json_response(response_text)
                return {
                    "data": parsed,
                    "model_used": model_used,
                    "elapsed_time": response_dict['elapsed_time']
                }
        
        raise ValueError(f"Unknown model: {model_used}")
    
    def log_metric(self, metric: Dict[str, Any]):
        """성능 메트릭 저장"""
        self.metrics.append(metric)

    def get_performance_summary(self) -> Dict[str, Any]:
        """
        성능 요약 리포트

        Returns:
            dict: {
                "gpt-5-mini": {
                    "calls": 10,
                    "success_rate": 0.9,
                    "avg_time": 1.23
                },
                ...
            }
        """
        summary = {}

        for provider in self.providers.values():
            model_name = provider.get_model_name()
            model_metrics = [m for m in self.metrics if m['model'] == model_name]

            if not model_name:
                continue

            successful = [m for m in model_metrics if m.get('success', False)]

            summary[model_name] = {
                "total_calls": len(model_metrics),
                "successful_calls": len(successful),
                "success_rate": len(successful) / len(model_metrics) if model_metrics else 0,
                "avg_time": sum(m['elapsed_time'] for m in successful) / len(successful) if successful else 0,
                "cost_per_1k": provider.get_cost_per_1k_tokens()
            }

            return summary
        
    def save_metrics(self, filepath: str = "metrics.json"):
        """메트릭을 파일로 저장"""
        with open(filepath, 'w') as f:
            json.dump({
                "metrics": self.metrics,
                "summary": self.get_performance_summary()
            }, f, indent=2)
        print(f"📊 메트릭 저장: {filepath}")

# 싱글톤 인스턴스
_llm_router = None

def get_llm_router():
    """LLM 라우터 싱글톤 인스턴스 반환"""
    global _llm_router
    if _llm_router is None:
        _llm_router = LLMRouter()
    return _llm_router