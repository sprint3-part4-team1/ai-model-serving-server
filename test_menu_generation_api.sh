#!/bin/bash

# 메뉴 생성 API 테스트 스크립트

echo "========================================="
echo "메뉴 생성 API 테스트"
echo "========================================="

# 1. 헬스 체크
echo ""
echo "1. 헬스 체크..."
curl -X GET "http://localhost:9091/api/v1/menu-generation/health"
echo ""

# 2. 매장 생성 (테스트용)
echo ""
echo "2. 테스트 매장 생성..."
STORE_RESPONSE=$(curl -s -X POST "http://localhost:9091/api/v1/menu/store" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "테스트 카페",
    "address": "서울시 강남구",
    "phone": "02-1234-5678"
  }')

echo $STORE_RESPONSE | jq '.'
STORE_ID=$(echo $STORE_RESPONSE | jq -r '.data.id')
echo "생성된 매장 ID: $STORE_ID"

# 3. 메뉴판 생성 (이미지 생성 OFF로 빠른 테스트)
echo ""
echo "3. 메뉴판 생성 (매장 ID: $STORE_ID)..."
MENU_RESPONSE=$(curl -s -X POST "http://localhost:9091/api/v1/menu-generation/generate" \
  -H "Content-Type: application/json" \
  -d "{
    \"store_id\": $STORE_ID,
    \"categories\": [
      {
        \"category_name\": \"커피\",
        \"items\": [
          {
            \"name\": \"아메리카노\",
            \"price\": 4000
          },
          {
            \"name\": \"카페라떼\",
            \"price\": 4500
          }
        ]
      }
    ],
    \"auto_generate_images\": false,
    \"auto_generate_descriptions\": true
  }")

echo $MENU_RESPONSE | jq '.'

# 4. DB 확인 - 매장의 메뉴 조회
echo ""
echo "4. DB 확인 - 생성된 메뉴 조회..."
curl -s -X GET "http://localhost:9091/api/v1/menu/store/$STORE_ID" | jq '.'

echo ""
echo "========================================="
echo "테스트 완료!"
echo "========================================="
echo ""
echo "만약 메뉴가 조회되면 → DB 저장 성공 ✅"
echo "만약 메뉴가 조회 안 되면 → DB 저장 실패 ❌"
echo ""
