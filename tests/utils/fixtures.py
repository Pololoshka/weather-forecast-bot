import pytest
from sqlalchemy.orm import Session

from src.services.db.models import City, User, UserCity
from src.services.geolocation.geolocation_client import GeolocationClient
from src.settings import Settings


@pytest.fixture()
def client(settings: Settings) -> GeolocationClient:
    return GeolocationClient(url=settings.geolocation_url, timeout=settings.timeout)


@pytest.fixture()
def city_1(session: Session) -> City:
    city = City(
        latitude=59.93863,
        longitude=30.31413,
        timezone="Europe/Moscow",
        name="санкт-петербург",
        country="Россия",
        district="Санкт-Петербург",
    )
    session.add(city)
    session.flush()
    return city


@pytest.fixture()
def city_2(session: Session) -> City:
    city = City(
        latitude=55.75222,
        longitude=37.61556,
        timezone="Europe/Moscow",
        name="москва",
        country="Россия",
        district="Москва",
    )
    session.add(city)
    session.flush()
    return city


@pytest.fixture()
def city_3(session: Session) -> City:
    city = City(
        latitude=52.52437,
        longitude=13.41053,
        timezone="Europe/Berlin",
        name="berlin",
        country="Germany",
        district="Land Berlin",
    )
    session.add(city)
    session.flush()
    return city


@pytest.fixture()
def city_4(session: Session) -> City:
    city = City(
        latitude=51.50853,
        longitude=-0.12574,
        timezone="Europe/London",
        name="london",
        country="United Kingdom",
        district="England",
    )
    session.add(city)
    session.flush()
    return city


@pytest.fixture()
def city_5(session: Session) -> City:
    city = City(
        latitude=41.89193,
        longitude=12.51133,
        timezone="Europe/Rome",
        name="rome",
        country="Italy",
        district="Latium",
    )
    session.add(city)
    session.flush()
    return city


@pytest.fixture()
def user(session: Session) -> User:
    user = User(
        id=1,
        first_name="Leo",
    )
    session.add(user)
    session.flush()
    return user


@pytest.fixture()
def user_city_with_preferred_city(session: Session, user: User, city_1: City) -> UserCity:
    user.city_associations.append(user_city := UserCity(city=city_1, is_preferred=True))
    session.flush()
    return user_city


@pytest.fixture()
def user_city_without_preferred_city(session: Session, user: User, city_2: City) -> UserCity:
    user.city_associations.append(user_city := UserCity(city=city_2))
    session.flush()
    return user_city
