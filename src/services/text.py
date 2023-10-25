import enum
import re


class Language(enum.StrEnum):
    en = enum.auto()
    ru = enum.auto()


def get_language(message: str) -> Language:
    match = re.search("[a-z]+", message, flags=re.IGNORECASE)
    return Language.en if match else Language.ru
