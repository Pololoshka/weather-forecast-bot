from datetime import datetime

from telebot.types import Message

from src.models.models_for_db import User, UserCity
from src.services.text import get_language
from src.services.ui.bot import MyBot
from src.view.bot.add_new_cities_in_bd import add_new_cities_in_bd
from src.view.bot.chahge_preferred_city_user import change_preferred_city
from src.view.bot.create_markup import MarkupBot
from src.view.bot.create_message import MessageBot


def start(message: Message, bot: MyBot, user: User) -> None:
    markup = MarkupBot.create_buttons_with_cities_user(user=user)
    MessageBot.create_start_message(message_chat_id=message.chat.id, markup=markup, bot=bot)


def add_new_city(message: Message, bot: MyBot, user: User) -> None:
    MessageBot.create_message_with_input_new_city(message_chat_id=message.chat.id, bot=bot)
    bot.register_next_step_handler(message=message, callback=on_click)


def on_click(message: Message, bot: MyBot, user: User) -> None:
    language = get_language(message.text)
    city_name = message.text.lower()

    if cities_in_bd := bot.services.uow.cities.get_by_name(city=city_name):
        markup = MarkupBot.create_buttons_with_new_cities(cities=cities_in_bd)
        MessageBot.create_message_with_new_cities(
            message_chat_id=message.chat.id, bot=bot, city_name=city_name, markup=markup
        )

    elif cities := bot.services.geo_client.get_geolocation(city_name=city_name, language=language):
        add_new_cities_in_bd(bot=bot, cities=cities)
        markup = MarkupBot.create_buttons_with_new_cities(
            cities=bot.services.uow.cities.get_by_name(city_name)
        )
        MessageBot.create_message_with_new_cities(
            message_chat_id=message.chat.id, bot=bot, city_name=city_name, markup=markup
        )

    else:
        MessageBot.create_message_wrong_city(
            message_chat_id=message.chat.id,
            markup=MarkupBot.create_buttons_with_cities_user(user=user),
            bot=bot,
        )


def choose_another_city(message: Message, bot: MyBot, user: User) -> None:
    MessageBot.create_message_choose_another_city(
        message_chat_id=message.chat.id,
        markup=MarkupBot.create_buttons_with_cities_user(user=user),
        bot=bot,
    )


def create_current_weather_forecast(message: Message, bot: MyBot, user: User) -> None:
    if preferred_user_city := user.preferred_user_city:
        city = preferred_user_city.city
        current_weather = bot.services.weather_client.get_current_weather(geolocation=city)
        MessageBot.create_message_with_current_weather(
            message_chat_id=message.chat.id,
            bot=bot,
            date=datetime.fromtimestamp(message.date),
            city=city,
            current_weather=current_weather,
        )
    else:
        MessageBot.create_message_except_no_preferred_city(
            message_chat_id=message.chat.id, bot=bot, markup=MarkupBot.create_button_add_new_city()
        )


def create_weather_forecast_on_one_day(message: Message, bot: MyBot, user: User) -> None:
    if preferred_user_city := user.preferred_user_city:
        city = preferred_user_city.city
        weather_forecast = bot.services.weather_client.get_forecast_weather(
            geolocation=city, days=1
        )
        MessageBot.create_message_with_weather_forecast_on_one_day(
            message_chat_id=message.chat.id,
            bot=bot,
            city=city,
            day=weather_forecast.weather_on_day[0],
        )
    else:
        MessageBot.create_message_except_no_preferred_city(
            message_chat_id=message.chat.id, bot=bot, markup=MarkupBot.create_button_add_new_city()
        )


def create_weather_forecast_on_three_days(message: Message, bot: MyBot, user: User) -> None:
    if preferred_user_city := user.preferred_user_city:
        city = preferred_user_city.city
        forecast_weather = bot.services.weather_client.get_forecast_weather(
            geolocation=city, days=3
        )

        for day in forecast_weather.weather_on_day:
            MessageBot.create_message_with_weather_forecast_for_few_days(
                message_chat_id=message.chat.id,
                bot=bot,
                city=city,
                day=day,
            )
    else:
        MessageBot.create_message_except_no_preferred_city(
            message_chat_id=message.chat.id, bot=bot, markup=MarkupBot.create_button_add_new_city()
        )


def create_weather_forecast_on_seven_days(message: Message, bot: MyBot, user: User) -> None:
    if preferred_user_city := user.preferred_user_city:
        city = preferred_user_city.city
        forecast_weather = bot.services.weather_client.get_forecast_weather(
            geolocation=city, days=7
        )
        for day in forecast_weather.weather_on_day:
            MessageBot.create_message_with_weather_forecast_for_few_days(
                message_chat_id=message.chat.id,
                bot=bot,
                city=city,
                day=day,
            )
    else:
        MessageBot.create_message_except_no_preferred_city(
            message_chat_id=message.chat.id, bot=bot, markup=MarkupBot.create_button_add_new_city()
        )


