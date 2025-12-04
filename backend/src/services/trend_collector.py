"""
Trend Collector Service
SNS, 실시간 검색어, 트렌드 키워드를 수집하는 서비스
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
import os

# 상대 경로로 import
from ..logger import app_logger as logger
from ..config import settings


class TrendCollectorService:
    """트렌드 수집 서비스"""

    def __init__(self):
        self.naver_client_id = settings.NAVER_CLIENT_ID
        self.naver_client_secret = settings.NAVER_CLIENT_SECRET
        self.cache = {}
        self.cache_ttl = 300  # 5분 캐시

    def get_trends(self, limit: int = 10, categories: List[str] = None) -> List[str]:
        """
        실시간 트렌드 키워드 수집 (통합)

        Args:
            limit: 가져올 트렌드 개수
            categories: 필터링할 카테고리 (예: ['food', 'weather', 'event'])

        Returns:
            트렌드 키워드 리스트
        """
        try:
            trends = []

            # 1. 네이버 실시간 검색어 (가능하면)
            naver_trends = self._get_naver_trends(limit=5)
            trends.extend(naver_trends)

            # 2. 웹 스크래핑 기반 트렌드 (백업)
            if len(trends) < limit:
                web_trends = self._get_web_trends(limit=limit - len(trends))
                trends.extend(web_trends)

            # 3. Mock 데이터 (최후의 수단)
            if len(trends) < limit:
                mock_trends = self._get_mock_trends(limit=limit - len(trends))
                trends.extend(mock_trends)

            # 카테고리 필터링
            if categories:
                trends = self._filter_by_category(trends, categories)

            # 중복 제거
            trends = list(dict.fromkeys(trends))

            logger.info(f"Collected {len(trends)} trends: {trends[:5]}")
            return trends[:limit]

        except Exception as e:
            logger.error(f"Failed to collect trends: {e}")
            return self._get_mock_trends(limit)

    def _get_naver_trends(self, limit: int = 5) -> List[str]:
        """
        네이버 검색 API를 통한 트렌드 수집

        Note: 네이버는 공식 실시간 검색어 API를 제공하지 않으므로
        검색량이 많은 키워드를 추론하는 방식 사용
        """
        if not self.naver_client_id or not self.naver_client_secret:
            return []

        try:
            # 캐시 확인
            cache_key = "naver_trends"
            if self._is_cache_valid(cache_key):
                return self.cache[cache_key]['data']

            # 음식/날씨 관련 일반 키워드로 검색
            base_keywords = ["맛집", "카페", "메뉴", "음료", "디저트"]
            trends = []

            url = "https://openapi.naver.com/v1/search/blog.json"
            headers = {
                "X-Naver-Client-Id": self.naver_client_id,
                "X-Naver-Client-Secret": self.naver_client_secret
            }

            for keyword in base_keywords[:2]:  # 2개만 조회 (API 할당량 고려)
                params = {
                    "query": keyword,
                    "display": 3,
                    "sort": "sim"
                }

                response = requests.get(url, headers=headers, params=params, timeout=3)

                if response.status_code == 200:
                    data = response.json()
                    # 블로그 제목에서 키워드 추출 (간단한 방식)
                    for item in data.get('items', []):
                        title = item.get('title', '')
                        # HTML 태그 제거
                        title = title.replace('<b>', '').replace('</b>', '')
                        trends.append(title.split()[0] if title else keyword)

            # 캐시 저장
            self.cache[cache_key] = {
                'data': trends[:limit],
                'timestamp': datetime.now()
            }

            return trends[:limit]

        except Exception as e:
            logger.warning(f"Failed to fetch Naver trends: {e}")
            return []

    def _get_web_trends(self, limit: int = 5) -> List[str]:
        """
        간단한 웹 기반 트렌드 추론
        (실제로는 공개 트렌드 API나 RSS 피드 활용)
        """
        try:
            # 예: 시간대별 인기 키워드
            hour = datetime.now().hour

            if 6 <= hour < 10:  # 아침
                return ["모닝커피", "아침식사", "브런치"]
            elif 10 <= hour < 14:  # 점심
                return ["점심메뉴", "런치세트", "샐러드"]
            elif 14 <= hour < 18:  # 오후
                return ["디저트", "아이스커피", "케이크"]
            elif 18 <= hour < 22:  # 저녁
                return ["저녁식사", "맥주", "치킨"]
            else:  # 밤
                return ["야식", "라면", "치킨"]

        except Exception as e:
            logger.warning(f"Failed to get web trends: {e}")
            return []

    def _get_mock_trends(self, limit: int = 5) -> List[str]:
        """계절/월별 Mock 트렌드 데이터"""
        now = datetime.now()
        month = now.month
        weekday = now.weekday()

        # 월별 트렌드
        monthly_trends = {
            1: ["신년", "따뜻한음료", "핫초코", "떡국"],
            2: ["발렌타인", "초콜릿", "겨울"],
            3: ["봄", "벚꽃", "피크닉", "봄나들이"],
            4: ["봄", "딸기", "새학기", "야외"],
            5: ["가정의달", "카네이션", "가족"],
            6: ["여름", "아이스커피", "빙수"],
            7: ["여름휴가", "바캉스", "수박", "시원한"],
            8: ["여름", "열대야", "아이스크림"],
            9: ["가을", "추석", "송편"],
            10: ["가을", "단풍", "할로윈"],
            11: ["가을", "추위", "따뜻한"],
            12: ["크리스마스", "연말", "겨울", "따뜻한"]
        }

        # 요일별 추가 트렌드
        weekday_trends = {
            0: ["월요병", "한주시작"],  # 월요일
            4: ["불금", "주말"],  # 금요일
            5: ["주말", "휴식"],  # 토요일
            6: ["일요일", "휴식"]  # 일요일
        }

        trends = monthly_trends.get(month, ["맛집", "카페", "음료"])

        # 요일 트렌드 추가
        if weekday in weekday_trends:
            trends = weekday_trends[weekday] + trends

        return trends[:limit]

    def _filter_by_category(self, trends: List[str], categories: List[str]) -> List[str]:
        """
        카테고리별 트렌드 필터링

        Args:
            trends: 트렌드 키워드 리스트
            categories: 카테고리 리스트 (['food', 'weather', 'event'])
        """
        # 카테고리별 키워드 매핑
        category_keywords = {
            'food': ['맛집', '음식', '메뉴', '디저트', '음료', '커피', '카페', '치킨', '피자'],
            'weather': ['날씨', '비', '눈', '추위', '더위', '맑음', '흐림'],
            'event': ['크리스마스', '설날', '추석', '할로윈', '발렌타인', '생일']
        }

        filtered = []
        for trend in trends:
            for category in categories:
                keywords = category_keywords.get(category, [])
                if any(keyword in trend for keyword in keywords):
                    filtered.append(trend)
                    break

        return filtered if filtered else trends  # 필터 결과 없으면 원본 반환

    def _is_cache_valid(self, key: str) -> bool:
        """캐시 유효성 검사"""
        if key not in self.cache:
            return False

        cache_time = self.cache[key]['timestamp']
        return (datetime.now() - cache_time).seconds < self.cache_ttl

    def get_trending_keywords_for_menu(
        self,
        menu_categories: List[str] = None,
        store_type: str = None
    ) -> List[str]:
        """
        메뉴 카테고리 및 매장 타입에 맞는 트렌딩 키워드 반환

        Args:
            menu_categories: 메뉴 카테고리 (예: ['커피', '디저트'])
            store_type: 매장 타입 (예: '카페', '레스토랑', '디저트', '술집')

        Returns:
            관련 트렌드 키워드
        """
        # 전체 트렌드 가져오기
        all_trends = self.get_trends(limit=20)

        # 1. 매장 타입별 부적합 트렌드 제거
        if store_type:
            all_trends = self._filter_by_store_type(all_trends, store_type)

        # 2. 메뉴 카테고리와 관련된 트렌드만 필터링
        if menu_categories:
            related_trends = []
            for trend in all_trends:
                for category in menu_categories:
                    if category in trend or any(word in trend for word in ['음료', '커피', '디저트', '음식']):
                        related_trends.append(trend)
                        break

            return related_trends[:5] if related_trends else all_trends[:5]

        return all_trends[:5]

    def _filter_by_store_type(self, trends: List[str], store_type: str) -> List[str]:
        """
        매장 타입별 부적합한 트렌드 제거

        Args:
            trends: 트렌드 키워드 리스트
            store_type: 매장 타입

        Returns:
            필터링된 트렌드 리스트
        """
        # 매장 타입별 제외 키워드
        exclude_keywords = {
            '카페': ['맥주', '소주', '술', '치킨', '삼겹살', '고기', '회', '주류', '양주', '와인'],
            '디저트': ['맥주', '소주', '술', '치킨', '삼겹살', '고기', '회', '주류', '양주', '와인'],
            '술집': ['커피', '아메리카노', '라떼', '카페', '케이크', '마카롱'],
            '레스토랑': []  # 레스토랑은 대부분 OK
        }

        # 제외 키워드 가져오기
        excludes = exclude_keywords.get(store_type, [])

        # 필터링
        filtered = []
        for trend in trends:
            # 제외 키워드가 포함되어 있는지 확인
            if not any(exclude in trend for exclude in excludes):
                filtered.append(trend)

        return filtered if filtered else trends  # 필터링 결과 없으면 원본 반환


# 싱글톤 인스턴스
trend_collector_service = TrendCollectorService()


# 테스트 함수
if __name__ == "__main__":
    service = TrendCollectorService()

    print("=== 전체 트렌드 ===")
    trends = service.get_trends(limit=10)
    print(trends)

    print("\n=== 음식 관련 트렌드 ===")
    food_trends = service.get_trends(limit=10, categories=['food'])
    print(food_trends)

    print("\n=== 메뉴별 트렌드 ===")
    menu_trends = service.get_trending_keywords_for_menu(['커피', '디저트'])
    print(menu_trends)
