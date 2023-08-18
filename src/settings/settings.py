from dataclasses import dataclass, field


@dataclass
class Settings:
    weather_url: str = field(default="https://api.open-meteo.com/v1/forecast")
    geolocation_url: str = field(default="https://geocoding-api.open-meteo.com/v1/search")
    timeout: int = field(default=5)