def create_weather_forecast_on_fourteen_day(message: Message, bot: MyBot, user: User) -> None:
    if preferred_user_city := user.preferred_user_city:
        city = preferred_user_city.city
        forecast_weather = bot.services.weather_client.get_forecast_weather(
            geolocation=city, days=14
        )
        for day in forecast_weather.weather_on_day:
            MessageBot.create_message_with_weather_forecast_for_few_days(
                message_chat_id=message.chat.id,
                bot=bot,
                city=city,
                day=day,
            )
    else:
        MessageBot.create_message_except_no_preferred_city(
            message_chat_id=message.chat.id, bot=bot, markup=MarkupBot.create_button_add_new_city()
        )


def delete_city_user(message: Message, bot: MyBot, user: User) -> None:
    del user.city_associations[:-4]
    bot.services.uow.session.flush()
    markup = MarkupBot.create_buttons_with_cities_user(user=user)
    MessageBot.create_message_delete_city_user(
        message_chat_id=message.chat.id, bot=bot, markup=markup
    )


def handle_text(message: Message, bot: MyBot, user: User) -> None:
    message_list = message.text[:-1].split(" (")
    if len(message_list) == 2:
        city_name = message_list[0]
        country, district = message_list[1].split(", ")

        if city := bot.services.uow.cities.get_by_name_country_district(
            city=city_name, country=country, district=district
        ):
            if city not in (c for c in user.cities):
                user.city_associations.append(UserCity(city=city))
                bot.services.uow.session.flush()

            change_preferred_city(user=user, city_id=city.id, uow=bot.services.uow)

            MessageBot.create_message_with_preferred_city(
                message_chat_id=message.chat.id,
                markup=MarkupBot.create_buttons_for_days(),
                city_name=city_name.title(),
                country=country,
                district=district,
                bot=bot,
            )
        else:
            MessageBot.create_message_with_incomprehension(
                message_chat_id=message.chat.id,
                markup=MarkupBot.create_buttons_choose_another_city(),
                bot=bot,
            )

    else:
        MessageBot.create_message_with_incomprehension(
            message_chat_id=message.chat.id,
            markup=MarkupBot.create_buttons_choose_another_city(),
            bot=bot,
        )


def handle_any_content(message: Message, bot: MyBot, user: User) -> None:
    MessageBot.create_message_with_incomprehension(
        message_chat_id=message.chat.id,
        markup=MarkupBot.create_buttons_choose_another_city(),
        bot=bot,
    )


# @bot.callback_query_handler(func=lambda callback: True)
# def callback_message(callback):
#     with uow:

# class Foo(enum.StrEnum):
#     yes = enum.auto()
#     no = enum.auto()

# def create_inline_buttons(id_city: int):
#     dict1 = {"method": str(Foo.yes), "city": id_city}
#     dict2 = {"method": str(Foo.no), "city": id_city}
#     markup_inline = types.InlineKeyboardMarkup()
#     button_inline_1 = types.InlineKeyboardButton(
#         "Да",
#         callback_data=json.dumps(dict1),
#     )
#     button_inline_2 = types.InlineKeyboardButton(
#         "Нет",
#         callback_data=json.dumps(dict2),
#     )
#     markup_inline.row(button_inline_1, button_inline_2)
#     return markup_inline


# @bot.callback_query_handler(func=lambda callback: True)
# def callback_message(callback):
#     with uow:
#         req = callback.data.split("_")
#         json_string = json.loads(req[0])
#         city_id = json_string["city"]
#         city_name = uow.cities.get_by_id(city_id=city_id).name
#
#         cities = bot.services.geo_client.get_geolocation(city_name=city_name, language=language)
#         markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#         markup.add(*[types.KeyboardButton(city.name.title()) for city in cities], row_width=2)
#         markup.add(types.KeyboardButton("Выбрать другой город"))
#         bot.send_message(
#             chat_id=message.chat.id,
#             text=f"Ниже показаны варианты городов с названием {city_name.title()}.
#             Выберите, какой вам подходит",
#             reply_markup=markup,
#         )
#         bot.services.uow.session.add(city for city in cities)
# user.city_associations.append(UserCity(city=city))
# bot.services.uow.session.flush()


#         bot.edit_message_text(
#             text=f"Вы выбрали город {city_name}. Хотите сделать его основным?",
#             chat_id=callback.message.chat.id,
#             message_id=callback.message.message_id,
#         )
#
#         if json_string["method"] == Foo.yes:
#             bot.send_message(
#                 text=f"Вы хотите сделать город основным {city_name}",
#                 chat_id=callback.message.chat.id,
#             )
#             try:
#                 user_city_is_preferred = uow.user_city.get_is_preferred_city(
#                     user_id=callback.from_user.id
#                 )
#                 user_city_is_preferred.is_preferred = False
#
#             except NotFoundError:
#                 pass
#
#             finally:
#                 user_city = uow.user_city.get_by_id(
#                     user_id=callback.from_user.id, city_id=city_id)
#                 user_city.is_preferred = True
#
#         elif json_string["method"] == Foo.no:
#             bot.send_message(
#                 text=f"Вы не хотите сделать город основным {city_name}",
#                 chat_id=callback.message.chat.id,
#             )
#         else:
#             ZeroDivisionError()
#
