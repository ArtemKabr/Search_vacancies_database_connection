from src.config import get_settings

def test_get_settings_defaults(monkeypatch):
    s = get_settings()
    assert s.pg_host == "127.0.0.1"
    assert s.pg_port == 5432
    assert s.pg_user == "postgres"
    assert s.pg_password == "postgres"
    assert s.pg_db == "hh_vacancies"
    assert s.hh_per_page == 100
    assert s.employer_ids == []
    assert "dbname=postgres" in s.dsn_server
    assert f"dbname={s.pg_db}" in s.dsn_target

def test_get_settings_from_env(monkeypatch):
    monkeypatch.setenv("PG_HOST", "db")
    monkeypatch.setenv("PG_PORT", "5433")
    monkeypatch.setenv("PG_USER", "u")
    monkeypatch.setenv("PG_PASSWORD", "p")
    monkeypatch.setenv("PG_DB", "mydb")
    monkeypatch.setenv("HH_PER_PAGE", "77")
    monkeypatch.setenv("HH_EMPLOYER_IDS", "1740, 3529, ,  ")

    s = get_settings()
    assert s.pg_host == "db"
    assert s.pg_port == 5433
    assert s.pg_user == "u"
    assert s.pg_password == "p"
    assert s.pg_db == "mydb"
    assert s.hh_per_page == 77
    assert s.employer_ids == ["1740", "3529"]
    assert s.dsn_server.startswith("host=db")
    assert s.dsn_target.startswith("host=db")
