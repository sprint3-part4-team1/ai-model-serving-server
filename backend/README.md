# 백엔드 API 서버 - 사용 가이드

## 🚀 빠른 시작

### 1. 가상 환경 생성 및 활성화

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`.env` 파일이 이미 설정되어 있습니다. OpenAI API 키가 포함되어 있습니다.

### 4. 서버 실행

```bash
# 개발 모드 (자동 리로드)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 9090

# 프로덕션 모드
python -m uvicorn app.main:app --host 0.0.0.0 --port 9090 --workers 4
```

### 5. API 문서 확인

서버 실행 후 브라우저에서:
- Swagger UI: http://localhost:9090/api/docs
- ReDoc: http://localhost:9090/api/redoc

---

## 📖 API 엔드포인트

### 광고 문구 생성

**POST /api/v1/ad-copy/generate**

```json
{
  "product_name": "수제 초콜릿 케이크",
  "product_description": "벨기에산 다크 초콜릿 사용",
  "tone": "emotional",
  "length": "short",
  "target_audience": "20-30대 여성",
  "platform": "Instagram",
  "num_variations": 3
}
```

**응답 시간**: 2-5초

### 텍스트→이미지 생성

**POST /api/v1/text-to-image/generate**

```json
{
  "prompt": "A delicious chocolate cake on a wooden table",
  "style": "realistic",
  "aspect_ratio": "1:1",
  "num_inference_steps": 50,
  "guidance_scale": 7.5,
  "num_images": 1
}
```

**응답 시간**: 15-30초 (GPU), 2-5분 (CPU)

### 배경 제거

**POST /api/v1/background/remove**

```json
{
  "image_url": "https://example.com/product.jpg",
  "return_mask": false
}
```

**응답 시간**: 2-5초

### 배경 교체

**POST /api/v1/background/replace**

```json
{
  "image_url": "https://example.com/product.jpg",
  "background_prompt": "wooden table background",
  "preserve_lighting": true
}
```

---

## 🧪 테스트

### API 테스트 스크립트 실행

```bash
python test_api.py
```

이 스크립트는 다음을 테스트합니다:
- 헬스 체크
- 광고 문구 생성
- 스타일 목록 조회
- (선택) 이미지 생성

### 수동 테스트 (curl)

```bash
# 헬스 체크
curl http://localhost:8000/health

# 광고 문구 생성
curl -X POST "http://localhost:8000/api/v1/ad-copy/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "라떼",
    "tone": "friendly",
    "length": "short",
    "num_variations": 2
  }'
```

---

## 📊 성능 가이드

### GPU 사용 (권장)

**요구사항**:
- NVIDIA GPU (8GB+ VRAM 권장)
- CUDA 11.8+
- cuDNN

**설치**:
```bash
# PyTorch with CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**성능**:
- 이미지 생성: 15-30초
- VRAM 사용: 8-12GB

### CPU 사용

**성능**:
- 이미지 생성: 2-5분
- RAM 사용: 16GB+ 권장

**설정**:
`.env` 파일에서:
```env
ENABLE_CPU_OFFLOAD=True
```

---

## 🎨 스타일 프리셋

1. **realistic** - 사실적인 제품 사진
2. **artistic** - 예술적 일러스트
3. **minimalist** - 미니멀 디자인
4. **vintage** - 빈티지 감성
5. **modern** - 현대적 세련됨
6. **colorful** - 화려한 색감

---

## 🔧 환경 변수 설명

### 필수
- `OPENAI_API_KEY` - OpenAI API 키 (이미 설정됨)

### 선택
- `DEBUG` - 디버그 모드 (True/False)
- `USE_XFORMERS` - 메모리 최적화 (True/False)
- `USE_HALF_PRECISION` - FP16 사용 (True/False)
- `DEFAULT_NUM_INFERENCE_STEPS` - 기본 생성 스텝 (20-100)

---

## 📁 디렉토리 구조

```
backend/
├── app/
│   ├── api/endpoints/    # API 엔드포인트
│   ├── core/            # 핵심 설정
│   ├── models/          # DB 모델
│   ├── schemas/         # Pydantic 스키마
│   ├── services/        # 비즈니스 로직
│   └── utils/           # 유틸리티
├── data/
│   ├── models/          # AI 모델 캐시
│   └── uploads/         # 생성된 이미지
├── logs/                # 로그 파일
├── requirements.txt     # 의존성
├── .env                # 환경 변수
└── test_api.py         # 테스트 스크립트
```

---

## 🐛 트러블슈팅

### CUDA out of memory

**해결책**:
1. `.env`에서 `USE_HALF_PRECISION=True` 확인
2. `USE_XFORMERS=True` 활성화
3. `DEFAULT_NUM_INFERENCE_STEPS` 줄이기 (50 → 30)
4. `num_images` 줄이기 (1개씩)

### 이미지 생성 느림

**해결책**:
1. GPU 사용 확인
2. CUDA 드라이버 업데이트
3. `num_inference_steps` 줄이기

### ImportError: No module named...

**해결책**:
```bash
pip install -r requirements.txt
```

---

## 📝 로그 확인

```bash
# 실시간 로그 확인
tail -f logs/app.log

# 에러 로그만 확인
tail -f logs/app_error.log
```

---

## 🔒 보안 주의사항

1. `.env` 파일 절대 공유 금지
2. OpenAI API 키 보호
3. 프로덕션에서 `DEBUG=False` 설정
4. CORS 설정 확인

---

## 📚 더 많은 정보

- API 문서: http://localhost:9090/api/docs
- 프로젝트 README: ../README.md
- 개발 과정: ../진행과정_기록.md

---
