from datetime import datetime

import pytest
from requests_mock import Mocker as RequestsMocker

from src.models import CurrentWeather, Geolocation, WeatherForecast, WeatherOnDay
from src.services.wheater_client import WeatherClient
from src.settings import Settings


@pytest.fixture()
def client(settings: Settings) -> WeatherClient:
    return WeatherClient(url=settings.weather_url, timeout=settings.timeout)


def test_get_forecast_weather(
    requests_mock: RequestsMocker, client: WeatherClient, geolocation: Geolocation
) -> None:
    requests_mock.get(
        client.url,
        json={
            "latitude": 59.93801,
            "longitude": 30.32132,
            "generationtime_ms": 0.841975212097168,
            "utc_offset_seconds": 10800,
            "timezone": "Europe/Moscow",
            "timezone_abbreviation": "MSK",
            "elevation": 4.0,
            "daily_units": {
                "time": "iso8601",
                "weathercode": "wmo code",
                "temperature_2m_max": "°C",
                "temperature_2m_min": "°C",
            },
            "daily": {
                "time": [
                    "2023-08-17",
                    "2023-08-18",
                    "2023-08-19",
                    "2023-08-20",
                    "2023-08-21",
                    "2023-08-22",
                    "2023-08-23",
                ],
                "weathercode": [3, 3, 3, 3, 63, 61, 61],
                "temperature_2m_max": [24.5, 22.2, 23.0, 23.1, 24.9, 18.4, 17.6],
                "temperature_2m_min": [20.1, 17.5, 15.7, 16.4, 14.5, 15.2, 13.1],
            },
        },
    )

    expected = WeatherForecast(
        weather_on_day=[
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-17"), temp_max=24.5, temp_min=20.1, condition=3
            ),
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-18"), temp_max=22.2, temp_min=17.5, condition=3
            ),
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-19"), temp_max=23.0, temp_min=15.7, condition=3
            ),
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-20"), temp_max=23.1, temp_min=16.4, condition=3
            ),
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-21"),
                temp_max=24.9,
                temp_min=14.5,
                condition=63,
            ),
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-22"),
                temp_max=18.4,
                temp_min=15.2,
                condition=61,
            ),
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-23"),
                temp_max=17.6,
                temp_min=13.1,
                condition=61,
            ),
        ]
    )

    assert client.get_forecast_weather(days=7, geolocation=geolocation) == expected


def test_get_current_weather(
    requests_mock: RequestsMocker, client: WeatherClient, geolocation: Geolocation
) -> None:
    requests_mock.get(
        client.url,
        json={
            "latitude": 59.93801,
            "longitude": 30.32132,
            "generationtime_ms": 0.4640817642211914,
            "utc_offset_seconds": 10800,
            "timezone": "Europe/Moscow",
            "timezone_abbreviation": "MSK",
            "elevation": 4.0,
            "current_weather": {
                "temperature": 24.5,
                "windspeed": 16.9,
                "winddirection": 276,
                "weathercode": 0,
                "is_day": 1,
                "time": "2023-08-17T13:00",
            },
        },
    )
    expected = CurrentWeather(
        temp=24.5,
        condition=0,
        date=datetime.fromisoformat("2023-08-17T13:00"),
    )
    assert client.get_current_weather(geolocation=geolocation) == expected
