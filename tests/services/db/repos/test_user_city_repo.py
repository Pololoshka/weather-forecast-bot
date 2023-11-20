from src.services.db.models import UserCity
from src.services.db.uow import SqlAlchemyUnitOfWork


def test_get_by_id(uow: SqlAlchemyUnitOfWork, user_city_with_preferred_city: UserCity) -> None:
    user_city_repo = uow.user_city
    assert (
        user_city_repo.get_by_id(
            user_id=user_city_with_preferred_city.user_id,
            city_id=user_city_with_preferred_city.city_id,
        )
        == user_city_with_preferred_city
    )
