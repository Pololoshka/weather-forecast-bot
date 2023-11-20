import pytest

from src.services.text import City, Language, get_language, parse_city_from_message


def test_get_language__ru() -> None:
    assert get_language(text="Привет") == Language.ru


def test_get_language__en() -> None:
    assert get_language(text="Hello") == Language.en


def test_parse_city_from_message() -> None:
    assert parse_city_from_message("Москва (Россия, Москва)") == City(
        city="Москва", country="Россия", district="Москва"
    )


def test_parse_city_from_message_with_error() -> None:
    with pytest.raises(ValueError, match="This is not city"):
        parse_city_from_message("Hello")
