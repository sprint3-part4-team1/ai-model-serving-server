# 시즈널 스토리 기능 벨류업 (Feature #6 Enhanced)

**작성자**: 지민종
**일자**: 2025-11-18

---

## 🚀 추가된 벨류업 기능

### 1️⃣ 실시간 SNS 트렌드 수집

**파일**: `src/services/trend_collector.py`

#### 기능 설명
- 네이버 검색 API 연동으로 실시간 트렌드 수집
- 시간대별 자동 트렌드 분석 (아침/점심/오후/저녁/밤)
- 메뉴 카테고리별 관련 트렌드 필터링
- 5분 캐싱으로 API 호출 최적화

#### 사용 예시
```python
from src.services.trend_collector import trend_collector_service

# 전체 트렌드
trends = trend_collector_service.get_trends(limit=10)

# 음식 관련 트렌드만
food_trends = trend_collector_service.get_trends(categories=['food'])

# 메뉴별 맞춤 트렌드
menu_trends = trend_collector_service.get_trending_keywords_for_menu(['커피', '디저트'])
```

#### 실제 적용 예시
```
컨텍스트: 가을 저녁, 비 옴, 트렌드: ["단풍", "추석", "불금"]
생성 문구: "비 오는 불금 저녁, 따뜻한 아메리카노와 함께 단풍 구경 어떠세요?"
```

---

### 2️⃣ 브랜드 톤앤매너 차별화

**파일**: `src/services/story_generator.py` (129-135번 라인)

#### 매장 타입별 톤 차별화
- **카페**: "친근하고 따뜻한 톤" (예: ~어떠세요?, ~해보세요)
- **레스토랑**: "품격있고 전문적인 톤" (예: ~어떻습니까?, ~만들어보세요)
- **디저트**: "발랄하고 달콤한 톤" (예: ~즐겨봐요!, ~느껴보세요)
- **술집**: "편안하고 캐주얼한 톤" (예: ~어때요?, ~함께해요)

#### 비교 예시
```
[카페] "비 오는 오후, 따뜻한 라떼 한 잔 어떠세요?"
[레스토랑] "비 오는 오후, 특별한 요리로 여유를 만들어보세요."
[디저트] "비 오는 오후, 달콤한 케이크로 기분 전환 해봐요!"
```

---

### 3️⃣ A/B 테스트 기능 (다중 버전 생성)

**API**: `POST /api/v1/seasonal-story/generate-variants`

#### 기능 설명
- 동일한 컨텍스트로 3가지 버전의 스토리 동시 생성
- GPT의 temperature 파라미터로 다양성 확보
- 효과적인 문구 선택 가능

#### API 요청 예시
```bash
curl -X POST "http://localhost:8000/api/v1/seasonal-story/generate-variants" \
  -H "Content-Type: application/json" \
  -d '{
    "store_name": "서울카페",
    "store_type": "카페",
    "location": "Seoul",
    "menu_categories": ["커피", "디저트"]
  }'
```

#### 응답 예시
```json
{
  "success": true,
  "data": {
    "stories": [
      {
        "variant": "Version 1",
        "story": "비 오는 가을 저녁, 따뜻한 아메리카노와 함께 여유를 느껴보세요."
      },
      {
        "variant": "Version 2",
        "story": "가을비가 내리는 저녁, 진한 커피 한 잔으로 하루를 마무리하세요."
      },
      {
        "variant": "Version 3",
        "story": "비 내리는 이 순간, 아메리카노로 특별한 가을 감성을 느껴보세요."
      }
    ],
    "context": {...}
  }
}
```

---

### 4️⃣ 향상된 프롬프트 엔지니어링

**파일**: `src/services/story_generator.py` (148-176번 라인)

#### 개선사항
- 트렌드 키워드 자동 통합 지시
- Few-shot 예시 4개 → 실제 트렌드 활용 예시 포함
- 문장 길이 50자 → 60자로 확장
- 억지스럽지 않은 트렌드 활용 가이드

#### 프롬프트 예시
```
**🔥 트렌드 활용 (필수):**
- 현재 인기 키워드: 단풍, 불금, 추석
- 위 트렌드 중 1-2개를 자연스럽게 문구에 녹여내세요
- 억지로 끼워넣지 말고, 맥락에 맞게 활용
- 예: "요즘 인기인 단풍와 함께 커피 어떠세요?"
```

---

## 📊 성능 비교

| 항목 | 기존 | 벨류업 후 |
|------|------|-----------|
| 트렌드 수집 | Mock 데이터 only | 실시간 API + Mock 백업 |
| 브랜드 톤 | 단일 톤 | 4가지 매장 타입별 차별화 |
| 스토리 버전 | 1개 | 3개 (A/B 테스트) |
| 프롬프트 품질 | 기본 | 고급 (Few-shot + 트렌드) |
| API 엔드포인트 | 3개 | 4개 (variants 추가) |

---

## 🎯 비즈니스 임팩트

### 1. 고객 경험 향상
- 실시간 트렌드 반영으로 **공감도 ↑**
- 브랜드별 맞춤 톤으로 **일관성 ↑**

### 2. 운영 효율성
- A/B 테스트로 **효과적인 문구 선택**
- 자동 캐싱으로 **API 비용 절감**

### 3. 데이터 기반 개선
- 다중 버전으로 **클릭률 비교 가능**
- 효과적인 패턴 학습

---

## 📝 사용 가이드

### 기본 스토리 생성
```bash
POST /api/v1/seasonal-story/generate
{
  "store_name": "서울카페",
  "store_type": "카페",
  "location": "Seoul",
  "menu_categories": ["커피", "디저트"]
}
```

### A/B 테스트용 다중 생성
```bash
POST /api/v1/seasonal-story/generate-variants
{
  "store_name": "서울카페",
  "store_type": "레스토랑",  # 톤이 달라짐!
  "location": "Seoul",
  "menu_categories": ["메인요리", "디저트"]
}
```

---

## 🔧 필요한 환경 변수

```env
# 필수
OPENAI_API_KEY=your_openai_key

# 선택 (없으면 Mock 데이터 사용)
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret
```

---

## 📌 다음 단계 (선택)

- [ ] Redis 캐싱 구현 (성능 최적화)
- [ ] Google Trends API 추가 연동
- [ ] 클릭률 추적 시스템 구축
- [ ] 개인화 (고객 이력 기반)

---

**문의**: 지민종
**GitHub**: jmj 브랜치
