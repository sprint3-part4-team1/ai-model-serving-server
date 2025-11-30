# 🍽️ AI 메뉴 추천 시스템

GPT-5.1 기반의 자연어 메뉴 추천 시스템입니다.

## 📋 프로젝트 개요

고객이 자연어로 요청하면 AI가 의도를 파악하여 최적의 메뉴를 추천합니다.

### 주요 기능
- 🤖 GPT-5.1 기반 자연어 이해
- 🔍 영양소 기반 필터링 (칼로리, 단백질, 카페인, 당분)
- 📊 스마트 정렬 알고리즘
- 💬 친근한 추천 문구 자동 생성
- 💾 JSON/MySQL 듀얼 데이터 소스 지원

## 🚀 설치 방법

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
`.env` 파일을 생성하고 다음 내용을 입력하세요:

```env
# Python Path
PYTHONPATH=./src

# MySQL Database
DB_USER=your-username
DB_PASSWORD=your-password
DB_HOST=34.28.223.101
DB_PORT=8004
DB_NAME=codeit_team1

# OpenAI API Key
OPENAI_API_KEY=sk-proj-your-api-key-here
```

## 💻 사용 방법

### 메인 프로그램 실행
```bash
python main.py
```

### 사용 예시
```
무엇을 찾고 계신가요?

👤 당신: 칼로리 낮은 음료 추천해줘

🤖 AI가 요청을 분석 중...
✅ 분석 완료: 칼로리가 낮은 음료를 찾으시는군요!

🔍 메뉴 검색 중...
✅ 7개의 메뉴를 찾았습니다.

============================================================
🎯 추천 메뉴
============================================================

[1] 아메리카노 - 4,000원
    진한 원두 향의 커피
    📊 5kcal | 단백질 0.5g | 당분 0g
    💡 칼로리가 거의 없어서 다이어트 중에도 부담 없이 즐기실 수 있어요!

[2] 카푸치노 - 4,500원
    우유 거품이 올라간 커피
    📊 120kcal | 단백질 6.0g | 당분 9.0g
    💡 우유가 들어가지만 여전히 칼로리가 낮은 편이고, 단백질도 보충할 수 있어요!

[3] 자몽 에이드 - 6,000원
    상큼한 자몽 탄산음료
    📊 140kcal | 단백질 1.0g | 당분 28.0g
    💡 상큼한 맛으로 기분 전환하기 좋고, 비타민도 풍부해요!

============================================================
```

## 📁 프로젝트 구조

```
menu-recommendation/
├── samples/
│   └── menu_sample_data_v2.json        # 샘플 데이터 (dev/테스트 전용)
├── src/
│   ├── database.py
│   └── recommendation/
│        ├── gpt_client.py
│        ├── intent_parser.py
│        ├── recommendation.py
│        ├── data_loader.py
│        ├── utils.py
│        ├── recommendation_service.py  # 진입점(API)
│        └── recommendation_cli.py      # 대화형 CLI
├── tests/
│   └── test_recommendation.py
├── main.py                             # 메인 라우터 (파트 진입점)
├── TEAM_GUIDE.md                       # 팀원통합 사용법
├── pyproject.toml                      # (uv/PEP621)
└── README.md                           # 이 파일

```

## 🔧 기술 스택

- **Python 3.12**
- **GPT-5.1 API** (OpenAI)
- **SQLAlchemy** (ORM)
- **PyMySQL** (MySQL 드라이버)
- **python-dotenv** (환경 변수 관리)

## 📊 데이터베이스 스키마

### Tables
- `stores`: 매장 정보
- `menus`: 메뉴판
- `menu_items`: 메뉴 아이템
- `item_ingredients`: 재료 정보
- `nutrition_estimates`: AI 영양소 추정치

## 🧪 테스트

```bash
pytest tests/
```

## 👥 팀원

- **본인**: 고객 요청 기반 추천 시스템
- **팀원 B**: 메뉴 클릭 시 영양 성분 + 스토리텔링
- **팀원 C**: 시즈널/이벤트 스토리 확장
- **팀원 D**: 접속 단계 테마 자동 생성

## 📝 라이선스

팀 프로젝트 (Codeit Team 1)

## 🔗 참고 자료

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
