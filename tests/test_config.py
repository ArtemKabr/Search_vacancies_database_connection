from src.config import get_settings


def test_settings_loads():
    settings = get_settings()
    assert settings.pg_host
    assert settings.pg_port > 0
    assert isinstance(settings.employer_ids, list)
