import telebot
from telebot.types import Message

from src.errors import NotFoundError
from src.models import City
from src.regular_expressions import input_language_definitions
from src.services.db.uow import SqlAlchemyUnitOfWork, create_url
from src.services.geolocation_client import GeolocationClient
from src.services.ui.constants import Commands
from src.settings import Settings
from src.view.bot.chahge_preferred_city_user import change_preferred_city
from src.view.bot.create_markup import MarkupBot
from src.view.bot.create_message import MessageBot

bot = telebot.TeleBot(token=Settings.from_environ().token_telebot)
url_ = create_url(settings=Settings.from_environ())
uow = SqlAlchemyUnitOfWork.get_session(url=url_)


@bot.message_handler(commands=[Commands.start])
def start(message: Message) -> None:
    with uow:
        try:
            user = uow.users.get(user_id=message.from_user.id)
        except NotFoundError:
            uow.users.create(user_id=message.from_user.id, first_name=message.from_user.first_name)
            user = uow.users.get(user_id=message.from_user.id)

        markup = MarkupBot.create_buttons_with_cities(user=user)
        MessageBot.create_start_message(message_chat_id=message.chat.id, markup=markup, bot=bot)


@bot.message_handler(func=lambda message: message.text == "Добавить новый город")
def add_new_city(message):
    MessageBot.create_message_with_input_new_city(message_chat_id=message.chat.id, bot=bot)
    bot.register_next_step_handler(message=message, callback=on_click)


def on_click(message):
    with uow:
        user = uow.users.get(user_id=message.from_user.id)
        language = input_language_definitions(message.text)
        city_name = message.text.lower()

        try:
            city_in_bd = uow.cities.get_by_name(city=city_name)
            user.cities.append(city_in_bd)
            change_preferred_city(user_id=user.id, city_id=city_in_bd.id, uow=uow)
            MessageBot.create_message_with_preferred_city(
                message_chat_id=message.chat.id,
                city_name=city_name,
                markup=MarkupBot.create_buttons_for_days(),
                bot=bot,
            )

        except NotFoundError:
            try:
                GeolocationClient(
                    url=Settings.geolocation_url,
                    timeout=Settings.timeout,
                ).get_geolocation(city=city_name, language=language)
                city = City(name=message.text)
                uow.session.add(city)
                user.cities.append(city)
                uow.session.flush()

                change_preferred_city(user_id=user.id, city_id=city.id, uow=uow)
                MessageBot.create_message_with_preferred_city(
                    message_chat_id=message.chat.id,
                    city_name=city_name,
                    markup=MarkupBot.create_buttons_for_days(),
                    bot=bot,
                )

            except KeyError:
                MessageBot.create_message_wrong_city(
                    message_chat_id=message.chat.id,
                    markup=MarkupBot.create_buttons_with_cities(user=user),
                    bot=bot,
                )


@bot.message_handler(func=lambda message: message.text == "Выбрать другой город")
def choose_another_city(message):
    with uow:
        user = uow.users.get(user_id=message.from_user.id)
        MessageBot.create_message_choose_another_city(
            message_chat_id=message.chat.id,
            markup=MarkupBot.create_buttons_with_cities(user=user),
            bot=bot,
        )


@bot.message_handler(content_types=["text"])
def foo(message):
    with uow:
        user = uow.users.get(user_id=message.from_user.id)
        cities = [city.name for city in user.cities]
        city_name = message.text.title()

        if city_name in cities:
            city_id = uow.cities.get_by_name(city=city_name).id
            change_preferred_city(user_id=user.id, city_id=city_id, uow=uow)

            MessageBot.create_message_with_preferred_city(
                message_chat_id=message.chat.id,
                markup=MarkupBot.create_buttons_for_days(),
                city_name=city_name,
                bot=bot,
            )

        else:
            MessageBot.create_message_with_incomprehension(
                message_chat_id=message.chat.id,
                markup=MarkupBot.create_buttons_choose_another_city(),
                bot=bot,
            )


bot.polling(none_stop=True)

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
