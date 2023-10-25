from collections.abc import Callable

from telebot.types import Message

from src.services.db.uow import SqlAlchemyUnitOfWork, create_url
from src.services.geolocation_client import GeolocationClient
from src.services.ui import handlers as h
from src.services.ui.bot import MyBot, Service
from src.services.ui.const_ui import Command, MessageType, Text
from src.services.wheater_client import WeatherClient
from src.settings import Settings


def eq(a: str) -> Callable:
    def wrapper(m: Message) -> bool:
        return bool(m.text == a)

    return wrapper


def main() -> None:
    services = Service(
        uow=SqlAlchemyUnitOfWork.get_session(url=create_url(settings=Settings.from_environ())),
        weather_client=WeatherClient(url=Settings.weather_url, timeout=Settings.timeout),
        geo_client=GeolocationClient(url=Settings.geolocation_url, timeout=Settings.timeout),
    )
    bot = MyBot(services=services, token=Settings.from_environ().token_telebot)

    bot.register_message_handler(commands=[Command.start], callback=h.start)
    bot.register_message_handler(func=eq(Text.add_city), callback=h.add_new_city)
    bot.register_message_handler(func=eq(Text.choose_city), callback=h.choose_another_city)
    bot.register_message_handler(func=eq(Text.now), callback=h.create_current_weather_forecast)
    bot.register_message_handler(
        func=eq(Text.one_day), callback=h.create_weather_forecast_on_one_day
    )
    bot.register_message_handler(
        func=eq(Text.three_days), callback=h.create_weather_forecast_on_three_days
    )
    bot.register_message_handler(
        func=eq(Text.seven_days), callback=h.create_weather_forecast_on_seven_days
    )
    bot.register_message_handler(
        func=eq(Text.fourteen_days), callback=h.create_weather_forecast_on_fourteen_day
    )
    bot.register_message_handler(func=eq(Text.delete), callback=h.delete_city_user)
    bot.register_message_handler(content_types=[MessageType.text], callback=h.handle_text)
    bot.register_message_handler(content_types=[MessageType.any], callback=h.handle_any_content)

    bot.polling(none_stop=True)


if __name__ == "__main__":
    main()
