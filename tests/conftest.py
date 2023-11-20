import pytest

from src.settings import Settings

pytest_plugins = [
    "tests.utils.db",
    "tests.utils.fixtures",
]


@pytest.fixture()
def settings() -> Settings:
    return Settings.from_environ(".env.tests")
