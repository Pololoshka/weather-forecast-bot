import enum
from datetime import datetime

from src.services.db.models import City
from src.services.weather.const import WEATHER_CODES
from src.services.weather.models import CurrentWeather, WeatherOnDay


class Command(enum.StrEnum):
    start = "start"


class Text:
    add_city = "🌍 Добавить новый город"
    choose_city = "🌉 Выбрать другой город"
    now = "✔️ Сейчас"
    one_day = "✔️ На 1 день"
    three_days = "✔️ На 3 дня"
    seven_days = "✔️ На 7 дней"
    fourteen_days = "✔️ На 14 дней"
    delete = "🗑 Очистить историю поиска\n(оставлю 4 последних города)"
    start = (
        "Привет, дорогой друг🤚\nЯ расскажу тебе, какая погода за окном 🌦\n"
        "Снизу ты видишь кнопки с городами, которые ты раньше добавлял 👇 "
        "Выбери, какой для тебя на данный момент город актуален."
        "Если ты первый раз, то нажимай на кнопку добавить город 🌍"
    )
    input_new_city = "Введите название города✒️"
    wrong_city = "Tакого города не существует 🤷\n Проверьте, правильно ли вы написали 🤔"
    choose_or_add = "Выберите интересующий город или добавьте новый 👇 "
    incomprehension = "Извините, я вас не поминаю 🤷 Пожалуйста, следуйте кнопкам на клавиатуре 👇"
    no_preferred_city = "У вас пока нет ни одного города ✖️ Пожалуйста, добавьте новый город🌇"
    after_delete = (
        "Я почистил историю поиска и оставил 4 последних города. "
        "Нажимайте на нужную кнопку для дальнейшей работы 👇"
    )
    exc_geolocation = "Сервер поиска геолокации не отвечает ✖️"
    exc_weather = "Сервер поиска прогноза погоды не отвечает ✖️"

    city_template = "{city} ({country}, {district})"
    city_regex = r"(?P<city>.+) \((?P<country>.+), (?P<district>.+)\)"

    @staticmethod
    def message_exc(err: str) -> str:
        return f"Упс, что-то пошло не так 🫣\n{err}\nПопробуйте снова 👇"

    @classmethod
    def text_button_with_city(cls, city: City) -> str:
        return cls.city_template.format(
            city=city.name.title(),
            country=city.country,
            district=city.district,
        )

    @classmethod
    def text_selected_city(cls, city: City) -> str:
        return (
            f"Вы выбрали город {cls.text_button_with_city(city)} 🌃\n"
            f"Выберите, за какое время хотите получить прогноз 📅"
        )

    @staticmethod
    def text_current_weather(
        date: datetime,
        city: City,
        current_weather: CurrentWeather,
    ) -> str:
        return (
            f"Сейчас {date.strftime('%H:%M %d.%m.%Y')} "
            f"в городе {city.name.title()} {int(current_weather.temp)}° 🌇\n"
            f"{WEATHER_CODES[current_weather.condition][city.language]}"
        )

    @staticmethod
    def text_weather_today(city: City, day: WeatherOnDay) -> str:
        return (
            f"Сегодня {day.date.strftime('%d.%m.%Y')} в городе {city.name.title()} 🌇\n"
            f"максимальная температура {int(day.temp_max)}°, а минимальная {int(day.temp_min)}°.\n"
            f"{WEATHER_CODES[day.condition][city.language]}"
        )

    @staticmethod
    def text_weather_for_few_days(city: City, day: WeatherOnDay) -> str:
        return (
            f"• {day.date.strftime('%d.%m.%Y')} в городе {city.name.title()} 🌇\n"
            f"максимальная температура {int(day.temp_max)}°, а минимальная {int(day.temp_min)}°.\n"
            f"{WEATHER_CODES[day.condition][city.language]}"
        )

    @staticmethod
    def text_with_new_cities(city_name: str) -> str:
        return (
            f"Ниже показаны варианты городов с названием {city_name.title()}."
            f"Выберите, какой вам подходит 👇"
        )


class MessageType(enum.StrEnum):
    text = "text"
    any = "any"
