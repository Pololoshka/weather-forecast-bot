from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.models_for_db import City, User, UserCity


class UserRepo:
    def __init__(self, session: Session):
        self.session = session

    def create(self, user_id: int, first_name: str) -> User:
        self.session.add(user := User(id=user_id, first_name=first_name))
        return user

    def get(self, user_id: int) -> User | None:
        return self.session.scalar(select(User).where(User.id == user_id))


class CityRepo:
    def __init__(self, session: Session):
        self.session = session

    def get_by_name(self, city: str) -> Sequence[City]:
        list_cities = self.session.execute(select(City).where(City.name == city)).scalars().all()
        return list_cities

    def get_by_name_country_district(self, city: str, country: str, district: str) -> City | None:
        return self.session.scalar(
            select(City).where(
                City.name == city.lower(), City.country == country, City.district == district
            )
        )

    def get_by_id(self, city_id: int) -> City | None:
        return self.session.scalar(select(City).where(City.id == city_id))


class UserCityRepo:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, user_id: int, city_id: int) -> UserCity | None:
        return self.session.scalar(
            select(UserCity).where(
                UserCity.user_id == user_id,
                UserCity.city_id == city_id,
            )
        )
