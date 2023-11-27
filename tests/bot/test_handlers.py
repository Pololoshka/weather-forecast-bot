from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol
from unittest.mock import MagicMock, call

import pytest
from pytest_mock import MockFixture
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.bot.bot import Bot
from src.bot.handlers import (
    _add_new_cities_in_bd,
    _change_preferred_city,
    add_new_city,
    choose_another_city,
    create_current_weather_forecast,
    create_weather_forecast_on_fourteen_day,
    create_weather_forecast_on_one_day,
    create_weather_forecast_on_seven_days,
    create_weather_forecast_on_three_days,
    delete_city_user,
    handle_any_content,
    handle_text,
    on_click,
    process_message_with_city,
    start,
)
from src.bot.messages import ReplyMessage
from src.services.db.models import City, User, UserCity
from src.services.db.uow import SqlAlchemyUnitOfWork
from src.services.geolocation.client import GeolocationClient
from src.services.weather.client import WeatherClient
from src.services.weather.models import CurrentWeather, WeatherForecast, WeatherOnDay


class AttrGenerator(Protocol):
    def __call__(self, text: str = "hello") -> dict:
        ...


@pytest.fixture()
def bot(mocker: MockFixture, uow: SqlAlchemyUnitOfWork) -> MagicMock:
    bot = mocker.MagicMock(spec=Bot)
    bot.return_value.services.uow = uow
    bot.return_value.services.geo_client = mocker.MagicMock(spec=GeolocationClient)
    bot.return_value.services.weather_client = mocker.MagicMock(spec=WeatherClient)
    return bot.return_value  # type: ignore


@pytest.fixture()
def reply(mocker: MockFixture) -> MagicMock:
    return mocker.MagicMock(spec=ReplyMessage).return_value  # type: ignore


@dataclass
class Message:
    text: str
    date: int = field(default=1323456464)


@pytest.fixture()
def get_dict_attr(bot: MagicMock, user: User, reply: MagicMock) -> AttrGenerator:
    def wrapper(text: str = "санкт-петербург") -> dict:
        return {
            "bot": bot,
            "user": user,
            "message": Message(text=text),
            "reply": reply,
        }

    return wrapper


def test_start(get_dict_attr: AttrGenerator, reply: MagicMock) -> None:
    start(**get_dict_attr())
    reply.create_start_message.assert_called_once()


def test_add_new_city(get_dict_attr: AttrGenerator, reply: MagicMock, bot: MagicMock) -> None:
    add_new_city(**get_dict_attr())
    reply.create_message_with_input_new_city.assert_called_once()
    bot.register_next_step_handler.assert_called_once()


def test_on_click__if_city_in_db(
    get_dict_attr: AttrGenerator,
    reply: MagicMock,
    city_1: City,
) -> None:
    on_click(**get_dict_attr())
    reply.create_message_with_new_cities.assert_called_once_with(
        city_name=city_1.name, cities=[city_1]
    )


def test_on_click__if_city_not_in_db(
    get_dict_attr: AttrGenerator,
    reply: MagicMock,
    bot: MagicMock,
    session: Session,
) -> None:
    expected_city = [
        City(
            latitude=59.93863,
            longitude=30.31413,
            timezone="Europe/Moscow",
            name="санкт-петербург",
            country="Россия",
            district="Санкт-Петербург",
        )
    ]
    bot.services.geo_client.get_geolocation.return_value = expected_city

    on_click(**get_dict_attr())
    cities = session.scalars(select(City).where(City.name == "санкт-петербург")).all()

    reply.create_message_with_new_cities.assert_called_once_with(
        city_name=expected_city[0].name, cities=cities
    )


def test_on_click__if_city_not_in_geo(
    get_dict_attr: AttrGenerator,
    reply: MagicMock,
    bot: MagicMock,
) -> None:
    bot.services.geo_client.get_geolocation.return_value = None
    on_click(**get_dict_attr(text="abracadabra"))
    reply.create_message_wrong_city.assert_called_once()


