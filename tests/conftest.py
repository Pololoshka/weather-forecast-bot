import pytest

from src.models import Geolocation
from src.settings import Settings


@pytest.fixture()
def settings() -> Settings:
    return Settings()


@pytest.fixture()
def geolocation() -> Geolocation:
    return Geolocation(
        latitude=59.93863,
        longitude=30.31413,
        timezone="Europe/Moscow",
        city="Санкт-Петербург",
        country_code="RU",
    )
