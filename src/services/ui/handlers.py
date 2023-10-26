from collections.abc import Sequence
from datetime import datetime

from telebot.types import Message

from src.services.db.models_for_db import City, User, UserCity
from src.services.db.uow import SqlAlchemyUnitOfWork
from src.services.text import get_language, parse_city_from_message
from src.services.ui.bot import MyBot
from src.services.ui.create_message import MessageBot


def add_new_cities_in_bd(bot: MyBot, cities: Sequence[City]) -> None:
    for city in cities:
        if bot.services.uow.cities.get_by_name_country_district(
            city=city.name, country=city.country, district=city.district
        ):
            continue
        bot.services.uow.session.add(city)
    bot.services.uow.session.flush()


def change_preferred_city(user: User, city_id: int, uow: SqlAlchemyUnitOfWork) -> None:
    if preferred_user_city := user.preferred_user_city:
        preferred_user_city.is_preferred = False
    if user_city := uow.user_city.get_by_id(user_id=user.id, city_id=city_id):
        user_city.is_preferred = True
    uow.session.flush()


def start(message: Message, bot: MyBot, user: User) -> None:
    MessageBot(chat_id=message.chat.id, bot=bot).create_start_message(user=user)


def add_new_city(message: Message, bot: MyBot, user: User) -> None:
    MessageBot(chat_id=message.chat.id, bot=bot).create_message_with_input_new_city()
    bot.register_next_step_handler(message=message, callback=on_click)


def on_click(message: Message, bot: MyBot, user: User) -> None:
    output_message = MessageBot(chat_id=message.chat.id, bot=bot)
    language = get_language(message.text)
    city_name = message.text.lower()

    if cities_in_bd := bot.services.uow.cities.get_by_name(city=city_name):
        output_message.create_message_with_new_cities(city_name=city_name, cities=cities_in_bd)

    elif cities := bot.services.geo_client.get_geolocation(city_name=city_name, language=language):
        add_new_cities_in_bd(bot=bot, cities=cities)
        output_message.create_message_with_new_cities(
            city_name=city_name, cities=bot.services.uow.cities.get_by_name(city_name)
        )

    else:
        output_message.create_message_wrong_city(user=user)


def choose_another_city(message: Message, bot: MyBot, user: User) -> None:
    MessageBot(chat_id=message.chat.id, bot=bot).create_message_choose_another_city(user=user)


def create_current_weather_forecast(message: Message, bot: MyBot, user: User) -> None:
    output_message = MessageBot(chat_id=message.chat.id, bot=bot)
    if preferred_user_city := user.preferred_user_city:
        city = preferred_user_city.city
        current_weather = bot.services.weather_client.get_current_weather(geolocation=city)
        output_message.create_message_with_current_weather(
            date=datetime.fromtimestamp(message.date),
            city=city,
            current_weather=current_weather,
        )
    else:
        output_message.create_message_except_no_preferred_city()


def create_weather_forecast_on_one_day(message: Message, bot: MyBot, user: User) -> None:
    output_message = MessageBot(chat_id=message.chat.id, bot=bot)
    if preferred_user_city := user.preferred_user_city:
        city = preferred_user_city.city
        weather_forecast = bot.services.weather_client.get_forecast_weather(
            geolocation=city, days=1
        )
        output_message.create_message_with_weather_forecast_on_one_day(
            city=city,
            day=weather_forecast.weather_on_day[0],
        )
    else:
        output_message.create_message_except_no_preferred_city()


def create_weather_forecast_on_three_days(message: Message, bot: MyBot, user: User) -> None:
    output_message = MessageBot(chat_id=message.chat.id, bot=bot)

    if preferred_user_city := user.preferred_user_city:
        city = preferred_user_city.city
        forecast_weather = bot.services.weather_client.get_forecast_weather(
            geolocation=city, days=3
        )

        for day in forecast_weather.weather_on_day:
            output_message.create_message_with_weather_forecast_for_few_days(
                city=city,
                day=day,
            )
    else:
        output_message.create_message_except_no_preferred_city()


def create_weather_forecast_on_seven_days(message: Message, bot: MyBot, user: User) -> None:
    output_message = MessageBot(chat_id=message.chat.id, bot=bot)

    if preferred_user_city := user.preferred_user_city:
        city = preferred_user_city.city
        forecast_weather = bot.services.weather_client.get_forecast_weather(
            geolocation=city, days=7
        )
        for day in forecast_weather.weather_on_day:
            output_message.create_message_with_weather_forecast_for_few_days(
                city=city,
                day=day,
            )
    else:
        output_message.create_message_except_no_preferred_city()


def create_weather_forecast_on_fourteen_day(message: Message, bot: MyBot, user: User) -> None:
    output_message = MessageBot(chat_id=message.chat.id, bot=bot)

    if preferred_user_city := user.preferred_user_city:
        city = preferred_user_city.city
        forecast_weather = bot.services.weather_client.get_forecast_weather(
            geolocation=city, days=14
        )
        for day in forecast_weather.weather_on_day:
            output_message.create_message_with_weather_forecast_for_few_days(
                city=city,
                day=day,
            )
    else:
        output_message.create_message_except_no_preferred_city()


def delete_city_user(message: Message, bot: MyBot, user: User) -> None:
    del user.city_associations[:-4]
    bot.services.uow.session.flush()
    MessageBot(chat_id=message.chat.id, bot=bot).create_message_delete_city_user(user=user)


def process_message_with_city(message: Message, bot: MyBot, user: User) -> None:
    output_message = MessageBot(chat_id=message.chat.id, bot=bot)

    city_ = parse_city_from_message(text=message.text)
    city = bot.services.uow.cities.get_by_name_country_district(
        city=city_.city, country=city_.country, district=city_.district
    )
    if not city:
        output_message.create_message_with_incomprehension()
        return
    if city not in (c for c in user.cities):
        user.city_associations.append(UserCity(city=city))
        bot.services.uow.session.flush()

    change_preferred_city(user=user, city_id=city.id, uow=bot.services.uow)
    output_message.create_message_with_preferred_city(city=city)


def handle_text(message: Message, bot: MyBot, user: User) -> None:
    MessageBot(chat_id=message.chat.id, bot=bot).create_message_with_incomprehension()


def handle_any_content(message: Message, bot: MyBot, user: User) -> None:
    MessageBot(chat_id=message.chat.id, bot=bot).create_message_with_incomprehension()
