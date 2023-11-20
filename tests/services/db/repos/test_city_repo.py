import pytest

from src.services.db.models import City
from src.services.db.repos import CityRepo
from src.services.db.uow import SqlAlchemyUnitOfWork


@pytest.fixture()
def city_repo(uow: SqlAlchemyUnitOfWork) -> CityRepo:
    return uow.cities


def test_get_by_name(city_repo: CityRepo, city_1: City) -> None:
    assert city_repo.get_by_name(city=city_1.name) == [city_1]


def test_get_by_name_country_district(city_repo: CityRepo, city_1: City) -> None:
    assert (
        city_repo.get_by_name_country_district(
            city=city_1.name, country=city_1.country, district=city_1.district
        )
        == city_1
    )


def test_get_by_name_country_district__not_found(city_repo: CityRepo, city_1: City) -> None:
    assert (
        city_repo.get_by_name_country_district(
            city="not-found", country=city_1.country, district=city_1.district
        )
        is None
    )


def test_get_by_id(city_repo: CityRepo, city_1: City) -> None:
    assert city_repo.get_by_id(city_id=city_1.id) == city_1


def test_get_by_id__not_found(city_repo: CityRepo, city_1: City) -> None:
    assert city_repo.get_by_id(city_id=1000) is None
