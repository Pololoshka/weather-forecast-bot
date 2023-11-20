import os
from dataclasses import dataclass, field, fields
from typing import Self

from dotenv import load_dotenv


@dataclass
class Settings:
    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    token_telebot: str
    log_level: str
    weather_url: str = field(default="https://api.open-meteo.com/v1/forecast")
    geolocation_url: str = field(default="https://geocoding-api.open-meteo.com/v1/search")
    timeout: int = field(default=5)

    @classmethod
    def from_environ(cls, dotenv_path: str | None = None) -> Self:
        load_dotenv(dotenv_path)
        return cls(
            **{
                field_.name: field_.type(value)  # FIXME: ONLY simple types
                for field_ in fields(cls)
                if (value := os.environ.get(field_.name.upper()))
            }
        )
