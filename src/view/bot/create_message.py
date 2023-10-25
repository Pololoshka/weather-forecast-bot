from datetime import datetime

from telebot.types import ReplyKeyboardMarkup

from src.const_api import WEATHER_CODES
from src.models.models_for_db import City
from src.models.query_models_api import CurrentWeather, WeatherOnDay
from src.services.ui.bot import MyBot


class MessageBot:
    @staticmethod
    def create_start_message(message_chat_id: int, markup: ReplyKeyboardMarkup, bot: MyBot) -> None:
        bot.send_message(
            chat_id=message_chat_id,
            text="Привет, дорогой друг! "
            "Я чат-бот, который расскажет тебе, какая погода за окном. "
            "Снизу ты видишь кнопки с городами, которые ты раньше добавлял. "
            "Выбери, какой для тебя на данный момент город актуален. "
            "Если ты первый раз, то нажимай на кнопку добавить город",
            reply_markup=markup,
        )

    @staticmethod
    def create_message_with_input_new_city(message_chat_id: int, bot: MyBot) -> None:
        bot.send_message(chat_id=message_chat_id, text="Введите название города")

    @staticmethod
    def create_message_with_preferred_city(
        message_chat_id: int,
        city_name: str,
        country: str,
        district: str,
        markup: ReplyKeyboardMarkup,
        bot: MyBot,
    ) -> None:
        bot.send_message(
            chat_id=message_chat_id,
            text=(
                f"Вы выбрали город {city_name.title()} ({country}, {district}). "
                f"Выберите, за какое время хотите получить прогноз"
            ),
            reply_markup=markup,
        )

    @staticmethod
    def create_message_wrong_city(
        message_chat_id: int, markup: ReplyKeyboardMarkup, bot: MyBot
    ) -> None:
        bot.send_message(
            chat_id=message_chat_id,
            text="Извините, такого города не существует. \n Проверьте, правильно ли вы написали.",
            reply_markup=markup,
        )

    @staticmethod
    def create_message_choose_another_city(
        message_chat_id: int, markup: ReplyKeyboardMarkup, bot: MyBot
    ) -> None:
        bot.send_message(
            chat_id=message_chat_id,
            text="Выберите интересующий город или добавьте новый",
            reply_markup=markup,
        )

    @staticmethod
    def create_message_with_incomprehension(
        message_chat_id: int, markup: ReplyKeyboardMarkup, bot: MyBot
    ) -> None:
        bot.send_message(
            chat_id=message_chat_id,
            text="Извините, я вас не поминаю. Пожалуйста, следуйте кнопкам на клавиатуре",
            reply_markup=markup,
        )

    @staticmethod
    def create_message_with_current_weather(
        message_chat_id: int,
        bot: MyBot,
        date: datetime,
        city: City,
        current_weather: CurrentWeather,
    ) -> None:
        bot.send_message(
            chat_id=message_chat_id,
            text=(
                f"Сейчас {date.strftime('%H:%M %d.%m.%Y')} "
                f"в городе {city.name.title()} {int(current_weather.temp)}°. \n"
                f"{WEATHER_CODES[current_weather.condition][city.language]}"
            ),
        )

    @staticmethod
    def create_message_with_weather_forecast_on_one_day(
        message_chat_id: int,
        bot: MyBot,
        city: City,
        day: WeatherOnDay,
    ) -> None:
        bot.send_message(
            chat_id=message_chat_id,
            text=(
                f"Сегодня {day.date.strftime('%d.%m.%Y')} "
                f"в городе {city.name.title()} \n"
                f"максимальная температура {int(day.temp_max)}°, "
                f"а минимальная {int(day.temp_min)}°. \n"
                f"{WEATHER_CODES[day.condition][city.language]}"
            ),
        )

    @staticmethod
    def create_message_with_weather_forecast_for_few_days(
        message_chat_id: int, bot: MyBot, city: City, day: WeatherOnDay
    ) -> None:
        bot.send_message(
            chat_id=message_chat_id,
            text=(
                f"• {day.date.strftime('%d.%m.%Y')} "
                f"в городе {city.name.title()} \n"
                f"максимальная температура {int(day.temp_max)}°, "
                f"а минимальная {int(day.temp_min)}°. \n"
                f"{WEATHER_CODES[day.condition][city.language]} \n"
            ),
        )

    @staticmethod
    def create_message_with_new_cities(
        message_chat_id: int, bot: MyBot, city_name: str, markup: ReplyKeyboardMarkup
    ) -> None:
        bot.send_message(
            chat_id=message_chat_id,
            text=f"Ниже показаны варианты городов с названием {city_name.title()}. "
            f"Выберите, какой вам подходит",
            reply_markup=markup,
        )

    @staticmethod
    def create_message_delete_city_user(
        message_chat_id: int, bot: MyBot, markup: ReplyKeyboardMarkup
    ) -> None:
        bot.send_message(
            chat_id=message_chat_id,
            text="Я почистил историю поиска и оставил 4 последних города. "
            "Нажимайте на нужную кнопку для дальнейшей работы",
            reply_markup=markup,
        )

    @staticmethod
    def create_message_except_no_preferred_city(
        message_chat_id: int, bot: MyBot, markup: ReplyKeyboardMarkup
    ) -> None:
        bot.send_message(
            chat_id=message_chat_id,
            text="У вас пока нет ни одного города. Пожалуйста, добавьте новый город",
            reply_markup=markup,
        )
