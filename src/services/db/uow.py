from typing import Protocol, Self

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.services.db.repos import CityRepo, UserCityRepo, UserRepo


class Settings(Protocol):
    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: int


def create_url(settings: Settings) -> URL:
    return URL.create(
        drivername="postgresql+psycopg",
        username=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    )


class SqlAlchemyUnitOfWork:
    session: Session
    users: UserRepo
    cities: CityRepo

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.users = UserRepo(session=self.session)
        self.cities = CityRepo(session=self.session)
        self.user_city = UserCityRepo(session=self.session)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    @classmethod
    def get_session(cls, url: URL) -> Self:
        return cls(
            session_factory=sessionmaker(
                bind=create_engine(
                    url=url,
                ),
            )
        )


if __name__ == "__main__":
    ...
