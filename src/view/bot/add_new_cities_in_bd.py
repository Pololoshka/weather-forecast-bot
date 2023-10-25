from collections.abc import Sequence

from src.models.models_for_db import City
from src.services.ui.bot import MyBot


def add_new_cities_in_bd(bot: MyBot, cities: Sequence[City]) -> None:
    for city in cities:
        if bot.services.uow.cities.get_by_name_country_district(
            city=city.name, country=city.country, district=city.district
        ):
            continue
        bot.services.uow.session.add(city)
    bot.services.uow.session.flush()
