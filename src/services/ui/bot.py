import functools
from dataclasses import dataclass
from typing import Any

from telebot import TeleBot
from telebot.types import Message

from src.services.db.uow import SqlAlchemyUnitOfWork
from src.services.geolocation_client import GeolocationClient
from src.services.wheater_client import WeatherClient


@dataclass
class Service:
    uow: SqlAlchemyUnitOfWork
    geo_client: GeolocationClient
    weather_client: WeatherClient


class MyBot(TeleBot):
    def __init__(self, services: Service, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.services = services

    def _with_db(self, func: Any) -> Any:
        @functools.wraps(func)
        def inner_wrapper(message: Message, *args: Any, **kwargs: Any) -> Any:
            with self.services.uow:
                if not (user := self.services.uow.users.get(message.from_user.id)):
                    user = self.services.uow.users.create(
                        user_id=message.from_user.id,
                        first_name=message.from_user.first_name,
                    )

                return func(message, *args, user=user, **kwargs)

        return inner_wrapper

    def register_message_handler(self, *args: Any, callback: Any, **kwargs: Any) -> None:
        super().register_message_handler(
            *args, **kwargs, callback=self._with_db(callback), pass_bot=True
        )

    def register_next_step_handler(self, *args: Any, callback: Any, **kwargs: Any) -> None:
        super().register_next_step_handler(
            *args, **kwargs, callback=self._with_db(callback), bot=self
        )
