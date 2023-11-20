from src.services.db.models import User, UserCity


def test_preferred_user_city(user_city_with_preferred_city: UserCity, user: User) -> None:
    assert user.preferred_user_city == user_city_with_preferred_city


def test_preferred_user_city__is_none(
    user_city_without_preferred_city: UserCity, user: User
) -> None:
    assert user.preferred_user_city is None


def test_cities(
    user: User,
    user_city_with_preferred_city: UserCity,
    user_city_without_preferred_city: UserCity,
) -> None:
    assert list(user.cities) == [
        user_city_with_preferred_city.city,
        user_city_without_preferred_city.city,
    ]
