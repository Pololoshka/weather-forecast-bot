from collections.abc import Generator

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import URL, Connection, create_engine
from sqlalchemy.orm import Session

from src.services.db.uow import SqlAlchemyUnitOfWork, create_url
from src.settings import Settings


@pytest.fixture(scope="session")
def db_url() -> URL:
    settings = Settings.from_environ(".env.tests")

    return create_url(settings=settings)


@pytest.fixture(scope="session")
def alembic_config(db_url: URL) -> Config:
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url.render_as_string(hide_password=False))
    return alembic_cfg


@pytest.fixture(scope="session")
def engine(db_url: "URL", alembic_config: Config) -> Generator[Connection, None, None]:
    engine = create_engine(db_url)
    connection = engine.connect()

    alembic_config.attributes["connection"] = connection
    command.upgrade(alembic_config, "head")

    yield connection

    command.downgrade(alembic_config, "base")

    connection.close()
    engine.dispose()


@pytest.fixture()
def session(engine: Connection) -> Generator[Session, None, None]:
    with engine.begin() as transaction:
        with Session(bind=engine, expire_on_commit=False) as session:
            yield session

        transaction.rollback()


@pytest.fixture()
def uow(session: Session) -> Generator[SqlAlchemyUnitOfWork, None, None]:
    uow = SqlAlchemyUnitOfWork(session_factory=lambda: session)  # type: ignore
    with uow:
        yield uow
