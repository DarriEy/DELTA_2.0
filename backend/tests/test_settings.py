from backend.utils import settings


def test_get_database_url_default(monkeypatch):
    settings.reset_environment_for_tests()
    monkeypatch.setenv("DATABASE_URL", "")

    assert settings.get_database_url() == "sqlite:///./fallback.db"


def test_get_database_url_postgres_normalization(monkeypatch):
    settings.reset_environment_for_tests()
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pass@localhost/db")

    assert (
        settings.get_database_url()
        == "postgresql://user:pass@localhost/db"
    )