def test_choose_another_city(get_dict_attr: AttrGenerator, reply: MagicMock) -> None:
    choose_another_city(**get_dict_attr())
    reply.create_message_choose_another_city.assert_called_once()


def test_create_current_weather_forecast_with_preferred_city(
    get_dict_attr: AttrGenerator,
    reply: MagicMock,
    user_city_with_preferred_city: UserCity,
    bot: MagicMock,
    city_1: City,
) -> None:
    message = Message(text="hello")
    current_weather = CurrentWeather(
        temp=24.5,
        condition=0,
        date=datetime.fromtimestamp(message.date, tz=UTC),
    )
    bot.services.weather_client.get_current_weather.return_value = current_weather
    create_current_weather_forecast(**get_dict_attr())
    reply.create_message_with_current_weather.assert_called_once_with(
        date=datetime.fromtimestamp(message.date, tz=UTC),
        city=city_1,
        current_weather=current_weather,
    )


def test_create_current_weather_forecast_without_preferred_city(
    get_dict_attr: AttrGenerator,
    reply: MagicMock,
) -> None:
    create_current_weather_forecast(**get_dict_attr())
    reply.create_message_except_no_preferred_city.assert_called_once()


def test_create_weather_forecast_on_one_day_with_preferred_city(
    get_dict_attr: AttrGenerator,
    reply: MagicMock,
    user_city_with_preferred_city: UserCity,
    bot: MagicMock,
    city_1: City,
) -> None:
    weather_forecast = WeatherForecast(
        weather_on_day=[
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-17"), temp_max=24.5, temp_min=20.1, condition=3
            ),
        ]
    )
    bot.services.weather_client.get_forecast_weather.return_value = weather_forecast
    create_weather_forecast_on_one_day(**get_dict_attr())
    reply.create_message_with_weather_forecast_on_one_day.assert_called_once_with(
        city=city_1,
        day=weather_forecast.weather_on_day[0],
    )


def test_create_weather_forecast_on_one_day_without_preferred_city(
    get_dict_attr: AttrGenerator,
    reply: MagicMock,
) -> None:
    create_weather_forecast_on_one_day(**get_dict_attr())
    reply.create_message_except_no_preferred_city.assert_called_once()


def test_create_weather_forecast_on_three_days_with_preferred_city(
    get_dict_attr: AttrGenerator,
    reply: MagicMock,
    user_city_with_preferred_city: UserCity,
    bot: MagicMock,
    city_1: City,
) -> None:
    weather_forecast = WeatherForecast(
        weather_on_day=[
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-17"), temp_max=24.5, temp_min=20.1, condition=3
            ),
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-18"), temp_max=24.5, temp_min=20.1, condition=3
            ),
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-19"), temp_max=24.5, temp_min=20.1, condition=3
            ),
        ]
    )
    bot.services.weather_client.get_forecast_weather.return_value = weather_forecast
    create_weather_forecast_on_three_days(**get_dict_attr())
    assert reply.create_message_with_weather_forecast_for_few_days.call_count == 3
    reply.create_message_with_weather_forecast_for_few_days.assert_has_calls(
        calls=[
            call(city=city_1, day=weather_forecast.weather_on_day[0]),
            call(city=city_1, day=weather_forecast.weather_on_day[1]),
            call(city=city_1, day=weather_forecast.weather_on_day[2]),
        ]
    )


def test_create_weather_forecast_on_three_days_without_preferred_city(
    get_dict_attr: AttrGenerator,
    reply: MagicMock,
) -> None:
    create_weather_forecast_on_three_days(**get_dict_attr())
    reply.create_message_except_no_preferred_city.assert_called_once()


