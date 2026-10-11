import dataclasses
from pathlib import Path

import pytest

from data_platform.config import Settings, load_settings


@pytest.fixture(autouse=True)
def isolate_environment(monkeypatch):
    """Keep tests independent from the developer's real .env file."""
    monkeypatch.setattr(
        "data_platform.config.load_dotenv", lambda *args, **kwargs: None
    )
    for name in ("APP_ENV", "LOG_LEVEL", "LOG_DIR"):
        monkeypatch.delenv(name, raising=False)


def test_defaults_when_nothing_is_set():
    settings = load_settings()
    assert settings == Settings(
        env="development", log_level="INFO", log_dir=Path("logs")
    )


def test_values_are_read_from_environment(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("LOG_LEVEL", "debug")
    monkeypatch.setenv("LOG_DIR", "custom_logs")

    settings = load_settings()

    assert settings.env == "production"
    assert settings.log_level == "DEBUG"
    assert settings.log_dir == Path("custom_logs")


def test_invalid_log_level_raises(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "VERBOSE")
    with pytest.raises(ValueError, match="LOG_LEVEL"):
        load_settings()


def test_settings_are_immutable():
    settings = load_settings()
    with pytest.raises(dataclasses.FrozenInstanceError):
        settings.env = "production"