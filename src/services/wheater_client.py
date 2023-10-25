import requests

from src.models.models_for_db import City
from src.models.query_models_api import CurrentWeather, WeatherForecast


class WeatherClient:
    def __init__(self, url: str, timeout: int):
        self.url = url
        self.timeout = timeout

    def get_forecast_weather(self, days: int, geolocation: City) -> WeatherForecast:
        response = requests.get(
            url=self.url,
            params={
                "latitude": str(geolocation.latitude),
                "longitude": str(geolocation.longitude),
                "daily": ["weathercode", "temperature_2m_max", "temperature_2m_min"],
                "current_weather": "false",
                "timezone": geolocation.timezone,
                "forecast_days": str(days),
            },
            timeout=self.timeout,
        )
        return WeatherForecast.parse(data=response.json()["daily"])

    def get_current_weather(self, geolocation: City) -> CurrentWeather:
        response = requests.get(
            url=self.url,
            params={
                "latitude": str(geolocation.latitude),
                "longitude": str(geolocation.longitude),
                "current_weather": "true",
                "timezone": geolocation.timezone,
            },
            timeout=self.timeout,
        )
        return CurrentWeather.parse(data=response.json()["current_weather"])
