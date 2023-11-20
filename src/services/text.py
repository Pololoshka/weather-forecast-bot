import enum
import re
from dataclasses import dataclass


class Language(enum.StrEnum):
    en = enum.auto()
    ru = enum.auto()


def get_language(text: str) -> Language:
    match = re.search("[a-z]+", text, flags=re.IGNORECASE)
    return Language.en if match else Language.ru


@dataclass
class City:
    city: str
    country: str
    district: str


def parse_city_from_message(text: str) -> City:
    from src.services.ui.const_ui import Text

    if match := re.match(pattern=Text.city_regex, string=text):
        return City(**match.groupdict())
    raise ValueError("This is not city")
