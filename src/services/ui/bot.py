import functools
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar

from telebot import TeleBot
from telebot.types import Message

from src import exceptions as exc
from src.services.db.uow import SqlAlchemyUnitOfWork
from src.services.geolocation.geolocation_client import GeolocationClient
from src.services.ui.const_ui import Text
from src.services.weather.weather_client import WeatherClient


@dataclass
class Service:
    uow: SqlAlchemyUnitOfWork
    geo_client: GeolocationClient
    weather_client: WeatherClient


RT = TypeVar("RT")


class MyBot(TeleBot):
    def __init__(self, services: Service, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.services = services

    def _with_db(self, func: Callable[..., RT]) -> Callable[..., RT]:
        @functools.wraps(func)
        def inner_wrapper(message: Message, *args: Any, **kwargs: Any) -> RT:
            with self.services.uow:
                if not (user := self.services.uow.users.get(message.from_user.id)):
                    user = self.services.uow.users.create(
                        user_id=message.from_user.id,
                        first_name=message.from_user.first_name,
                    )

                return func(message, *args, user=user, **kwargs)

        return inner_wrapper

    def _error_handler(self, func: Callable[..., RT]) -> Callable[..., RT | None]:
        @functools.wraps(func)
        def inner_wrapper(message: Message, *args: Any, **kwargs: Any) -> RT | None:
            try:
                return func(message, *args, **kwargs)
            except exc.BotError as err:
                self.send_message(chat_id=message.chat.id, text=Text.message_exc(err=str(err)))
            except Exception as err:
                # TODO: logger
                print(err)  # noqa: T201
                self.send_message(chat_id=message.chat.id, text=Text.message_exc(err=""))
            return None

        return inner_wrapper

    def register_message_handler(self, *args: Any, callback: Any, **kwargs: Any) -> None:
        super().register_message_handler(
            *args, **kwargs, callback=self._with_db(self._error_handler(callback)), pass_bot=True
        )

    def register_next_step_handler(self, *args: Any, callback: Any, **kwargs: Any) -> None:
        super().register_next_step_handler(
            *args, **kwargs, callback=self._with_db(self._error_handler(callback)), bot=self
        )