def test_create_weather_forecast_on_seven_days_with_preferred_city(
    get_dict_attr: AttrGenerator,
    reply: MagicMock,
    user_city_with_preferred_city: UserCity,
    bot: MagicMock,
    city_1: City,
) -> None:
    weather_forecast = WeatherForecast(
        weather_on_day=[
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-17"), temp_max=24.5, temp_min=20.1, condition=3
            ),
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-18"), temp_max=24.5, temp_min=20.1, condition=3
            ),
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-19"), temp_max=24.5, temp_min=20.1, condition=3
            ),
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-20"), temp_max=24.5, temp_min=20.1, condition=3
            ),
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-21"), temp_max=24.5, temp_min=20.1, condition=3
            ),
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-22"), temp_max=24.5, temp_min=20.1, condition=3
            ),
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-23"), temp_max=24.5, temp_min=20.1, condition=3
            ),
        ]
    )
    bot.services.weather_client.get_forecast_weather.return_value = weather_forecast
    create_weather_forecast_on_seven_days(**get_dict_attr())
    assert reply.create_message_with_weather_forecast_for_few_days.call_count == 7
    reply.create_message_with_weather_forecast_for_few_days.assert_has_calls(
        calls=[
            call(city=city_1, day=weather_forecast.weather_on_day[0]),
            call(city=city_1, day=weather_forecast.weather_on_day[1]),
            call(city=city_1, day=weather_forecast.weather_on_day[2]),
            call(city=city_1, day=weather_forecast.weather_on_day[3]),
            call(city=city_1, day=weather_forecast.weather_on_day[4]),
            call(city=city_1, day=weather_forecast.weather_on_day[5]),
            call(city=city_1, day=weather_forecast.weather_on_day[6]),
        ]
    )


def test_create_weather_forecast_on_seven_days_without_preferred_city(
    get_dict_attr: AttrGenerator,
    reply: MagicMock,
) -> None:
    create_weather_forecast_on_seven_days(**get_dict_attr())
    reply.create_message_except_no_preferred_city.assert_called_once()


def test_create_weather_forecast_on_fourteen_day_with_preferred_city(
    get_dict_attr: AttrGenerator,
    reply: MagicMock,
    user_city_with_preferred_city: UserCity,
    bot: MagicMock,
    city_1: City,
) -> None:
    weather_forecast = WeatherForecast(
        weather_on_day=[
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-17"), temp_max=24.5, temp_min=20.1, condition=3
            ),
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-18"), temp_max=24.5, temp_min=20.1, condition=3
            ),
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-19"), temp_max=24.5, temp_min=20.1, condition=3
            ),
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-20"), temp_max=24.5, temp_min=20.1, condition=3
            ),
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-21"), temp_max=24.5, temp_min=20.1, condition=3
            ),
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-22"), temp_max=24.5, temp_min=20.1, condition=3
            ),
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-23"), temp_max=24.5, temp_min=20.1, condition=3
            ),
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-24"), temp_max=24.5, temp_min=20.1, condition=3
            ),
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-25"), temp_max=24.5, temp_min=20.1, condition=3
            ),
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-26"), temp_max=24.5, temp_min=20.1, condition=3
            ),
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-27"), temp_max=24.5, temp_min=20.1, condition=3
            ),
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-28"), temp_max=24.5, temp_min=20.1, condition=3
            ),
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-29"), temp_max=24.5, temp_min=20.1, condition=3
            ),
            WeatherOnDay(
                date=datetime.fromisoformat("2023-08-30"), temp_max=24.5, temp_min=20.1, condition=3
            ),
        ]
    )
    bot.services.weather_client.get_forecast_weather.return_value = weather_forecast
    create_weather_forecast_on_fourteen_day(**get_dict_attr())
    assert reply.create_message_with_weather_forecast_for_few_days.call_count == 14
    reply.create_message_with_weather_forecast_for_few_days.assert_has_calls(
        calls=[
            call(city=city_1, day=weather_forecast.weather_on_day[0]),
            call(city=city_1, day=weather_forecast.weather_on_day[1]),
            call(city=city_1, day=weather_forecast.weather_on_day[2]),
            call(city=city_1, day=weather_forecast.weather_on_day[3]),
            call(city=city_1, day=weather_forecast.weather_on_day[4]),
            call(city=city_1, day=weather_forecast.weather_on_day[5]),
            call(city=city_1, day=weather_forecast.weather_on_day[6]),
            call(city=city_1, day=weather_forecast.weather_on_day[7]),
            call(city=city_1, day=weather_forecast.weather_on_day[8]),
            call(city=city_1, day=weather_forecast.weather_on_day[9]),
            call(city=city_1, day=weather_forecast.weather_on_day[10]),
            call(city=city_1, day=weather_forecast.weather_on_day[11]),
            call(city=city_1, day=weather_forecast.weather_on_day[12]),
            call(city=city_1, day=weather_forecast.weather_on_day[13]),
        ]
    )


