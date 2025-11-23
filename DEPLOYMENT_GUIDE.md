# 배포 가이드

**작성자**: 지민종
**작성일**: 2025-11-18

---

## 🚀 GCP 서버에 배포하기

### 배포 정보
- **API 서버**: http://34.28.223.101:8002/api/v1
- **API 문서**: http://34.28.223.101:8002/codeit-team1-api-docs
- **Streamlit**: http://34.28.223.101:8003/

---

## 📋 방법 1: GitHub을 통한 배포 (권장)

### 1. 로컬에서 Git Commit

```bash
# 변경사항 확인
git status

# 제가 추가한 파일들만 커밋
git add backend/app/services/context_collector.py
git add backend/app/services/story_generator.py
git add backend/app/schemas/seasonal_story.py
git add backend/app/api/endpoints/seasonal_story.py
git add backend/app/core/config.py
git add backend/requirements.txt
git add backend/.env

# 커밋
git commit -m "feat: Add seasonal story feature

- Add context collector service (weather, season, time)
- Add story generator service (GPT-based)
- Add seasonal story API endpoints
- Update config and requirements"

# Push
git push origin jmj
```

### 2. GCP VM에서 Pull (노준혁님께 요청)

```bash
# SSH 접속
ssh {username}@34.28.223.101

# 프로젝트 디렉토리로 이동
cd /path/to/project

# Pull
git pull origin jmj

# 라이브러리 설치
cd backend
pip install -r requirements.txt

# 서버 재시작
# (기존 프로세스 종료 후)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 &
```

### 3. 배포 확인

```bash
# 헬스 체크
curl http://34.28.223.101:8002/health

# 시즈널 스토리 API 확인
curl http://34.28.223.101:8002/api/v1/seasonal-story/health
```

---

## 📋 방법 2: 파일만 전달 (간단)

### 1. 추가된 파일 목록

```
backend/app/services/
├── context_collector.py      # 신규
└── story_generator.py        # 신규

backend/app/schemas/
└── seasonal_story.py         # 신규

backend/app/api/endpoints/
└── seasonal_story.py         # 신규

backend/app/core/
└── config.py                 # 수정 (3줄 추가)

backend/app/
└── main.py                   # 수정 (1줄 추가)

backend/
└── requirements.txt          # 수정 (라이브러리 추가)
```

### 2. 수정된 부분만 알려주기

**config.py (30-32줄 추가)**:
```python
# Seasonal Story API Keys
OPENWEATHER_API_KEY: str = "YOUR_API_KEY_HERE"
NAVER_CLIENT_ID: str = ""
NAVER_CLIENT_SECRET: str = ""
```

**main.py (189줄 수정)**:
```python
from app.api.endpoints import ad_copy, text_to_image, background, seasonal_story
...
app.include_router(seasonal_story.router, prefix="/api/v1/seasonal-story", tags=["시즈널 스토리"])
```

**requirements.txt (추가)**:
```
requests==2.31.0
pytz==2023.3
beautifulsoup4==4.12.2
lxml==4.9.3
pymysql==1.1.0
cryptography==41.0.7
compel==2.0.2
```

### 3. 노준혁님께 전달

팀 채팅에 다음과 같이 공유:

```
@노준혁님
시즈널 스토리 기능 개발 완료했습니다!

추가된 파일:
- backend/app/services/context_collector.py
- backend/app/services/story_generator.py
- backend/app/schemas/seasonal_story.py
- backend/app/api/endpoints/seasonal_story.py

수정된 파일:
- backend/app/core/config.py (3줄 추가)
- backend/app/main.py (1줄 추가)
- backend/requirements.txt (라이브러리 추가)

GCP 서버에 배포 부탁드립니다!
자세한 내용은 DEPLOYMENT_GUIDE.md 참고해주세요.
```

---

## 📋 방법 3: 직접 배포 (GCP 접근 권한 있는 경우)

### 1. SSH 접속

```bash
ssh yjy@34.28.223.101
# 또는
ssh {본인_계정}@34.28.223.101
```

### 2. 프로젝트 디렉토리 확인

```bash
# 프로젝트 위치 찾기
find / -name "app" -type d 2>/dev/null | grep backend

# 또는 노준혁님께 경로 문의
```

### 3. 파일 업로드

```bash
# 로컬에서 (새 터미널)
scp backend/app/services/context_collector.py yjy@34.28.223.101:/path/to/backend/app/services/
scp backend/app/services/story_generator.py yjy@34.28.223.101:/path/to/backend/app/services/
scp backend/app/schemas/seasonal_story.py yjy@34.28.223.101:/path/to/backend/app/schemas/
scp backend/app/api/endpoints/seasonal_story.py yjy@34.28.223.101:/path/to/backend/app/api/endpoints/
```

### 4. 라이브러리 설치

```bash
# SSH 접속된 상태에서
cd /path/to/backend
pip install requests==2.31.0 pytz==2023.3 beautifulsoup4==4.12.2 lxml==4.9.3 pymysql==1.1.0 cryptography==41.0.7 compel==2.0.2
```

### 5. 서버 재시작

```bash
# 기존 프로세스 확인
ps aux | grep uvicorn

# 종료
kill -9 {PID}

# 재시작
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 &
```

---

## ✅ 배포 확인

### 1. API 문서 확인
http://34.28.223.101:8002/codeit-team1-api-docs

**시즈널 스토리** 섹션이 보여야 함:
- POST /api/v1/seasonal-story/generate
- POST /api/v1/seasonal-story/menu-storytelling
- GET /api/v1/seasonal-story/context
- GET /api/v1/seasonal-story/health

### 2. API 테스트

```bash
# 헬스 체크
curl http://34.28.223.101:8002/api/v1/seasonal-story/health

# 컨텍스트 조회
curl http://34.28.223.101:8002/api/v1/seasonal-story/context?location=Seoul

# 스토리 생성
curl -X POST http://34.28.223.101:8002/api/v1/seasonal-story/generate \
  -H "Content-Type: application/json" \
  -d '{"store_name":"서울카페","store_type":"카페","location":"Seoul","menu_categories":["커피","디저트"]}'
```

---

## 🔑 환경 변수 설정

GCP 서버의 `.env` 파일에 다음 추가 필요:

```bash
# 시즈널 스토리 생성용 API Keys
OPENWEATHER_API_KEY=YOUR_API_KEY_HERE
NAVER_CLIENT_ID=
NAVER_CLIENT_SECRET=
```

**OpenWeatherMap API 키 발급**: https://openweathermap.org/api

---

## 🎯 권장 배포 순서

1. **지금**: 노준혁님께 파일 전달 및 배포 요청
2. **다음**: API 테스트 및 확인
3. **이후**: 프론트엔드 연동 (김지영님, 노준혁님)

---

## 💡 팀원과 공유할 URL

배포 후 팀원들에게 공유:

- **API 문서**: http://34.28.223.101:8002/codeit-team1-api-docs
- **사용 가이드**: `SEASONAL_STORY_README.md`
- **작업 보고서**: `WORK_COMPLETION_REPORT.md`

---

**작성자**: 지민종
**배포 담당**: 노준혁님
