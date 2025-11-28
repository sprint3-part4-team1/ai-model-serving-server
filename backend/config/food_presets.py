"""
음식 이미지 변환 프리셋 설정
MVP에서 사용할 옵션 기반 프리셋
"""
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class TransformPreset:
    """변환 프리셋 데이터 클래스"""
    name: str
    description: str
    prompt_template: str
    negative_prompt: str
    controlnet_type: str
    strength: float
    guidance_scale: float
    num_inference_steps: int
    size: tuple[int, int]
    additional_params: Dict[str, Any]


# ===== 변환 목적별 프리셋 =====

PURPOSE_PRESETS: Dict[str, TransformPreset] = {
    "banner_web": TransformPreset(
        name="웹 배너",
        description="SNS 커버, 웹사이트 배너용 (1920x1080)",
        prompt_template="{food_name}, wide angle shot, hero food photography, marketing banner style, "
                       "eye-catching composition, professional presentation, high-end restaurant quality, "
                       "vibrant colors, appetizing, commercial food photography",
        negative_prompt="blurry, low quality, bad composition, amateur, dark, unappetizing",
        controlnet_type="depth",
        strength=0.6,
        guidance_scale=7.5,
        num_inference_steps=30,
        size=(1920, 1080),
        additional_params={"aspect_ratio": "16:9"}
    ),

    "banner_sns": TransformPreset(
        name="SNS 포스트",
        description="인스타그램, 페이스북용 정사각형 (1080x1080)",
        prompt_template="{food_name}, square composition, instagram food photography, trendy food styling, "
                       "bright and colorful, social media ready, attractive plating, professional food shot",
        negative_prompt="blurry, low quality, bad lighting, unappealing",
        controlnet_type="canny",
        strength=0.65,
        guidance_scale=7.5,
        num_inference_steps=30,
        size=(1080, 1080),
        additional_params={"aspect_ratio": "1:1"}
    ),

    "product_emphasis": TransformPreset(
        name="제품 강조",
        description="제품 상세 페이지용, 클로즈업 (1024x1024)",
        prompt_template="{food_name}, product photography, close-up shot, studio lighting, clean background, "
                       "sharp focus on food, professional commercial photography, high detail, "
                       "appetizing presentation, food product shot",
        negative_prompt="blurry, cluttered background, poor lighting, low quality",
        controlnet_type="canny",
        strength=0.8,
        guidance_scale=8.0,
        num_inference_steps=35,
        size=(1024, 1024),
        additional_params={"focus": "product"}
    ),

    "background_change": TransformPreset(
        name="배경 변경",
        description="배경만 자연스럽게 교체",
        prompt_template="{food_name}, {background_style}, natural composition, "
                       "seamless background integration, professional food photography",
        negative_prompt="unnatural, poorly integrated, obvious editing, low quality",
        controlnet_type="depth",
        strength=0.5,
        guidance_scale=7.0,
        num_inference_steps=30,
        size=(1024, 1024),
        additional_params={"preserve_foreground": True}
    ),

    "color_correction": TransformPreset(
        name="색감 보정",
        description="더 먹음직스럽게 색감 개선",
        prompt_template="{food_name}, enhanced colors, vibrant and appetizing, "
                       "professional color grading, natural food colors, fresh and delicious looking",
        negative_prompt="oversaturated, unnatural colors, dull, unappealing",
        controlnet_type="canny",
        strength=0.4,
        guidance_scale=6.5,
        num_inference_steps=25,
        size=(1024, 1024),
        additional_params={"enhance_colors": True}
    ),

    "bw_to_color": TransformPreset(
        name="흑백→컬러",
        description="흑백 사진을 자연스러운 컬러로 복원",
        prompt_template="{food_name}, colorized photo, natural food colors, realistic colorization, "
                       "vibrant yet natural, professional food photography",
        negative_prompt="unnatural colors, oversaturated, poor colorization",
        controlnet_type="canny",
        strength=0.7,
        guidance_scale=8.0,
        num_inference_steps=40,
        size=(1024, 1024),
        additional_params={"colorize": True}
    ),
}


