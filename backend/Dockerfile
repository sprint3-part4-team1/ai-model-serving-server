# 소상공인 광고 콘텐츠 생성 서비스 - Backend Dockerfile

# Python 3.10 베이스 이미지
FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필수 도구 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사 (app과 src 모두 복사)
COPY app /app/app
COPY src /app/src
COPY .env /app/.env

# 필요한 디렉토리 생성
RUN mkdir -p /app/data/models \
             /app/data/uploads \
             /app/data/static \
             /app/logs

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 포트 노출
EXPOSE 9091

# 헬스 체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:9091/health')"

# 서버 실행 - 새로운 entry point 사용
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "9091"]
