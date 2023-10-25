from collections.abc import Sequence

from telebot import types
from telebot.types import ReplyKeyboardMarkup

from src.models.models_for_db import City, User
from src.services.ui.const_ui import Text


class MarkupBot:
    @staticmethod
    def create_buttons_for_days() -> ReplyKeyboardMarkup:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(types.KeyboardButton(Text.now), row_width=1)
        markup.add(
            types.KeyboardButton(Text.one_day),
            types.KeyboardButton(Text.three_days),
            types.KeyboardButton(Text.seven_days),
            types.KeyboardButton(Text.fourteen_days),
        )
        markup.add(types.KeyboardButton(Text.choose_city), row_width=1)
        return markup

    @staticmethod
    def create_buttons_with_cities_user(user: User) -> ReplyKeyboardMarkup:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(types.KeyboardButton(Text.add_city), row_width=1)
        if len(user.city_associations) > 4:
            markup.add(
                types.KeyboardButton("Очистить историю поиска🗑 \n(оставлю 4 последних города)"),
                row_width=1,
            )
        markup.add(
            *[
                types.KeyboardButton(f"{city.name.title()} ({city.country}, {city.district})")
                for city in user.cities
            ],
            row_width=2,
        )

        return markup

    @staticmethod
    def create_buttons_with_new_cities(cities: Sequence[City]) -> ReplyKeyboardMarkup:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

        markup.add(
            *[
                types.KeyboardButton(f"{city.name.title()} ({city.country}, {city.district})")
                for city in cities
            ],
            row_width=2,
        )
        markup.add(types.KeyboardButton(Text.choose_city), row_width=1)

        return markup

    @staticmethod
    def create_buttons_choose_another_city() -> ReplyKeyboardMarkup:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton(Text.choose_city))
        return markup

    @staticmethod
    def create_button_add_new_city() -> ReplyKeyboardMarkup:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton(Text.add_city))
        return markup
