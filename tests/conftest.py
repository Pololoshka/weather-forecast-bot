import pytest

from src.models.models_for_db import City
from src.settings import Settings


@pytest.fixture()
def settings() -> Settings:
    return Settings.from_environ()


@pytest.fixture()
def geolocation() -> City:
    return City(
        latitude=59.93863,
        longitude=30.31413,
        timezone="Europe/Moscow",
        name="Санкт-Петербург",
        country="Россия",
        district="Санкт-Петербург",
    )
