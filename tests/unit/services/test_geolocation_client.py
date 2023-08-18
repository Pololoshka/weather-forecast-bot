import pytest
from requests_mock import Mocker as RequestsMocker

from src.models import Geolocation
from src.services.geolocation_client import GeolocationClient
from src.settings import Settings


@pytest.fixture()
def client(settings: Settings) -> GeolocationClient:
    return GeolocationClient(url=settings.geolocation_url, timeout=settings.timeout)


def test_get_geolocation(
    requests_mock: RequestsMocker, client: GeolocationClient, geolocation: Geolocation
) -> None:
    requests_mock.get(
        url=client.url,
        json={
            "results": [
                {
                    "id": 498817,
                    "name": "Санкт-Петербург",
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
    expected = geolocation
    assert client.get_geolocation("Санкт-Петербург") == expected
