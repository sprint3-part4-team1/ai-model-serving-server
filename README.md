# AI Model Serving Server - ValueUp

AI 기반 메뉴판 자동 생성 및 편집, 시즈널 스토리 생성, 메뉴 추천 통합 시스템

## 프로젝트 개요

소상공인을 위한 AI 기반 통합 서비스:
- **메뉴판 생성**: AI로 메뉴 이미지와 설명 자동 생성
- **메뉴판 OCR**: 기존 메뉴판 인식 및 재생성
- **시즈널 스토리**: 매장별 계절 스토리 생성
- **메뉴 추천**: LLM 기반 고객 맞춤 메뉴 추천

## 주요 기능

### 1. AI 메뉴판 생성 (`/api/v1/menu-generation`)
- 메뉴 이름, 재료, 가격 입력만으로 메뉴판 자동 생성
- AI 기반 메뉴 이미지 자동 생성 (Stable Diffusion)
- AI 기반 메뉴 설명 자동 생성 (OpenAI)
- 카테고리별 메뉴 그룹핑
- 매장별 메뉴 데이터 저장 및 재사용

### 2. 메뉴판 OCR/재생성 (`/api/v1/menu-ocr`)
- 기존 메뉴판 이미지에서 텍스트 추출 (PaddleOCR)
- 메뉴 구조 자동 파싱 (제목, 항목, 가격)
- 추출한 스키마로 메뉴판 이미지 재생성
- 메뉴 내용 수정 후 재생성 가능

### 3. 메뉴 편집 (`/api/v1/menu`)
- 메뉴 아이템 추가/수정/삭제
- 메뉴 이미지 업로드
- 매장별 메뉴 조회

### 4. 시즈널 스토리 생성
- 매장 유형별 계절 스토리 생성
- Google & Instagram 트렌드 수집
- 컨텍스트 기반 스토리 생성

### 5. 메뉴 추천 시스템
- LLM 기반 메뉴 추천 (GPT-4, GPT-5, Gemini)
- 영양성분 분석
- 고객 의도 파싱

## 기술 스택

### Frontend
- React 18 + TypeScript
- Vite (개발 서버)
- Material-UI (MUI)
- Zustand (상태 관리)

### Backend
- **FastAPI** (메뉴 생성, OCR, 이미지 생성)
- **Flask** (시즈널 스토리, 추천 시스템)
- SQLAlchemy (ORM)
- MySQL (데이터베이스)
- PaddleOCR (텍스트 인식)
- Stable Diffusion (이미지 생성)
- OpenAI API (텍스트 생성)

### Infrastructure
- Server: GCP VM (34.28.223.101)
- Backend Port: 9090
- Frontend Port: 8030

## 환경설정

### UV 환경설정 (추천 시스템)
```bash
uv python install 3.12
uv init -p 3.12 --bare
uv add langchain langchain-openai
uv add dotenv sqlalchemy pymysql flask
```

### Python 환경설정 (메뉴 생성)
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 실행 방법

### Backend 실행 (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 9090
```

### Backend 실행 (Flask - 추천 시스템)
```bash
uv run src/app.py
```

### Frontend 실행
```bash
cd frontend
npm install
npm run dev  # http://localhost:8030
```

### 접속 정보
- Frontend: http://34.28.223.101:8030
- Backend API: http://34.28.223.101:9090
- API Docs (FastAPI): http://34.28.223.101:9090/docs
- API Docs (Flask): http://127.0.0.1:9090/docs

## 이미지 저장 구조

- 실제 파일: `backend/data/uploads/`
- DB 저장: URL 경로만 (`/static/uploads/filename.jpg`)
- 접근 URL: `http://34.28.223.101:9090/static/uploads/filename.jpg`

## 개발 환경

- Python: 3.10, 3.12
- Node.js: 18+
- MySQL: 8.0
- GCP VM: Ubuntu 20.04