# ===== 스타일 프리셋 =====

STYLE_PRESETS: Dict[str, Dict[str, str]] = {
    "natural": {
        "name": "자연스러운 사진",
        "prompt_suffix": "natural lighting, realistic photo, everyday setting, casual photography",
        "description": "일상적이고 자연스러운 느낌"
    },

    "luxury": {
        "name": "고급 레스토랑",
        "prompt_suffix": "fine dining, luxury restaurant ambiance, elegant plating, sophisticated presentation, "
                        "high-end gastronomy, michelin star quality, refined atmosphere",
        "description": "고급스럽고 우아한 분위기"
    },

    "cafe": {
        "name": "카페 감성",
        "prompt_suffix": "cafe aesthetic, cozy coffee shop vibes, instagram worthy, trendy cafe style, "
                        "warm and inviting, modern cafe interior",
        "description": "따뜻하고 감성적인 카페 분위기"
    },

    "vintage": {
        "name": "빈티지 필름",
        "prompt_suffix": "vintage film photography, retro colors, analog camera aesthetic, nostalgic feel, "
                        "film grain, classic food photography",
        "description": "레트로하고 향수를 불러일으키는"
    },

    "bright": {
        "name": "밝고 화사하게",
        "prompt_suffix": "bright and airy, light and fresh, clean white tones, minimalist style, "
                        "fresh and vibrant, modern bright photography",
        "description": "밝고 깨끗한 느낌"
    },

    "rustic": {
        "name": "소박한 시골풍",
        "prompt_suffix": "rustic charm, farmhouse style, homemade feel, wooden textures, "
                        "country kitchen aesthetic, warm and cozy",
        "description": "따뜻하고 소박한 시골 분위기"
    },
}


# ===== 배경 프리셋 =====

BACKGROUND_PRESETS: Dict[str, Dict[str, str]] = {
    "original": {
        "name": "원본 유지",
        "prompt": "",
        "description": "배경 변경 없음",
        "remove_bg": False
    },

    "white": {
        "name": "깔끔한 흰색",
        "prompt": "clean white background, studio setting, minimal background, professional product shot",
        "description": "깨끗한 흰색 배경 (제품 사진용)",
        "remove_bg": True,
        "solid_color": (255, 255, 255)
    },

    "wood": {
        "name": "나무 테이블",
        "prompt": "wooden table background, natural wood texture, rustic wood surface, "
                 "cafe table, warm wood tones",
        "description": "자연스러운 나무 테이블",
        "remove_bg": False
    },

    "marble": {
        "name": "대리석",
        "prompt": "marble countertop, white marble surface, luxury marble background, "
                 "elegant stone texture, high-end kitchen",
        "description": "고급스러운 대리석",
        "remove_bg": False
    },

    "outdoor": {
        "name": "야외 자연광",
        "prompt": "outdoor natural lighting, garden setting, fresh air ambiance, "
                 "natural daylight, outdoor dining atmosphere",
        "description": "야외 자연광 분위기",
        "remove_bg": False
    },

    "remove": {
        "name": "배경 제거 (투명)",
        "prompt": "",
        "description": "배경을 완전히 제거하여 투명 PNG로",
        "remove_bg": True,
        "transparent": True
    },

    "bokeh": {
        "name": "흐린 배경 (보케)",
        "prompt": "bokeh background, shallow depth of field, blurred background, "
                 "professional photography bokeh, soft background blur",
        "description": "아웃포커스 효과",
        "remove_bg": False
    },
}


# ===== 음식 카테고리별 키워드 =====

FOOD_CATEGORIES: Dict[str, List[str]] = {
    "한식": ["korean food", "traditional korean cuisine", "hansik"],
    "양식": ["western cuisine", "european food", "american food"],
    "중식": ["chinese cuisine", "chinese food"],
    "일식": ["japanese cuisine", "japanese food", "washoku"],
    "디저트": ["dessert", "sweet treat", "pastry", "cake"],
    "베이커리": ["bread", "bakery", "baked goods", "pastry"],
    "음료": ["beverage", "drink", "coffee", "tea"],
    "패스트푸드": ["fast food", "burger", "pizza", "fried food"],
    "샐러드": ["salad", "healthy bowl", "fresh vegetables"],
    "스낵": ["snack", "appetizer", "finger food"],
}


