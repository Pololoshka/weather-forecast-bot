from pytest_mock import MockFixture

from src.services.db.models import City


def test_language_city(mocker: MockFixture, city_1: City) -> None:
    mock = mocker.patch("src.services.db.models.get_language")

    assert city_1.language == mock.return_value
    mock.assert_called_once_with(text=city_1.name)
