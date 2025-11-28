# Sprint 03 - AI Menu Generator

AI 기반 메뉴판 자동 생성 및 편집 시스템

## 프로젝트 개요

AI를 활용하여 메뉴판을 자동으로 생성하고, 기존 메뉴판을 OCR로 인식하여 편집할 수 있는 통합 시스템

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

## 기술 스택

### Frontend
- React 18 + TypeScript
- Vite (개발 서버)
- Material-UI (MUI)
- Zustand (상태 관리)

### Backend
- FastAPI + Python 3.10
- SQLAlchemy (ORM)
- MySQL (데이터베이스)
- PaddleOCR (텍스트 인식)
- Stable Diffusion (이미지 생성)
- OpenAI API (텍스트 생성)

### Infrastructure
- Server: GCP VM (34.28.223.101)
- Backend Port: 9090
- Frontend Port: 8030

## 프로젝트 구조

```
task/
├── backend/                          # FastAPI 백엔드
│   ├── app/
│   │   ├── api/endpoints/           # API 엔드포인트
│   │   │   ├── menu_generation.py  # AI 메뉴판 생성
│   │   │   ├── menu_ocr.py         # OCR/Repaint
│   │   │   └── menu.py             # 메뉴 CRUD
│   │   ├── models/                  # DB 모델
│   │   ├── schemas/                 # Pydantic 스키마
│   │   ├── services/                # 비즈니스 로직
│   │   └── core/                    # 설정, DB, 로깅
│   ├── data/                        # 데이터 저장소
│   │   └── uploads/                 # 업로드된 이미지
│   └── requirements.txt
│
├── frontend/                         # React 프론트엔드
│   ├── src/
│   │   ├── components/              # UI 컴포넌트
│   │   ├── pages/                   # 페이지
│   │   ├── services/                # API 클라이언트
│   │   └── store/                   # 상태 관리
│   ├── vite.config.ts               # Vite 설정
│   └── package.json
│
└── deployment/                       # 배포 설정 (현재 미사용)
    └── docker-compose.yml
```

## 실행 방법

### Backend 실행
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 9090
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
- API Docs: http://34.28.223.101:9090/docs

## API 명세

### 1. AI 메뉴판 생성
**POST** `/api/v1/menu-generation/generate`

#### Request
```json
{
  "store_id": 1,
  "categories": [
    {
      "category_name": "파스타",
      "items": [
        {
          "name": "까르보나라",
          "price": 15000,
          "ingredients": ["파스타면", "베이컨", "크림", "파마산 치즈"]
        }
      ]
    }
  ],
  "auto_generate_images": true,
  "auto_generate_descriptions": true
}
```

#### Response
```json
{
  "store_id": 1,
  "categories": [
    {
      "category_name": "파스타",
      "items": [
        {
          "name": "까르보나라",
          "description": "크리미한 크림소스와...",
          "price": 15000,
          "image_url": "/static/uploads/carbonara_123.jpg"
        }
      ]
    }
  ],
  "generation_time": 12.5
}
```

### 2. 메뉴판 OCR
**POST** `/api/v1/menu-ocr/ocr`

#### Request (multipart/form-data)
- `image`: 메뉴판 이미지 파일
- `crop_mode`: true/false
- `save_results`: true/false

#### Response
```json
{
  "ocr_id": "abc123",
  "schema_content": "# 카페 메뉴\n## 커피\n- 아메리카노: 4500원",
  "result_image_url": "/static/ocr_results/abc123/result_with_boxes.jpg",
  "extracted_images": ["/static/ocr_results/abc123/images/0.jpg"]
}
```

### 3. 메뉴판 재생성
**POST** `/api/v1/menu-ocr/repaint`

#### Request
```json
{
  "ocr_id": "abc123",
  "schema_content": "# 카페 메뉴\n## 커피\n- 아메리카노: 5000원"
}
```

### 4. 메뉴 아이템 업데이트
**PUT** `/api/v1/menu/items/{item_id}`

#### Request
```json
{
  "name": "수정된 메뉴명",
  "description": "수정된 설명",
  "price": 18000
}
```

## 이미지 저장 구조

- 실제 파일: `backend/data/uploads/`
- DB 저장: URL 경로만 (`/static/uploads/filename.jpg`)
- 접근 URL: `http://34.28.223.101:9090/static/uploads/filename.jpg`

## 개발 환경

- Python: 3.10
- Node.js: 18+
- MySQL: 8.0
- GCP VM: Ubuntu 20.04
