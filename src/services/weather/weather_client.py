import logging

import requests
from requests import exceptions as req_exc

from src import exceptions as exc
from src.services.db.models import City
from src.services.ui.const_ui import Text
from src.services.weather.weather_models import CurrentWeather, WeatherForecast

logger = logging.getLogger(__name__)


class WeatherClient:
    def __init__(self, url: str, timeout: int):
        self.url = url
        self.timeout = timeout

    def get_forecast_weather(self, days: int, geolocation: City) -> WeatherForecast:
        try:
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
        except req_exc.RequestException as err:
            logger.error("WeatherClientError from get_forecast_weather", exc_info=True)

            raise exc.WeatherClientError(Text.exc_weather) from err
        return WeatherForecast.parse(data=response.json()["daily"])

    def get_current_weather(self, geolocation: City) -> CurrentWeather:
        try:
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
        except req_exc.RequestException as err:
            logger.error("WeatherClientError from get_current_weather", exc_info=True)
            raise exc.WeatherClientError(Text.exc_weather) from err
        return CurrentWeather.parse(data=response.json()["current_weather"])
