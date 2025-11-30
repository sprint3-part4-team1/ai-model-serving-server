#!/bin/bash

# AI Model Serving Server - GCP VM 배포 스크립트
# GitHub: https://github.com/sprint3-part4-team1/ai-model-serving-server

set -e  # 에러 발생 시 스크립트 중단

echo "=========================================="
echo "AI Model Serving Server 배포 시작"
echo "=========================================="

# 1. .env 파일 확인
echo ""
echo "📋 Step 1: .env 파일 확인"
if [ ! -f "backend/.env" ]; then
    echo "⚠️  backend/.env 파일이 없습니다."
    if [ -f "backend/.env.example" ]; then
        echo "📝 .env.example을 복사합니다..."
        cp backend/.env.example backend/.env
        echo "⚠️  backend/.env 파일을 열어서 API 키를 설정해주세요!"
        echo "   - OPENAI_API_KEY"
        echo "   - DATABASE_URL (필요시)"
        echo ""
        read -p "계속하려면 Enter를 누르세요..."
    else
        echo "❌ backend/.env.example 파일도 없습니다."
        exit 1
    fi
else
    echo "✅ backend/.env 파일 확인됨"
fi

# 2. 기존 컨테이너 중지 및 제거
echo ""
echo "🛑 Step 2: 기존 컨테이너 중지"
if docker ps -a | grep -q ai-backend; then
    echo "기존 컨테이너를 중지하고 제거합니다..."
    docker stop ai-backend 2>/dev/null || true
    docker rm ai-backend 2>/dev/null || true
    echo "✅ 기존 컨테이너 제거 완료"
else
    echo "✅ 기존 컨테이너 없음"
fi

# 3. 필요한 디렉토리 생성
echo ""
echo "📁 Step 3: 필요한 디렉토리 생성"
mkdir -p backend/data/uploads
mkdir -p backend/data/static
mkdir -p backend/data/models
mkdir -p backend/logs
echo "✅ 디렉토리 생성 완료"

# 4. Docker Compose로 빌드 및 실행
echo ""
echo "🐳 Step 4: Docker 이미지 빌드 및 컨테이너 실행"
docker-compose up -d --build

# 5. 컨테이너 상태 확인
echo ""
echo "⏳ Step 5: 서버 시작 대기 중..."
sleep 10

# 6. 헬스 체크
echo ""
echo "🏥 Step 6: 헬스 체크"
for i in {1..30}; do
    if curl -f http://localhost:9091/health > /dev/null 2>&1; then
        echo "✅ 서버가 정상적으로 실행중입니다!"
        break
    else
        if [ $i -eq 30 ]; then
            echo "❌ 서버 시작 실패. 로그를 확인하세요:"
            echo "   docker-compose logs backend"
            exit 1
        fi
        echo "   대기 중... ($i/30)"
        sleep 2
    fi
done

# 7. 배포 완료
echo ""
echo "=========================================="
echo "✅ 배포 완료!"
echo "=========================================="
echo ""
echo "🌐 서버 정보:"
echo "   - 로컬: http://localhost:9091"
echo "   - API 문서: http://localhost:9091/docs"
echo "   - 헬스 체크: http://localhost:9091/health"
echo ""
echo "📊 유용한 명령어:"
echo "   - 로그 확인: docker-compose logs -f backend"
echo "   - 컨테이너 상태: docker-compose ps"
echo "   - 컨테이너 중지: docker-compose down"
echo "   - 컨테이너 재시작: docker-compose restart"
echo ""
echo "🔥 방화벽 설정 확인:"
echo "   - GCP 방화벽에서 9091 포트가 열려있는지 확인하세요"
echo ""
