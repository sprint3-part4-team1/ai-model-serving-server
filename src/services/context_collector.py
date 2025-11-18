"""
Context Collector Service
날씨, 계절, 시간대, SNS 트렌드 등의 컨텍스트 정보를 수집하는 서비스
"""

import os
import requests
from datetime import datetime
from typing import Dict, Optional, List
import pytz
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from logger import app_logger as logger
from config import settings


class ContextCollectorService:
    """컨텍스트 정보 수집 서비스"""

    def __init__(self):
        self.openweather_api_key = settings.OPENWEATHER_API_KEY
        self.naver_client_id = settings.NAVER_CLIENT_ID
        self.naver_client_secret = settings.NAVER_CLIENT_SECRET

        # 한국 시간대
        self.korea_tz = pytz.timezone('Asia/Seoul')

    def get_full_context(
        self,
        location: str = "Seoul",
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> Dict:
        """
        전체 컨텍스트 정보 수집

        Args:
            location: 위치 이름 (예: "Seoul", "Busan")
            lat: 위도 (선택)
            lon: 경도 (선택)

        Returns:
            전체 컨텍스트 정보
        """
        logger.info(f"Collecting context for location: {location}")

        # 날씨 정보 수집
        weather = self.get_weather(location, lat, lon)

        # 계절 판단
        season = self.get_season()

        # 시간대 판단
        time_info = self.get_time_info()

        # 트렌드 수집 (선택)
        trends = self.get_trends()

        context = {
            "weather": weather,
            "season": season,
            "time_info": time_info,
            "trends": trends,
            "location": location,
            "timestamp": datetime.now(self.korea_tz).isoformat()
        }

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

    def get_trends(self, limit: int = 5) -> List[str]:
        """
        SNS 트렌드 수집 (선택 기능)

        Args:
            limit: 가져올 트렌드 개수

        Returns:
            트렌드 키워드 리스트
        """
        if not self.naver_client_id or not self.naver_client_secret:
            logger.warning("Naver API credentials not configured, returning empty trends")
            return []

        try:
            # TODO: 네이버 검색 트렌드 API 또는 크롤링 구현
            # 현재는 Mock 데이터 반환
            logger.warning("Trend collection not implemented yet, returning mock data")
            return self._get_mock_trends(limit)

        except Exception as e:
            logger.error(f"Failed to fetch trends: {e}")
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
