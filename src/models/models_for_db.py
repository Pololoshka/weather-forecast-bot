from collections.abc import Generator
from datetime import datetime
from typing import Optional, Self

from sqlalchemy import TIMESTAMP, BigInteger, Float, ForeignKey, String, func, text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column, relationship

from src.services.text import Language, get_language


class Base(DeclarativeBase, MappedAsDataclass):
    ...


class UserCity(Base):
    __tablename__ = "user_city"
    user_id: Mapped[int] = mapped_column(
        ForeignKey(column="users.id"), primary_key=True, init=False
    )
    city_id: Mapped[int] = mapped_column(
        ForeignKey(column="cities.id"), primary_key=True, init=False
    )
    is_preferred: Mapped[bool] = mapped_column(default=False, server_default=text("False"))
    date_added: Mapped[datetime] = mapped_column(
        TIMESTAMP(), init=False, server_default=func.CURRENT_TIMESTAMP()
    )

    # association between UserCity -> City
    city: Mapped["City"] = relationship(default=None, lazy="joined")


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(30))

    # association between User -> UserCity -> City
    city_associations: Mapped[list["UserCity"]] = relationship(
        default_factory=list,
        lazy="joined",
        order_by="UserCity.date_added",
        cascade="all, delete-orphan",
    )

    @hybrid_property
    def preferred_user_city(self) -> Optional["UserCity"]:
        for user_city in self.city_associations:
            if user_city.is_preferred is True:
                return user_city
        return None

    @hybrid_property
    def cities(self) -> Generator:
        for user_city in self.city_associations:
            yield user_city.city


class City(Base):
    __tablename__ = "cities"
    id: Mapped[int] = mapped_column(BigInteger, init=False, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    country: Mapped[str] = mapped_column(String(100))
    district: Mapped[str] = mapped_column(String(100))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    timezone: Mapped[str] = mapped_column(String(30))

    @classmethod
    def parse(cls, data: dict) -> Self:
        return cls(
            latitude=data["latitude"],
            longitude=data["longitude"],
            timezone=data["timezone"],
            name=data["name"].lower(),
            country=data["country"],
            district=data["admin1"],
        )

    @hybrid_property
    def language(self) -> Language:
        return get_language(message=self.name)
