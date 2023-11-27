import logging

import requests
from requests import exceptions as req_exc

from src import exceptions as exc
from src.services.db.models import City

logger = logging.getLogger(__name__)


class GeolocationClient:
    def __init__(self, url: str, timeout: int):
        self.url = url
        self.timeout = timeout

    def get_geolocation(self, city_name: str, language: str) -> list[City] | None:
        try:
            response = requests.get(
                url=self.url,
                params={"name": city_name, "count": "5", "format": "json", "language": language},
                timeout=self.timeout,
            )
        except req_exc.RequestException as err:
            logger.error("GeolocationClientError", exc_info=True)
            raise exc.GeolocationClientError("Text.exc_geolocation") from err

        if "results" not in response.json():
            return None
        return [City.parse(data=result) for result in response.json()["results"]]
