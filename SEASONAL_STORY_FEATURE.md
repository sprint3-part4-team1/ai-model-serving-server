# 시즈널 스토리 기능 (Feature #6)

**작성자**: 지민종
**작성일**: 2025-11-18

---

## 기능 개요

날씨, 계절, 시간대, 트렌드 등의 컨텍스트 정보를 기반으로 감성적인 추천 문구를 자동 생성하는 기능입니다.

---

## 파일 구조

```
src/
├── services/
│   ├── context_collector.py    # 컨텍스트 정보 수집 서비스
│   └── story_generator.py      # GPT 기반 스토리 생성 서비스
├── schemas/
│   └── seasonal_story.py        # API 요청/응답 스키마
├── api/
│   └── seasonal_story.py        # FastAPI 엔드포인트
├── config.py                    # 설정 파일
└── logger.py                    # 로깅 설정
```

---

## 기능 상세

### 1. Context Collector Service
- **실시간 날씨 정보** (OpenWeatherMap API)
- **계절 판단** (한국 기준)
- **시간대 분석** (아침/점심/오후/저녁/밤)
- **트렌드 수집** (선택적)

### 2. Story Generator Service
- **GPT-3.5-turbo 기반** 스토리 생성
- 컨텍스트를 반영한 감성적인 문구 작성
- 메뉴 클릭 시 스토리텔링 제공

---

## API 엔드포인트

### 1. POST /api/v1/seasonal-story/generate
시즈널 스토리 생성

**Request:**
```json
{
  "store_name": "서울카페",
  "store_type": "카페",
  "location": "Seoul",
  "menu_categories": ["커피", "디저트"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "story": "비 오는 가을 오후, 따뜻한 아메리카노 한 잔과 함께 여유를 느껴보세요.",
    "context": {
      "weather": {"condition": "rain", "temperature": 15.0},
      "season": "autumn",
      "time_info": {"period_kr": "오후"}
    }
  }
}
```

### 2. POST /api/v1/seasonal-story/menu-storytelling
메뉴 스토리텔링 생성

**Request:**
```json
{
  "menu_name": "아메리카노",
  "ingredients": ["에스프레소", "물"],
  "origin": "이탈리아",
  "history": "제2차 세계대전 중 미군이 에스프레소에 물을 타서 마신 것이 유래"
}
```

### 3. GET /api/v1/seasonal-story/context
현재 컨텍스트 정보 조회

---

## 환경 설정

### .env 파일 설정
```bash
# 필수
OPENAI_API_KEY=your_openai_api_key

# 선택 (없으면 Mock 데이터 사용)
OPENWEATHER_API_KEY=your_weather_api_key
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret
```

---

## 사용 예시

```python
from src.services.context_collector import context_collector_service
from src.services.story_generator import story_generator_service

# 1. 컨텍스트 수집
context = context_collector_service.get_full_context(location="Seoul")

# 2. 스토리 생성
story = story_generator_service.generate_story(
    context=context,
    store_name="서울카페",
    store_type="카페",
    menu_categories=["커피", "디저트"]
)

print(story)
# 출력: "맑은 가을 오후, 시원한 아이스 아메리카노와 함께 여유를 즐겨보세요."
```

---

## 테스트

```bash
# 의존성 설치
uv sync

# API 서버 실행 (main.py 필요)
uvicorn src.main:app --reload --port 8000

# 테스트 요청
curl -X POST "http://localhost:8000/api/v1/seasonal-story/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "store_name": "서울카페",
    "store_type": "카페",
    "location": "Seoul",
    "menu_categories": ["커피", "디저트"]
  }'
```

---

## 참고사항

- OpenWeatherMap API 키 없이도 작동 (Mock 데이터 사용)
- GPT-3.5-turbo 사용으로 비용 효율적
- 응답 시간: 2-4초 (캐싱 권장)

---

**문의**: 지민종
