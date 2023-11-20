import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.services.db.models import User
from src.services.db.repos import UserRepo
from src.services.db.uow import SqlAlchemyUnitOfWork


@pytest.fixture()
def user_repo(uow: SqlAlchemyUnitOfWork) -> UserRepo:
    return uow.users


def test_create(user_repo: UserRepo, session: Session) -> None:
    user = user_repo.create(user_id=1234, first_name="first_name")
    expected = session.scalar(select(User).where(User.id == user.id))
    assert user == expected


def test_get(user_repo: UserRepo, user: User) -> None:
    assert user_repo.get(user_id=user.id) == user


def test_get__is_none(user_repo: UserRepo) -> None:
    assert user_repo.get(user_id=10) is None
