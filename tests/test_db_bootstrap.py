from unittest.mock import MagicMock
import psycopg2
from src.db_bootstrap import ensure_database, ensure_tables
from src.config import Settings

def _fake_settings() -> Settings:
    return Settings(
        pg_host="h", pg_port=5432, pg_user="u", pg_password="p", pg_db="db",
        employer_ids=[], hh_per_page=100
    )

def _mk_conn(fetchone=None):
    cur = MagicMock()
    cur.__enter__.return_value = cur
    cur.fetchone.return_value = fetchone
    conn = MagicMock()
    conn.__enter__.return_value = conn
    conn.cursor.return_value = cur
    return conn, cur

def test_ensure_database_creates_when_absent(monkeypatch):
    conn, cur = _mk_conn(fetchone=None)  # нет записи в pg_database
    monkeypatch.setattr(psycopg2, "connect", lambda _dsn: conn)

    ensure_database(_fake_settings())
    # второй execute — CREATE DATABASE ...
    assert cur.execute.call_count == 2
    assert any("CREATE DATABASE" in str(c.args[0]) for c in cur.execute.call_args_list)

def test_ensure_database_skip_when_exists(monkeypatch):
    conn, cur = _mk_conn(fetchone=(1,))  # база уже есть
    monkeypatch.setattr(psycopg2, "connect", lambda _dsn: conn)

    ensure_database(_fake_settings())
    # только проверка наличия
    assert cur.execute.call_count == 1
    assert "SELECT 1 FROM pg_database" in str(cur.execute.call_args_list[0].args[0])

def test_ensure_tables_runs_two_ddls(monkeypatch):
    conn, cur = _mk_conn()
    monkeypatch.setattr(psycopg2, "connect", lambda _dsn: conn)

    ensure_tables(_fake_settings())
    # Должны выполняться 2 DDL
    assert cur.execute.call_count == 2
    sqls = [str(c.args[0]) for c in cur.execute.call_args_list]
    assert "CREATE TABLE IF NOT EXISTS employers" in sqls[0]
    assert "CREATE TABLE IF NOT EXISTS vacancies" in sqls[1]
