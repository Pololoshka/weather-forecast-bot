from sqlalchemy import select
from sqlalchemy.orm import Session

from src.errors import NotFoundError
from src.models import City, User, UserCity


class UserRepo:
    def __init__(self, session: Session):
        self.session = session

    def create(self, user_id: int, first_name: str) -> None:
        self.session.add(User(id=user_id, first_name=first_name))

    def get(self, user_id: int) -> User:
        user_ = self.session.scalar(select(User).where(User.id == user_id))
        if user_ is None:
            raise NotFoundError(f"User with id={user_id} not found")
        return user_


class CityRepo:
    def __init__(self, session: Session):
        self.session = session

    def get_by_name(self, city: str) -> City:
        city_ = self.session.scalar(select(City).where(City.name == city))
        if city_ is None:
            raise NotFoundError(f"City with name={city} not found")
        return city_

    def get_by_id(self, city_id: int) -> City:
        city_ = self.session.scalar(select(City).where(City.id == city_id))
        if city_ is None:
            raise NotFoundError(f"City with id={city_id} not found")
        return city_


class UserCityRepo:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, user_id: int, city_id: int) -> UserCity:
        user_city = self.session.scalar(
            select(UserCity).where(
                UserCity.user_id == user_id,
                UserCity.city_id == city_id,
            )
        )
        if user_city is None:
            raise NotFoundError(
                f"Association with user_id={user_id} and city_id={city_id} not found"
            )
        return user_city

    def get_is_preferred_city(self, user_id: int) -> UserCity:
        user_city = self.session.scalar(
            select(UserCity).where(
                UserCity.user_id == user_id,
                UserCity.is_preferred.is_(True),
            )
        )
        if user_city is None:
            raise NotFoundError(
                f"Association with user_id={user_id} and is_preferred_city not found"
            )
        return user_city
