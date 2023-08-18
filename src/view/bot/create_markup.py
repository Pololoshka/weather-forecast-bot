from telebot import types
from telebot.types import ReplyKeyboardMarkup

from src.models import User


class MarkupBot:
    @staticmethod
    def create_buttons_for_days() -> ReplyKeyboardMarkup:
        markup_with_days = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_1 = types.KeyboardButton("Сейчас")
        button_2 = types.KeyboardButton("На 1 день")
        button_3 = types.KeyboardButton("На 3 дня")
        button_4 = types.KeyboardButton("На 7 дней")
        button_5 = types.KeyboardButton("На 14 дней")
        button_6 = types.KeyboardButton("Выбрать другой город")
        markup_with_days.row(button_1)
        markup_with_days.row(button_2, button_3)
        markup_with_days.row(button_4, button_5)
        markup_with_days.row(button_6)
        return markup_with_days

    @staticmethod
    def create_buttons_with_cities(user: User) -> ReplyKeyboardMarkup:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Добавить новый город"))
        for city in user.cities:
            markup.add(types.KeyboardButton(city.name))
        return markup

    @staticmethod
    def create_buttons_choose_another_city() -> ReplyKeyboardMarkup:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Выбрать другой город"))
        return markup
