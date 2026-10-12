import pytest

from data_platform.database import DatabaseSettings, load_database_settings


@pytest.fixture(autouse=True)
def isolate_environment(monkeypatch):
    """Ignore the real .env file and any existing database variables."""
    monkeypatch.setattr(
        "data_platform.database.load_dotenv", lambda *args, **kwargs: None
    )
    for name in (
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_DB",
        "POSTGRES_HOST",
        "POSTGRES_PORT",
    ):
        monkeypatch.delenv(name, raising=False)


def test_settings_are_read_from_environment(monkeypatch):
    monkeypatch.setenv("POSTGRES_USER", "user1")
    monkeypatch.setenv("POSTGRES_PASSWORD", "secret")
    monkeypatch.setenv("POSTGRES_DB", "db1")
    monkeypatch.setenv("POSTGRES_PORT", "5433")

    settings = load_database_settings()

    assert settings.user == "user1"
    assert settings.database == "db1"
    assert settings.host == "localhost"
    assert settings.port == 5433


def test_missing_password_raises(monkeypatch):
    monkeypatch.setenv("POSTGRES_USER", "user1")
    monkeypatch.setenv("POSTGRES_DB", "db1")
    with pytest.raises(ValueError, match="POSTGRES_PASSWORD"):
        load_database_settings()


def test_url_hides_password_when_rendered():
    settings = DatabaseSettings(user="u", password="topsecret", database="d")
    rendered = settings.url.render_as_string(hide_password=True)
    assert "topsecret" not in rendered
    assert "***" in rendered


def test_password_with_special_characters_is_preserved():
    settings = DatabaseSettings(user="u", password="p@ss/word:1", database="d")
    assert settings.url.password == "p@ss/word:1"


def test_repr_does_not_contain_password():
    settings = DatabaseSettings(user="u", password="topsecret", database="d")
    assert "topsecret" not in repr(settings)