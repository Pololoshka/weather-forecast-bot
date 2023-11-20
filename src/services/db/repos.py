import logging
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.services.db.models import City, User, UserCity

logger = logging.getLogger(__name__)


class UserRepo:
    def __init__(self, session: Session):
        self.session = session

    def create(self, user_id: int, first_name: str) -> User:
        logger.debug("Create user in db")
        self.session.add(user := User(id=user_id, first_name=first_name))
        return user

    def get(self, user_id: int) -> User | None:
        logger.debug("Search user in db by id")
        return self.session.scalar(select(User).where(User.id == user_id))


class CityRepo:
    def __init__(self, session: Session):
        self.session = session

    def get_by_name(self, city: str) -> Sequence[City]:
        logger.debug("Search cities in db by name")
        list_cities = self.session.execute(select(City).where(City.name == city)).scalars().all()
        return list_cities

    def get_by_name_country_district(self, city: str, country: str, district: str) -> City | None:
        logger.debug("Search city in db by name, country, district")
        return self.session.scalar(
            select(City).where(
                City.name == city.lower(), City.country == country, City.district == district
            )
        )

    def get_by_id(self, city_id: int) -> City | None:
        logger.debug("Search city in db by id")
        return self.session.scalar(select(City).where(City.id == city_id))


class UserCityRepo:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, user_id: int, city_id: int) -> UserCity | None:
        logger.debug("Search user_city in db by id_user and id_city")
        return self.session.scalar(
            select(UserCity).where(
                UserCity.user_id == user_id,
                UserCity.city_id == city_id,
            )
        )
