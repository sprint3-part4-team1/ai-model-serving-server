"""
LLM 실험 러너
동일 프롬프트로 여러 모델 실험 및 비교 분석
"""

import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from llm.gpt5_provider import GPT5Provider
from llm.gpt4_provider import GPT4Provider
from llm.gemini_provider import GeminiProvider
from llm.base_provider import BaseLLMProvider


class ExperimentRunner:
    """
    LLM 실험 러너
    - 동일 프롬프트로 여러 모델 실험
    - 응답 품질, 속도, 비용 비교
    - 결과 저장 및 분석
    """