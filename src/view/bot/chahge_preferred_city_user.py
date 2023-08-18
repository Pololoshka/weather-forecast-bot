from src.errors import NotFoundError
from src.services.db.uow import SqlAlchemyUnitOfWork


def change_preferred_city(user_id: int, city_id: int, uow: SqlAlchemyUnitOfWork) -> None:
    try:
        user_city_is_preferred = uow.user_city.get_is_preferred_city(user_id=user_id)
        user_city_is_preferred.is_preferred = False

    except NotFoundError:
        pass

    finally:
        user_city = uow.user_city.get_by_id(user_id=user_id, city_id=city_id)
        user_city.is_preferred = True
