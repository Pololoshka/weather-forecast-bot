from dataclasses import dataclass
from datetime import datetime
from typing import Self


@dataclass
class WeatherOnDay:
    date: datetime
    temp_max: float
    temp_min: float
    condition: int


@dataclass
class CurrentWeather:
    temp: float
    condition: int
    date: datetime

    @classmethod
    def parse(cls, data: dict) -> Self:
        return cls(
            temp=data["temperature"],
            condition=data["weathercode"],
            date=datetime.fromisoformat(data["time"]),
        )


@dataclass
class WeatherForecast:
    weather_on_day: list[WeatherOnDay]

    @classmethod
    def parse(cls, data: dict) -> Self:
        list_date = data["time"]
        list_temp_max = data["temperature_2m_max"]
        list_temp_min = data["temperature_2m_min"]
        list_condition_code = data["weathercode"]

        return cls(
            weather_on_day=[
                WeatherOnDay(
                    date=datetime.fromisoformat(date),
                    temp_max=temp_max,
                    temp_min=temp_min,
                    condition=condition,
                )
                for date, temp_max, temp_min, condition in zip(
                    list_date, list_temp_max, list_temp_min, list_condition_code, strict=False
                )
            ],
        )
