from src.models.models_for_db import User
from src.services.db.uow import SqlAlchemyUnitOfWork


def change_preferred_city(user: User, city_id: int, uow: SqlAlchemyUnitOfWork) -> None:
    if preferred_user_city := user.preferred_user_city:
        preferred_user_city.is_preferred = False
    if user_city := uow.user_city.get_by_id(user_id=user.id, city_id=city_id):
        user_city.is_preferred = True
    uow.session.flush()
