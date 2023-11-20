from pytest_mock import MockFixture
from sqlalchemy import select
from sqlalchemy.orm import Session

from src import exceptions as exc
from src.services.db.models import User
from src.services.db.uow import SqlAlchemyUnitOfWork
from src.services.ui.bot import Bot


def test_with_db_not_create_user(
    mocker: MockFixture, uow: SqlAlchemyUnitOfWork, user: User
) -> None:
    bot = mocker.MagicMock()
    func = mocker.MagicMock()
    message = mocker.MagicMock()
    message.from_user.id = user.id
    message.from_user.first_name = user.first_name

    reply = mocker.patch("src.services.ui.bot.MessageBot")

    bot.services.uow = uow

    args = (1, 2)
    kwargs = {"a": "a"}

    res = Bot._with_db(bot, func=func)(message, *args, **kwargs)
    assert res == func.return_value

    func.assert_called_once_with(message, *args, user=user, reply=reply.return_value, **kwargs)
    reply.assert_called_once_with(bot=bot, chat_id=message.chat.id)


def test_with_db_with_create_user(
    mocker: MockFixture, uow: SqlAlchemyUnitOfWork, session: Session
) -> None:
    bot = mocker.MagicMock()
    func = mocker.MagicMock()
    message = mocker.MagicMock()
    reply = mocker.patch("src.services.ui.bot.MessageBot")

    user = User(id=1, first_name="Leo")
    message.from_user.id = user.id
    message.from_user.first_name = user.first_name

    bot.services.uow = uow

    args = (1, 2)
    kwargs = {"a": "a"}

    res = Bot._with_db(bot, func=func)(message, *args, **kwargs)
    assert res == func.return_value

    expected: User | None = session.scalar(select(User).where(User.id == user.id))
    assert expected
    assert expected.first_name == user.first_name
    func.assert_called_once_with(message, *args, user=expected, reply=reply.return_value, **kwargs)
    reply.assert_called_once_with(bot=bot, chat_id=message.chat.id)


def test_error_handler(mocker: MockFixture) -> None:
    bot = mocker.MagicMock()
    func = mocker.MagicMock()
    message = mocker.MagicMock()
    args = (1, 2)
    kwargs = {"a": "a"}
    res = Bot._error_handler(bot, func=func)(message, *args, **kwargs)
    assert res == func.return_value
    func.assert_called_once_with(message, *args, **kwargs)


def test_error_handler_with_error(mocker: MockFixture) -> None:
    bot = mocker.MagicMock()
    func = mocker.MagicMock(side_effect=exc.BotError)
    message = mocker.MagicMock()
    args = (1, 2)
    kwargs = {"a": "a"}
    res = Bot._error_handler(bot, func=func)(message, *args, **kwargs)
    assert res is None
    func.assert_called_once_with(message, *args, **kwargs)
