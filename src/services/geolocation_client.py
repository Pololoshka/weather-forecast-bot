import requests

from src.models.models_for_db import City


class GeolocationClient:
    def __init__(self, url: str, timeout: int):
        self.url = url
        self.timeout = timeout

    def get_geolocation(self, city_name: str, language: str) -> list[City] | None:
        response = requests.get(
            url=self.url,
            params={"name": city_name, "count": "5", "format": "json", "language": language},
            timeout=self.timeout,
        )
        if "results" not in response.json():
            return None
        geolocations = []
        for result in response.json()["results"]:
            geolocations.append(City.parse(data=result))
        return geolocations