def test_create_weather_forecast_on_fourteen_day_without_preferred_city(
    get_dict_attr: AttrGenerator,
    reply: MagicMock,
) -> None:
    create_weather_forecast_on_fourteen_day(**get_dict_attr())
    reply.create_message_except_no_preferred_city.assert_called_once()


def test_delete_city_user(
    get_dict_attr: AttrGenerator,
    reply: MagicMock,
    city_1: City,
    city_2: City,
    city_3: City,
    city_4: City,
    city_5: City,
    user: User,
    session: Session,
) -> None:
    user.city_associations.extend(
        [
            UserCity(city=city_1),
            UserCity(city=city_2),
            UserCity(city=city_3),
            UserCity(city=city_4),
            UserCity(city=city_5),
        ]
    )
    session.flush()
    delete_city_user(**get_dict_attr())
    expected = session.scalars(select(City).join(UserCity).where(UserCity.user_id == user.id)).all()
    assert len(expected) == 4
    reply.create_message_delete_city_user.assert_called_once_with(user=user)


def test_process_message_with_city__not_city(
    get_dict_attr: AttrGenerator, reply: MagicMock
) -> None:
    process_message_with_city(**get_dict_attr(text="Bla (BlaBla, Bla)"))
    reply.create_message_with_incomprehension.assert_called_once()


def test_process_message_with_city__not_city_in_user(
    get_dict_attr: AttrGenerator,
    reply: MagicMock,
    user: User,
    city_2: City,
    session: Session,
) -> None:
    process_message_with_city(**get_dict_attr(text="Москва (Россия, Москва)"))
    user_city = session.scalar(
        select(UserCity).where(UserCity.user_id == user.id, UserCity.city_id == city_2.id)
    )
    assert user_city
    assert user_city.is_preferred is True
    reply.create_message_with_preferred_city.assert_called_once_with(city=city_2)


def test_handle_text(get_dict_attr: AttrGenerator, reply: MagicMock) -> None:
    handle_text(**get_dict_attr())
    reply.create_message_with_incomprehension.assert_called_once()


def test_handle_any_content(get_dict_attr: AttrGenerator, reply: MagicMock) -> None:
    handle_any_content(**get_dict_attr())
    reply.create_message_with_incomprehension.assert_called_once()


def test__add_new_cities_in_bd(
    mocker: MockFixture,
    session: Session,
    city_1: City,
    city_2: City,
    uow: SqlAlchemyUnitOfWork,
) -> None:
    cities = [city_1, city_2]
    bot = mocker.MagicMock()
    bot.services.uow = uow

    _add_new_cities_in_bd(bot=bot, cities=cities)
    expected_1 = session.scalar(
        select(City).where(
            City.name == city_1.name,
            City.country == city_1.country,
            City.district == city_1.district,
        )
    )
    assert city_1 == expected_1

    expected_2 = session.scalar(
        select(City).where(
            City.name == city_2.name,
            City.country == city_2.country,
            City.district == city_2.district,
        )
    )
    assert city_2 == expected_2


def test__change_preferred_city(
    session: Session,
    uow: SqlAlchemyUnitOfWork,
    user: User,
    city_1: City,
    city_2: City,
) -> None:
    user.city_associations.append(UserCity(city=city_1, is_preferred=True))
    user.city_associations.append(UserCity(city=city_2))
    session.flush()

    _change_preferred_city(user=user, city_id=city_2.id, uow=uow)

    expected = session.scalar(
        select(City)
        .join(UserCity)
        .where(UserCity.user_id == user.id, UserCity.is_preferred.is_(True))
    )
    assert city_2 == expected
