from requests_mock import Mocker as RequestsMocker

from src.services.db.models import City
from src.services.geolocation.geolocation_client import GeolocationClient


def test_get_geolocation(client: GeolocationClient, requests_mock: RequestsMocker) -> None:
    requests_mock.get(
        url=client.url,
        json={
            "results": [
                {
                    "id": 498817,
                    "name": "санкт-петербург",
                    "latitude": 59.93863,
                    "longitude": 30.31413,
                    "elevation": 11.0,
                    "feature_code": "PPLA",
                    "country_code": "RU",
                    "admin1_id": 536203,
                    "timezone": "Europe/Moscow",
                    "population": 5028000,
                    "country_id": 2017370,
                    "country": "Россия",
                    "admin1": "Санкт-Петербург",
                }
            ],
            "generationtime_ms": 1.461029,
        },
    )
    expected = [
        City(
            latitude=59.93863,
            longitude=30.31413,
            timezone="Europe/Moscow",
            name="санкт-петербург",
            country="Россия",
            district="Санкт-Петербург",
        )
    ]
    assert client.get_geolocation(city_name="санкт-петербург", language="ru") == expected
