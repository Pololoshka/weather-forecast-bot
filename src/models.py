from dataclasses import dataclass
from datetime import datetime
from typing import Self

from sqlalchemy import BigInteger, ForeignKey, String, text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)


@dataclass
class WeatherOnDay:
    date: datetime
    temp_max: float
    temp_min: float
    condition: int


@dataclass
class CurrentWeather:
    temp: float
    condition: int
    date: datetime

    @classmethod
    def parse(cls, data: dict) -> Self:
        return cls(
            temp=data["temperature"],
            condition=data["weathercode"],
            date=datetime.fromisoformat(data["time"]),
        )


@dataclass
class WeatherForecast:
    weather_on_day: list[WeatherOnDay]

    @classmethod
    def parse(cls, data: dict) -> Self:
        list_date = data["time"]
        list_temp_max = data["temperature_2m_max"]
        list_temp_min = data["temperature_2m_min"]
        list_condition_code = data["weathercode"]

        return cls(
            weather_on_day=[
                WeatherOnDay(
                    date=datetime.fromisoformat(date),
                    temp_max=temp_max,
                    temp_min=temp_min,
                    condition=condition,
                )
                for date, temp_max, temp_min, condition in zip(
                    list_date, list_temp_max, list_temp_min, list_condition_code, strict=False
                )
            ],
        )


@dataclass
class Geolocation:
    latitude: float
    longitude: float
    timezone: str
    city: str
    country_code: str

    @classmethod
    def parse(cls, data: dict) -> Self:
        return cls(
            latitude=data["latitude"],
            longitude=data["longitude"],
            timezone=data["timezone"],
            city=data["name"],
            country_code=data["country_code"],
        )


class Base(DeclarativeBase, MappedAsDataclass):
    ...


class UserCity(Base):
    __tablename__ = "user_city"
    user_id: Mapped[int] = mapped_column(ForeignKey(column="users.id"), primary_key=True)
    city_id: Mapped[int] = mapped_column(ForeignKey(column="cities.id"), primary_key=True)
    is_preferred: Mapped[bool] = mapped_column(default=False, server_default=text("False"))

    # association between UserCity -> City
    city: Mapped["City"] = relationship(default=None)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(30))

    # many-to-many relationship to City, bypassing the `UserCity` class
    cities: Mapped[list["City"]] = relationship(
        default_factory=list,
        secondary="user_city",
    )

    # association between User -> UserCity -> City
    city_associations: Mapped[list["UserCity"]] = relationship(default_factory=list)

    @hybrid_property
    def preferred_city(self) -> "City":
        for user_city in self.city_associations:
            if user_city.is_preferred is True:
                return user_city.city


class City(Base):
    __tablename__ = "cities"
    id: Mapped[int] = mapped_column(BigInteger, init=False, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)


if __name__ == "__main__":
    ...