# ===== 프롬프트 빌더 =====

class PromptBuilder:
    """프리셋 기반 프롬프트 생성기"""

    @staticmethod
    def build_prompt(
        purpose: str,
        style: str,
        background: str,
        food_name: str = "delicious food",
        additional_prompt: str = ""
    ) -> tuple[str, str]:
        """
        옵션 기반 프롬프트 생성

        Args:
            purpose: 변환 목적
            style: 스타일
            background: 배경
            food_name: 음식 이름
            additional_prompt: 추가 프롬프트

        Returns:
            (positive_prompt, negative_prompt)
        """
        # 기본 프롬프트 (목적)
        purpose_preset = PURPOSE_PRESETS.get(purpose, PURPOSE_PRESETS["product_emphasis"])
        base_prompt = purpose_preset.prompt_template.format(
            food_name=food_name,
            background_style=""
        )

        # 스타일 추가
        if style in STYLE_PRESETS:
            style_suffix = STYLE_PRESETS[style]["prompt_suffix"]
            base_prompt += f", {style_suffix}"

        # 배경 추가
        if background in BACKGROUND_PRESETS:
            bg_prompt = BACKGROUND_PRESETS[background]["prompt"]
            if bg_prompt:
                base_prompt += f", {bg_prompt}"

        # 추가 프롬프트
        if additional_prompt:
            base_prompt += f", {additional_prompt}"

        # 품질 키워드
        quality_keywords = "masterpiece, best quality, highly detailed, 8k, sharp focus, professional photography"
        positive_prompt = f"{base_prompt}, {quality_keywords}"

        # 네거티브 프롬프트
        negative_prompt = purpose_preset.negative_prompt

        return positive_prompt, negative_prompt

    @staticmethod
    def get_preset_config(purpose: str) -> TransformPreset:
        """목적에 따른 프리셋 설정 반환"""
        return PURPOSE_PRESETS.get(purpose, PURPOSE_PRESETS["product_emphasis"])

    @staticmethod
    def should_remove_background(background: str) -> bool:
        """배경 제거가 필요한지 확인"""
        if background not in BACKGROUND_PRESETS:
            return False
        return BACKGROUND_PRESETS[background].get("remove_bg", False)

    @staticmethod
    def get_solid_color(background: str) -> tuple[int, int, int] | None:
        """단색 배경 색상 반환"""
        if background not in BACKGROUND_PRESETS:
            return None
        return BACKGROUND_PRESETS[background].get("solid_color")

    @staticmethod
    def is_transparent_background(background: str) -> bool:
        """투명 배경인지 확인"""
        if background not in BACKGROUND_PRESETS:
            return False
        return BACKGROUND_PRESETS[background].get("transparent", False)


# 테스트용
if __name__ == "__main__":
    builder = PromptBuilder()

    # 테스트 케이스
    test_cases = [
        ("banner_web", "luxury", "marble", "grilled salmon steak"),
        ("product_emphasis", "natural", "white", "chocolate cake"),
        ("background_change", "cafe", "wood", "latte with latte art"),
    ]

    print("=== 프롬프트 빌더 테스트 ===\n")

    for purpose, style, background, food in test_cases:
        prompt, neg_prompt = builder.build_prompt(purpose, style, background, food)
        config = builder.get_preset_config(purpose)

        print(f"목적: {purpose} | 스타일: {style} | 배경: {background}")
        print(f"음식: {food}")
        print(f"\n프롬프트:\n{prompt}\n")
        print(f"네거티브:\n{neg_prompt}\n")
        print(f"설정: ControlNet={config.controlnet_type}, Strength={config.strength}, Steps={config.num_inference_steps}")
        print("=" * 100 + "\n")
