from types import TracebackType
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

    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

    def __enter__(self) -> None:
        self.session = self.session_factory()
        self.users = UserRepo(session=self.session)
        self.cities = CityRepo(session=self.session)
        self.user_city = UserCityRepo(session=self.session)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.session.close()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
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
