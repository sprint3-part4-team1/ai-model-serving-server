"""
Context Collector Service
날씨, 계절, 시간대, SNS 트렌드 등의 컨텍스트 정보를 수집하는 서비스
"""

import os
import requests
import time
from datetime import datetime
from typing import Dict, Optional, List
import pytz
from pytrends.request import TrendReq
from app.core.logging import app_logger as logger
from app.core.config import settings


class ContextCollectorService:
    """컨텍스트 정보 수집 서비스"""

    def __init__(self):
        self.openweather_api_key = settings.OPENWEATHER_API_KEY
        self.naver_client_id = settings.NAVER_CLIENT_ID
        self.naver_client_secret = settings.NAVER_CLIENT_SECRET
        self.instagram_access_token = settings.INSTAGRAM_ACCESS_TOKEN
        self.instagram_business_account_id = settings.INSTAGRAM_BUSINESS_ACCOUNT_ID

        # 한국 시간대
        self.korea_tz = pytz.timezone('Asia/Seoul')

        # Google Trends 독립 캐시 (10분 유지)
        self._google_trends_cache = {}
        self._google_trends_cache_time = {}
        self._google_trends_cache_ttl = 600  # 10분 (초 단위)

        # Instagram Trends 독립 캐시 (30분 유지 - API 제한 고려)
        self._instagram_trends_cache = {}
        self._instagram_trends_cache_time = {}
        self._instagram_trends_cache_ttl = 1800  # 30분 (초 단위)

    def get_full_context(
        self,
        location: str = "Seoul",
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        include_all_trends: bool = True,
        store_type: str = "카페"
    ) -> Dict:
        """
        전체 컨텍스트 정보 수집

        Args:
            location: 위치 이름 (예: "Seoul", "Busan")
            lat: 위도 (선택)
            lon: 경도 (선택)
            include_all_trends: 모든 트렌드 소스를 분리하여 반환할지 여부
            store_type: 매장 타입 (카페, 중국집, 한식당 등)

        Returns:
            전체 컨텍스트 정보
        """
        logger.info(f"Collecting context for location: {location}, store_type: {store_type}")

        # 날씨 정보 수집
        weather = self.get_weather(location, lat, lon)

        # 계절 판단
        season = self.get_season()

        # 시간대 판단
        time_info = self.get_time_info()

        # 트렌드 수집
        if include_all_trends:
            # 모든 소스의 트렌드를 분리하여 수집 (매장 타입 기반)
            all_trends = self.get_all_trends(store_type=store_type)
            trends = all_trends.get("primary", [])  # 기본 트렌드 (하위 호환성)
        else:
            trends = self.get_trends()
            all_trends = None

        context = {
            "weather": weather,
            "season": season,
            "time_info": time_info,
            "trends": trends,
            "location": location,
            "timestamp": datetime.now(self.korea_tz).isoformat()
        }

        # 모든 트렌드 소스 정보 추가
        if all_trends:
            context["google_trends"] = all_trends.get("google", [])
            context["instagram_trends"] = all_trends.get("instagram", [])

        logger.info(f"Context collected successfully: {context}")
        return context

    def get_weather(
        self,
        location: str = "Seoul",
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> Dict:
        """
        OpenWeatherMap API를 통해 날씨 정보 수집

        Args:
            location: 도시 이름
            lat: 위도 (우선순위)
            lon: 경도 (우선순위)

        Returns:
            날씨 정보 딕셔너리
        """
        if not self.openweather_api_key or self.openweather_api_key == "YOUR_API_KEY_HERE":
            logger.warning("OpenWeatherMap API key not configured, returning mock data")
            return self._get_mock_weather()

        try:
            base_url = "https://api.openweathermap.org/data/2.5/weather"

            # 위도/경도가 주어진 경우 우선 사용
            if lat and lon:
                params = {
                    "lat": lat,
                    "lon": lon,
                    "appid": self.openweather_api_key,
                    "units": "metric",  # 섭씨 온도
                    "lang": "kr"  # 한국어
                }
            else:
                params = {
                    "q": location,
                    "appid": self.openweather_api_key,
                    "units": "metric",
                    "lang": "kr"
                }

            response = requests.get(base_url, params=params, timeout=5)
            response.raise_for_status()

            data = response.json()

            weather_info = {
                "condition": data["weather"][0]["main"].lower(),  # "rain", "clear", "clouds", etc.
                "description": data["weather"][0]["description"],  # "비", "맑음" 등
                "temperature": round(data["main"]["temp"], 1),
                "feels_like": round(data["main"]["feels_like"], 1),
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"]
            }

            logger.info(f"Weather data retrieved: {weather_info}")
            return weather_info

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch weather data: {e}")
            return self._get_mock_weather()
        except Exception as e:
            logger.error(f"Unexpected error in get_weather: {e}")
            return self._get_mock_weather()

    def _get_mock_weather(self) -> Dict:
        """Mock 날씨 데이터 (테스트용)"""
        return {
            "condition": "clear",
            "description": "맑음",
            "temperature": 15.0,
            "feels_like": 13.0,
            "humidity": 60,
            "wind_speed": 2.5
        }

    def get_season(self) -> str:
        """
        현재 계절 판단 (한국 기준)

        Returns:
            "spring", "summer", "autumn", "winter"
        """
        now = datetime.now(self.korea_tz)
        month = now.month

        if 3 <= month <= 5:
            season = "spring"
        elif 6 <= month <= 8:
            season = "summer"
        elif 9 <= month <= 11:
            season = "autumn"
        else:  # 12, 1, 2월
            season = "winter"

        logger.info(f"Current season: {season} (month: {month})")
        return season

    def get_time_info(self) -> Dict:
        """
        현재 시간대 정보

        Returns:
            시간대 정보 딕셔너리
        """
        now = datetime.now(self.korea_tz)
        hour = now.hour

        # 시간대 구분
        if 6 <= hour < 10:
            period = "morning"
            period_kr = "아침"
        elif 10 <= hour < 14:
            period = "lunch"
            period_kr = "점심"
        elif 14 <= hour < 18:
            period = "afternoon"
            period_kr = "오후"
        elif 18 <= hour < 22:
            period = "evening"
            period_kr = "저녁"
        else:  # 22-6시
            period = "night"
            period_kr = "밤"

        time_info = {
            "period": period,
            "period_kr": period_kr,
            "hour": hour,
            "minute": now.minute,
            "time_str": now.strftime("%H:%M"),
            "date": now.strftime("%Y-%m-%d"),
            "weekday": now.strftime("%A"),
            "weekday_kr": self._get_korean_weekday(now.weekday())
        }

        logger.info(f"Time info: {time_info}")
        return time_info

    def _get_korean_weekday(self, weekday: int) -> str:
        """요일을 한국어로 변환"""
        weekdays = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
        return weekdays[weekday]

    def get_all_trends(self, limit: int = 20, store_type: str = "카페") -> Dict[str, List[str]]:
        """
        모든 트렌드 소스를 분리하여 수집

        Args:
            limit: 각 소스별로 가져올 트렌드 개수 (기본값: 20)

        Returns:
            소스별 트렌드 딕셔너리
            {
                "google": [...],
                "naver": [...],
                "instagram": [...],
                "primary": [...]  # 우선순위가 가장 높은 트렌드
            }
        """
        current_time = time.time()
        logger.info(f"Fetching all trends from multiple sources for store type: {store_type}")

        # 1. Google Trends 수집 (독립적 캐싱 + 에러 격리)
        google_trends = []
        try:
            # 캐시 확인
            cache_key = f"google_{store_type}"
            cached_time = self._google_trends_cache_time.get(cache_key)

            if cached_time and (current_time - cached_time < self._google_trends_cache_ttl):
                google_trends = self._google_trends_cache.get(cache_key, [])
                logger.info(f"Using cached Google Trends for {store_type}: {len(google_trends)} items")
            else:
                # 새로 수집
                google_trends = self._get_google_trends(limit, store_type)
                # 캐시 저장
                self._google_trends_cache[cache_key] = google_trends
                self._google_trends_cache_time[cache_key] = current_time
                logger.info(f"Fetched Google Trends for {store_type}: {len(google_trends)} items")
        except Exception as e:
            logger.error(f"Failed to fetch Google Trends: {e}")
            google_trends = []

        # 2. Instagram Trends 수집 (독립적 캐싱 + 에러 격리)
        instagram_trends = []
        try:
            # 캐시 확인
            cache_key = f"instagram_{store_type}"
            cached_time = self._instagram_trends_cache_time.get(cache_key)

            if cached_time and (current_time - cached_time < self._instagram_trends_cache_ttl):
                instagram_trends = self._instagram_trends_cache.get(cache_key, [])
                logger.info(f"Using cached Instagram Trends for {store_type}: {len(instagram_trends)} items")
            else:
                # 새로 수집
                instagram_trends = self._get_instagram_trends(limit, store_type)
                # 캐시 저장
                self._instagram_trends_cache[cache_key] = instagram_trends
                self._instagram_trends_cache_time[cache_key] = current_time
                logger.info(f"Fetched Instagram Trends for {store_type}: {len(instagram_trends)} items")
        except Exception as e:
            logger.error(f"Failed to fetch Instagram Trends: {e}")
            instagram_trends = []

        # 3. 우선순위 결정
        if google_trends:
            primary = google_trends
        elif instagram_trends:
            primary = instagram_trends
        else:
            primary = self._get_mock_trends(limit)

        result = {
            "google": google_trends,
            "instagram": instagram_trends,
            "primary": primary
        }

        logger.info(f"All trends collected - Google: {len(google_trends)}, Instagram: {len(instagram_trends)}")
        return result

    def get_trends(self, limit: int = 5) -> List[str]:
        """
        SNS 트렌드 수집 (Google Trends, Naver API, Instagram Graph API 기반)

        캐시를 사용하여 30분마다 한 번씩만 API를 호출합니다.

        Args:
            limit: 가져올 트렌드 개수

        Returns:
            트렌드 키워드 리스트
        """
        import time

        # 캐시 확인
        current_time = time.time()
        if (self._trends_cache is not None and
            self._trends_cache_time is not None and
            current_time - self._trends_cache_time < self._trends_cache_ttl):
            logger.info(f"Using cached trends: {self._trends_cache[:limit]}")
            return self._trends_cache[:limit]

        # 캐시가 없거나 만료됨 - 새로 가져오기
        logger.info("Trends cache expired or empty, fetching new trends...")

        # 1순위: Google Trends
        google_trends = self._get_google_trends(limit)
        if google_trends:
            logger.info(f"Google trends collected: {google_trends}")
            self._trends_cache = google_trends
            self._trends_cache_time = current_time
            return google_trends

        # 2순위: Naver Trends API
        naver_trends = self._get_naver_trends(limit)
        if naver_trends:
            logger.info(f"Naver trends collected: {naver_trends}")
            self._trends_cache = naver_trends
            self._trends_cache_time = current_time
            return naver_trends

        # 3순위: Instagram Graph API
        instagram_trends = self._get_instagram_trends(limit)
        if instagram_trends:
            logger.info(f"Instagram trends collected: {instagram_trends}")
            self._trends_cache = instagram_trends
            self._trends_cache_time = current_time
            return instagram_trends

        # Fallback: Mock 트렌드
        logger.warning("Using mock trends as fallback")
        mock_trends = self._get_mock_trends(limit)
        self._trends_cache = mock_trends
        self._trends_cache_time = current_time
        return mock_trends

    def _get_instagram_trends(self, limit: int = 20, store_type: str = "카페") -> List[str]:
        """
        Instagram Graph API를 통한 트렌드 수집 (매장 타입별)

        Instagram Graph API는 공개 트렌딩 해시태그를 제공하지 않으므로,
        매장 타입과 계절에 맞는 해시태그의 활동성을 측정하여 반환

        Args:
            limit: 가져올 트렌드 개수 (기본값: 20)
            store_type: 매장 타입

        Returns:
            트렌드 키워드 리스트
        """
        if not self.instagram_access_token or self.instagram_access_token == "YOUR_ACCESS_TOKEN_HERE":
            logger.warning("Instagram access token not configured")
            return []

        if not self.instagram_business_account_id:
            logger.warning("Instagram business account ID not configured")
            return []

        logger.info(f"Fetching Instagram trends with account ID: {self.instagram_business_account_id}")

        try:
            # 매장 타입별 + 계절별 해시태그 생성
            season = self.get_season()
            store_keywords = self._get_store_season_keywords(store_type, season)

            # 일반적인 음식/카페 해시태그 추가
            general_hashtags = [
                "맛집", "맛스타그램", "먹스타그램", "오늘의메뉴",
                "데일리", "일상", "foodstagram", "instafood",
                "cafestagram", "foodie", "yummy", "delicious",
                "koreanfood", "kfood", "서울맛집", "강남맛집"
            ]

            # 매장 타입 키워드 + 일반 해시태그 조합 (rate limit 방지를 위해 개수 제한)
            candidate_hashtags = store_keywords[:5] + general_hashtags[:3]

            hashtag_scores = []

            # 각 해시태그의 최근 미디어 개수 측정
            for hashtag in candidate_hashtags:
                try:
                    # Instagram Graph API - Hashtag ID 검색
                    search_url = f"https://graph.facebook.com/v18.0/ig_hashtag_search"
                    search_params = {
                        "user_id": self.instagram_business_account_id,
                        "q": hashtag,
                        "access_token": self.instagram_access_token
                    }

                    search_response = requests.get(search_url, params=search_params, timeout=5)

                    if search_response.status_code != 200:
                        logger.warning(f"Instagram hashtag search failed for '{hashtag}': Status {search_response.status_code}, Response: {search_response.text[:200]}")
                        continue

                    search_data = search_response.json()

                    if not search_data.get("data"):
                        logger.debug(f"No data found for hashtag '{hashtag}': {search_data}")
                        continue

                    hashtag_id = search_data["data"][0]["id"]

                    # Hashtag의 최근 미디어 개수 조회
                    media_url = f"https://graph.facebook.com/v18.0/{hashtag_id}/recent_media"
                    media_params = {
                        "user_id": self.instagram_business_account_id,
                        "fields": "id",
                        "limit": 1,
                        "access_token": self.instagram_access_token
                    }

                    media_response = requests.get(media_url, params=media_params, timeout=5)

                    if media_response.status_code == 200:
                        # 해시태그가 활성화되어 있으면 점수 부여
                        hashtag_scores.append({
                            "tag": hashtag,
                            "score": 1  # 실제로는 미디어 개수나 engagement를 측정할 수 있음
                        })

                    # Rate limit 방지를 위한 지연
                    time.sleep(0.5)

                except Exception as e:
                    logger.warning(f"Failed to check hashtag '{hashtag}': {e}")
                    continue

            # 점수 순으로 정렬하여 상위 트렌드 반환
            if hashtag_scores:
                sorted_hashtags = sorted(hashtag_scores, key=lambda x: x["score"], reverse=True)
                trends = [item["tag"] for item in sorted_hashtags[:limit]]
                logger.info(f"Instagram trends found: {trends}")
                return trends

            logger.warning("No Instagram trends found")
            return []

        except Exception as e:
            logger.error(f"Failed to fetch Instagram trends: {e}")
            return []

    def _get_store_season_keywords(self, store_type: str, season: str) -> List[str]:
        """
        매장 타입과 계절에 맞는 키워드 생성

        Args:
            store_type: 매장 타입 (카페, 중국집, 한식당, 일식당, 양식당, 분식집, 치킨집, 디저트카페 등)
            season: 계절 (spring, summer, autumn, winter)

        Returns:
            해당 매장 타입과 계절에 맞는 키워드 리스트
        """
        # 매장 타입별 기본 키워드 (확장)
        store_base_keywords = {
            "카페": ["카페", "커피", "디저트", "베이커리", "브런치", "케이크", "라떼"],
            "중국집": ["중국집", "짜장면", "짬뽕", "탕수육", "양장피", "깐풍기", "볶음밥"],
            "한식당": ["한식", "백반", "찌개", "된장찌개", "김치찌개", "비빔밥", "불고기"],
            "일식당": ["일식", "초밥", "우동", "라멘", "돈부리", "사시미", "덮밥"],
            "양식당": ["양식", "파스타", "스테이크", "피자", "리조또", "샐러드", "그라탕"],
            "분식집": ["분식", "떡볶이", "김밥", "라면", "튀김", "순대", "오뎅"],
            "치킨집": ["치킨", "후라이드", "양념치킨", "간장치킨", "마늘치킨", "치맥"],
            "디저트카페": ["디저트", "케이크", "마카롱", "타르트", "크로플", "와플", "빙수"],
            "베이커리": ["빵", "베이글", "크루아상", "샌드위치", "페이스트리", "도넛"],
            "술집": ["술집", "맥주", "소주", "안주", "치맥", "포차", "이자카야"],
            # 추가 매장 타입
            "피자": ["피자", "피자집", "치즈", "토핑", "파스타", "샐러드", "치킨"],
            "햄버거": ["햄버거", "버거", "감자튀김", "패스트푸드", "세트메뉴", "음료"],
            "아시아음식": ["쌀국수", "팟타이", "태국음식", "베트남음식", "아시안", "분짜"],
            "멕시칸": ["타코", "부리또", "나초", "살사", "멕시칸", "케사디아"],
            "고기집": ["고기집", "삼겹살", "소고기", "구이", "BBQ", "숯불"],
            "회": ["회", "횟집", "회덮밥", "광어", "연어", "참치", "초밥"]
        }

        # 계절별 추가 키워드
        seasonal_keywords = {
            "spring": ["봄", "벚꽃", "딸기", "새싹", "봄나물", "봄나들이", "피크닉"],
            "summer": ["여름", "시원한", "빙수", "냉면", "수박", "아이스", "시원"],
            "autumn": ["가을", "단풍", "호박", "밤", "고구마", "따뜻한", "감"],
            "winter": ["겨울", "따뜻한", "군밤", "붕어빵", "호떡", "어묵", "국물"]
        }

        # 매장 타입별 + 계절별 조합 키워드
        combined_keywords = {
            ("카페", "spring"): ["벚꽃카페", "딸기라떼", "봄카페", "봄디저트", "벚꽃케이크"],
            ("카페", "summer"): ["빙수", "아이스커피", "아이스라떼", "여름카페", "시원한카페"],
            ("카페", "autumn"): ["가을카페", "단풍카페", "호박라떼", "밤케이크", "고구마라떼"],
            ("카페", "winter"): ["따뜻한커피", "겨울카페", "핫초코", "따뜻한차", "크리스마스카페"],

            ("중국집", "spring"): ["봄짜장", "짬뽕", "탕수육", "군만두", "볶음밥"],
            ("중국집", "summer"): ["냉짬뽕", "냉짜장", "차가운짬뽕", "시원한중식", "짬뽕"],
            ("중국집", "autumn"): ["얼큰짬뽕", "짬뽕", "짜장면", "탕수육", "중식"],
            ("중국집", "winter"): ["따뜻한짬뽕", "얼큰짬뽕", "국물요리", "중국집", "짬뽕"],

            ("한식당", "spring"): ["봄나물", "봄비빔밥", "쌈밥", "봄한정식", "봄백반"],
            ("한식당", "summer"): ["냉국", "콩국수", "열무국수", "시원한국물", "냉한식"],
            ("한식당", "autumn"): ["갈비찜", "불고기", "김치찌개", "된장찌개", "한식"],
            ("한식당", "winter"): ["국밥", "해장국", "삼계탕", "갈비탕", "따뜻한국물"],

            ("일식당", "spring"): ["봄초밥", "벚꽃초밥", "봄회", "사시미", "일식"],
            ("일식당", "summer"): ["냉우동", "소바", "냉소바", "시원한일식", "초밥"],
            ("일식당", "autumn"): ["라멘", "따뜻한우동", "돈부리", "일식", "초밥"],
            ("일식당", "winter"): ["라멘", "우동", "따뜻한국물", "일식", "돈부리"],

            ("양식당", "spring"): ["봄샐러드", "봄파스타", "봄요리", "양식", "파스타"],
            ("양식당", "summer"): ["시원한샐러드", "냉파스타", "샐러드", "양식", "파스타"],
            ("양식당", "autumn"): ["크림파스타", "따뜻한파스타", "리조또", "양식", "스테이크"],
            ("양식당", "winter"): ["크림파스타", "따뜻한수프", "그라탕", "양식", "스테이크"],

            ("분식집", "spring"): ["떡볶이", "김밥", "봄소풍", "분식", "튀김"],
            ("분식집", "summer"): ["냉떡볶이", "시원한김밥", "분식", "떡볶이", "라면"],
            ("분식집", "autumn"): ["떡볶이", "김밥", "오뎅", "분식", "라면"],
            ("분식집", "winter"): ["따뜻한떡볶이", "국물떡볶이", "오뎅", "분식", "어묵"],

            ("치킨집", "spring"): ["치킨", "후라이드", "양념치킨", "치맥", "봄치킨"],
            ("치킨집", "summer"): ["치맥", "시원한맥주", "치킨", "여름치맥", "후라이드"],
            ("치킨집", "autumn"): ["치킨", "양념치킨", "치맥", "가을치킨", "후라이드"],
            ("치킨집", "winter"): ["따뜻한치킨", "치킨", "치맥", "후라이드", "양념치킨"],

            ("디저트카페", "spring"): ["딸기디저트", "봄디저트", "벚꽃디저트", "딸기케이크", "마카롱"],
            ("디저트카페", "summer"): ["빙수", "시원한디저트", "아이스크림", "여름디저트", "젤라토"],
            ("디저트카페", "autumn"): ["호박디저트", "밤디저트", "가을디저트", "고구마케이크", "타르트"],
            ("디저트카페", "winter"): ["따뜻한디저트", "크리스마스케이크", "겨울디저트", "핫초코", "케이크"],

            # 추가 매장 타입
            ("피자", "spring"): ["봄피자", "봄샐러드", "피자", "치즈피자", "파스타"],
            ("피자", "summer"): ["시원한피자", "피자", "샐러드피자", "치즈피자", "음료"],
            ("피자", "autumn"): ["피자", "치즈피자", "고구마피자", "따뜻한피자", "파스타"],
            ("피자", "winter"): ["따뜻한피자", "치즈피자", "피자", "핫윙", "파스타"],

            ("햄버거", "spring"): ["햄버거", "버거", "감자튀김", "세트메뉴", "봄버거"],
            ("햄버거", "summer"): ["시원한버거", "아이스음료", "햄버거", "감자튀김", "세트"],
            ("햄버거", "autumn"): ["햄버거", "버거", "감자튀김", "세트메뉴", "치즈버거"],
            ("햄버거", "winter"): ["따뜻한버거", "햄버거", "핫커피", "감자튀김", "세트"],

            ("아시아음식", "spring"): ["쌀국수", "팟타이", "분짜", "월남쌈", "아시안"],
            ("아시아음식", "summer"): ["시원한쌀국수", "월남쌈", "팟타이", "아시안", "베트남"],
            ("아시아음식", "autumn"): ["쌀국수", "팟타이", "똠양꿍", "아시안", "태국음식"],
            ("아시아음식", "winter"): ["따뜻한쌀국수", "팟타이", "똠양꿍", "아시안", "베트남"],

            ("멕시칸", "spring"): ["타코", "부리또", "나초", "살사", "멕시칸"],
            ("멕시칸", "summer"): ["시원한타코", "나초", "부리또", "멕시칸", "살사"],
            ("멕시칸", "autumn"): ["타코", "부리또", "케사디아", "나초", "멕시칸"],
            ("멕시칸", "winter"): ["따뜻한부리또", "타코", "케사디아", "멕시칸", "나초"],

            ("고기집", "spring"): ["고기", "삼겹살", "봄고기", "BBQ", "구이"],
            ("고기집", "summer"): ["시원한맥주", "삼겹살", "고기", "냉면", "구이"],
            ("고기집", "autumn"): ["고기", "삼겹살", "소고기", "구이", "BBQ"],
            ("고기집", "winter"): ["따뜻한고기", "삼겹살", "소고기", "구이", "BBQ"],

            ("회", "spring"): ["봄회", "봄초밥", "사시미", "광어", "연어"],
            ("회", "summer"): ["시원한회", "사시미", "회덮밥", "광어", "연어"],
            ("회", "autumn"): ["가을회", "사시미", "초밥", "광어", "연어"],
            ("회", "winter"): ["회", "사시미", "초밥", "광어", "연어"]
        }

        # 매장 타입 정규화 (부분 매칭으로 유사한 타입 찾기)
        normalized_store_type = None
        store_type_lower = store_type.lower()

        # 정확한 매칭 먼저 시도
        if store_type in store_base_keywords:
            normalized_store_type = store_type
        # 부분 매칭으로 유사 타입 찾기
        elif "카페" in store_type or "커피" in store_type or "coffee" in store_type_lower:
            normalized_store_type = "카페"
        elif "중국" in store_type or "중식" in store_type:
            normalized_store_type = "중국집"
        elif "한식" in store_type or "한정식" in store_type or "백반" in store_type:
            normalized_store_type = "한식당"
        elif "일식" in store_type or "초밥" in store_type or "일본" in store_type or "스시" in store_type:
            normalized_store_type = "일식당"
        elif "양식" in store_type or "이탈리안" in store_type or "이태리" in store_type:
            normalized_store_type = "양식당"
        elif "분식" in store_type:
            normalized_store_type = "분식집"
        elif "치킨" in store_type or "chicken" in store_type_lower:
            normalized_store_type = "치킨집"
        elif "디저트" in store_type or "dessert" in store_type_lower:
            normalized_store_type = "디저트카페"
        elif "베이커리" in store_type or "빵" in store_type or "bakery" in store_type_lower:
            normalized_store_type = "베이커리"
        elif "술" in store_type or "주점" in store_type or "bar" in store_type_lower or "이자카야" in store_type:
            normalized_store_type = "술집"
        # 새로 추가한 타입들
        elif "피자" in store_type or "pizza" in store_type_lower:
            normalized_store_type = "피자"
        elif "햄버거" in store_type or "버거" in store_type or "burger" in store_type_lower:
            normalized_store_type = "햄버거"
        elif "타코" in store_type or "멕시칸" in store_type or "부리또" in store_type or "taco" in store_type_lower or "mexican" in store_type_lower:
            normalized_store_type = "멕시칸"
        elif "쌀국수" in store_type or "팟타이" in store_type or "태국" in store_type or "베트남" in store_type or "아시안" in store_type:
            normalized_store_type = "아시아음식"
        elif "고기" in store_type or "삼겹살" in store_type or "bbq" in store_type_lower or "구이" in store_type:
            normalized_store_type = "고기집"
        elif "횟집" in store_type or "회" in store_type or "사시미" in store_type:
            normalized_store_type = "회"

        # 일반 음식점 fallback 키워드
        general_food_keywords = ["맛집", "음식", "먹스타그램", "맛스타그램", "점심", "저녁", "식사", "요리"]

        # 키워드 수집 시작
        keywords = []

        # 1. 매장 타입 + 계절 조합 키워드
        if normalized_store_type:
            combo_key = (normalized_store_type, season)
            if combo_key in combined_keywords:
                keywords.extend(combined_keywords[combo_key])

            # 2. 매장 타입 기본 키워드
            if normalized_store_type in store_base_keywords:
                keywords.extend(store_base_keywords[normalized_store_type][:4])

        # 3. 정의되지 않은 매장 타입이거나 키워드가 부족한 경우
        if not normalized_store_type or len(keywords) < 5:
            logger.warning(f"Store type '{store_type}' not well-defined or insufficient keywords, using fallback")
            # 원본 매장 타입명을 직접 키워드로 사용
            if store_type:
                keywords.insert(0, store_type)
            # 일반 음식점 키워드 추가
            keywords.extend(general_food_keywords[:5])

        # 4. 계절 키워드 추가
        if season in seasonal_keywords:
            keywords.extend(seasonal_keywords[season][:3])

        # 중복 제거 및 최대 10개로 제한
        unique_keywords = []
        seen = set()
        for kw in keywords:
            if kw not in seen:
                unique_keywords.append(kw)
                seen.add(kw)
                if len(unique_keywords) >= 10:
                    break

        logger.info(f"Generated keywords for {store_type} (normalized: {normalized_store_type}, season: {season}): {unique_keywords}")
        return unique_keywords

    def _get_google_trends(self, limit: int = 20, store_type: str = "카페") -> List[str]:
        """
        Google Trends를 통한 실시간 트렌드 수집 (매장 타입별)

        Interest Over Time API를 사용하여 매장 타입 + 계절별 키워드의 인기도를 측정합니다.

        Args:
            limit: 가져올 트렌드 개수 (기본값: 20)
            store_type: 매장 타입

        Returns:
            트렌드 키워드 리스트
        """
        import time as time_module

        max_retries = 2
        retry_delay = 2  # 초

        for attempt in range(max_retries):
            try:
                # Google Trends 객체 생성 (한국, 한국어) - 더 긴 timeout
                pytrend = TrendReq(hl='ko', tz=540, timeout=(15, 30))

                # 매장 타입별 + 계절별 키워드 조합
                season = self.get_season()
                keywords = self._get_store_season_keywords(store_type, season)

                # 최대 5개씩 나눠서 검색, 최대 3개 배치(15개 키워드)까지만 (API 제한)
                all_scores = {}
                max_batches = 3
                batch_count = 0

                for i in range(0, len(keywords), 5):
                    if batch_count >= max_batches:
                        break

                    batch = keywords[i:i+5]

                    try:
                        # 키워드 등록
                        pytrend.build_payload(
                            batch,
                            cat=0,
                            timeframe='now 7-d',  # 최근 7일
                            geo='KR',  # 한국
                            gprop=''
                        )

                        # Interest Over Time 가져오기
                        interest_df = pytrend.interest_over_time()

                        if interest_df is not None and not interest_df.empty:
                            # 각 키워드의 평균 검색량 계산
                            for keyword in batch:
                                if keyword in interest_df.columns:
                                    avg_score = interest_df[keyword].mean()
                                    all_scores[keyword] = avg_score

                        batch_count += 1

                        # API 호출 간 딜레이 (더 길게)
                        if batch_count < max_batches and i + 5 < len(keywords):
                            time_module.sleep(2)

                    except Exception as batch_error:
                        logger.warning(f"Failed to fetch batch {batch}: {batch_error}")
                        batch_count += 1
                        continue

                # 인기순으로 정렬
                if all_scores:
                    sorted_keywords = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
                    top_keywords = [keyword for keyword, score in sorted_keywords[:limit]]
                    logger.info(f"Google Trends - seasonal trends found: {top_keywords}")
                    return top_keywords

                logger.warning("Google Trends returned no data")
                return []

            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Google Trends attempt {attempt + 1} failed: {e}, retrying in {retry_delay}s...")
                    time_module.sleep(retry_delay)
                else:
                    logger.error(f"Failed to fetch Google Trends after {max_retries} attempts: {e}")
                    return []

        return []

    def _get_naver_trends(self, limit: int = 5) -> List[str]:
        """
        Naver Datalab API를 통한 트렌드 수집

        Args:
            limit: 가져올 트렌드 개수

        Returns:
            트렌드 키워드 리스트
        """
        if not self.naver_client_id or not self.naver_client_secret:
            logger.warning("Naver API credentials not configured")
            return []

        try:
            # Naver Datalab API는 키워드를 미리 지정해야 하므로
            # 계절별 인기 음식 키워드를 기반으로 검색량 확인
            season = self.get_season()

            seasonal_keywords = {
                "spring": ["봄나물", "딸기", "벚꽃빵", "피크닉도시락", "봄샐러드"],
                "summer": ["빙수", "냉면", "수박", "아이스크림", "시원한음료"],
                "autumn": ["밤", "단풍카페", "호박", "고구마", "따뜻한차"],
                "winter": ["어묵", "군밤", "붕어빵", "호떡", "따뜻한국물"]
            }

            keywords = seasonal_keywords.get(season, ["커피", "디저트", "브런치", "샐러드", "파스타"])

            # 실제 Naver Datalab API 호출은 복잡하므로 일단 키워드 반환
            # TODO: Naver Datalab API 연동 구현
            logger.info(f"Naver seasonal keywords: {keywords[:limit]}")
            return keywords[:limit]

        except Exception as e:
            logger.error(f"Failed to fetch Naver trends: {e}")
            return []

    def _get_mock_trends(self, limit: int = 5) -> List[str]:
        """Mock 트렌드 데이터 (테스트용)"""
        now = datetime.now(self.korea_tz)
        month = now.month

        # 계절별 Mock 트렌드
        seasonal_trends = {
            "spring": ["벚꽃", "피크닉", "봄나들이", "새싹", "환절기"],
            "summer": ["여름휴가", "아이스커피", "수박", "바캉스", "더위"],
            "autumn": ["단풍", "가을", "추석", "낙엽", "독서"],
            "winter": ["크리스마스", "연말", "따뜻한", "겨울", "눈"]
        }

        season = self.get_season()
        trends = seasonal_trends.get(season, ["음식", "맛집", "카페", "디저트", "음료"])

        return trends[:limit]

    def get_weather_emoji(self, weather_condition: str) -> str:
        """날씨 조건에 따른 이모지 반환"""
        emoji_map = {
            "clear": "☀️",
            "clouds": "☁️",
            "rain": "🌧️",
            "drizzle": "🌦️",
            "thunderstorm": "⛈️",
            "snow": "🌨️",
            "mist": "🌫️",
            "fog": "🌫️"
        }
        return emoji_map.get(weather_condition.lower(), "🌤️")

    def get_season_emoji(self, season: str) -> str:
        """계절에 따른 이모지 반환"""
        emoji_map = {
            "spring": "🌸",
            "summer": "☀️",
            "autumn": "🍂",
            "winter": "⛄"
        }
        return emoji_map.get(season, "🌿")


# 싱글톤 인스턴스
context_collector_service = ContextCollectorService()
