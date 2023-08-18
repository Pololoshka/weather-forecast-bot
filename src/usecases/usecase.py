from src.services.geolocation_client import GeolocationClient
from src.services.wheater_client import WeatherClient
from src.settings import Settings


class UserRequestProcessing:
    def __init__(self, settings: Settings):
        self.settings = settings

    def act(
        self,
        city: str,
        days: int,
    ) -> None:
        geolocation = GeolocationClient(
            url=self.settings.geolocation_url,
            timeout=self.settings.timeout,
        )
        weather_forecast = WeatherClient(
            url=self.settings.weather_url,
            timeout=self.settings.timeout,
        )
        if days == 1:
            weather_forecast.get_current_weather(
                geolocation=geolocation.get_geolocation(city=city),
            )
        else:
            weather_forecast.get_forecast_weather(
                days=days,
                geolocation=geolocation.get_geolocation(city=city),
            )
