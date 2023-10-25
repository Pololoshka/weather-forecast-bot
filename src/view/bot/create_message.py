from collections.abc import Sequence
from datetime import datetime

from telebot import types

from src.models.models_for_db import City, User
from src.models.query_models_api import CurrentWeather, WeatherOnDay
from src.services.ui.bot import MyBot
from src.services.ui.const_ui import Text


class MessageBot:
    def __init__(self, chat_id: int, bot: MyBot):
        self.chat_id = chat_id
        self.markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        self.bot = bot

    def create_buttons_choose_another_city(self) -> None:
        self.markup.add(types.KeyboardButton(Text.choose_city), row_width=1)

    def create_button_add_new_city(self) -> None:
        self.markup.add(types.KeyboardButton(Text.add_city), row_width=1)

    def create_buttons_for_days(self) -> None:
        self.markup.add(types.KeyboardButton(Text.now), row_width=1)
        self.markup.add(
            types.KeyboardButton(Text.one_day),
            types.KeyboardButton(Text.three_days),
            types.KeyboardButton(Text.seven_days),
            types.KeyboardButton(Text.fourteen_days),
        )
        self.create_buttons_choose_another_city()

    def create_buttons_with_cities_user(self, user: User) -> None:
        self.create_button_add_new_city()
        if len(user.city_associations) > 4:
            self.markup.add(
                types.KeyboardButton(Text.delete),
                row_width=1,
            )
        self.markup.add(
            *[types.KeyboardButton(Text.text_button_with_city(city=city)) for city in user.cities]
        )

    def create_buttons_with_new_cities(self, cities: Sequence[City]) -> None:
        self.markup.add(
            *[types.KeyboardButton(Text.text_button_with_city(city=city)) for city in cities]
        )
        self.create_buttons_choose_another_city()

    def create_any_message(self, text: str) -> None:
        self.bot.send_message(
            chat_id=self.chat_id,
            text=text,
            reply_markup=self.markup,
        )

    def create_start_message(self, user: User) -> None:
        self.create_buttons_with_cities_user(user=user)
        self.create_any_message(text=Text.start)

    def create_message_with_input_new_city(self) -> None:
        self.create_any_message(text=Text.input_new_city)

    def create_message_with_preferred_city(
        self,
        city: City,
    ) -> None:
        self.create_buttons_for_days()
        self.create_any_message(text=Text.text_selected_city(city=city))

    def create_message_wrong_city(self, user: User) -> None:
        self.create_buttons_with_cities_user(user=user)
        self.create_any_message(text=Text.wrong_city)

    def create_message_choose_another_city(self, user: User) -> None:
        self.create_buttons_with_cities_user(user=user)
        self.create_any_message(text=Text.choose_or_add)

    def create_message_with_incomprehension(self) -> None:
        self.create_buttons_choose_another_city()
        self.create_any_message(text=Text.incomprehension)

    def create_message_with_current_weather(
        self,
        date: datetime,
        city: City,
        current_weather: CurrentWeather,
    ) -> None:
        self.create_buttons_for_days()
        self.create_any_message(
            text=Text.text_current_weather(date=date, city=city, current_weather=current_weather)
        )

    def create_message_with_weather_forecast_on_one_day(
        self,
        city: City,
        day: WeatherOnDay,
    ) -> None:
        self.create_buttons_for_days()
        self.create_any_message(text=Text.text_weather_today(city=city, day=day))

    def create_message_with_weather_forecast_for_few_days(
        self, city: City, day: WeatherOnDay
    ) -> None:
        self.create_buttons_for_days()
        self.create_any_message(text=Text.text_weather_for_few_days(city=city, day=day))

    def create_message_with_new_cities(self, city_name: str, cities: Sequence[City]) -> None:
        self.create_buttons_with_new_cities(cities=cities)
        self.create_any_message(text=Text.text_with_new_cities(city_name=city_name))

    def create_message_delete_city_user(self, user: User) -> None:
        self.create_buttons_with_cities_user(user=user)
        self.create_any_message(text=Text.after_delete)

    def create_message_except_no_preferred_city(self) -> None:
        self.create_button_add_new_city()
        self.create_any_message(text=Text.no_preferred_city)
