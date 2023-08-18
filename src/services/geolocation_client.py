import requests

from src.models import Geolocation


class GeolocationClient:
    def __init__(self, url: str, timeout: int):
        self.url = url
        self.timeout = timeout

    def get_geolocation(self, city: str, language: str) -> Geolocation:
        response = requests.get(
            url=self.url,
            params={"name": city, "count": "1", "format": "json", "language": language},
            timeout=self.timeout,
        )
        geo = Geolocation.parse(data=response.json()["results"][0])
        geo.city = city
        return geo
