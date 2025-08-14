from unittest.mock import MagicMock
import psycopg2
from src.db_manager import DBManager

def _mk_conn(fetchall=None, fetchone=None):
    cur = MagicMock()
    cur.__enter__.return_value = cur
    if fetchall is not None:
        cur.fetchall.return_value = fetchall
    if fetchone is not None:
        cur.fetchone.return_value = fetchone
    conn = MagicMock()
    conn.__enter__.return_value = conn
    conn.cursor.return_value = cur
    return conn, cur

def test_get_companies_and_vacancies_count(monkeypatch):
    data = [("A", 2), ("B", 0)]
    conn, cur = _mk_conn(fetchall=data)
    monkeypatch.setattr(psycopg2, "connect", lambda _dsn: conn)

    db = DBManager("dsn")
    got = db.get_companies_and_vacancies_count()
    assert got == [("A", 2), ("B", 0)]
    assert "GROUP BY e.name" in str(cur.execute.call_args.args[0])

def test_get_all_vacancies(monkeypatch):
    rows = [("Comp", "Vac", 123, "url"), ("Comp", "Vac2", None, "u2")]
    conn, cur = _mk_conn(fetchall=rows)
    monkeypatch.setattr(psycopg2, "connect", lambda _dsn: conn)

    db = DBManager("dsn")
    got = db.get_all_vacancies()
    assert got[0] == ("Comp", "Vac", 123, "url")
    assert got[1] == ("Comp", "Vac2", None, "u2")

def test_get_avg_salary(monkeypatch):
    conn, cur = _mk_conn(fetchone=(250000.0,))
    monkeypatch.setattr(psycopg2, "connect", lambda _dsn: conn)

    db = DBManager("dsn")
    assert db.get_avg_salary() == 250000.0

def test_get_avg_salary_none(monkeypatch):
    conn, cur = _mk_conn(fetchone=(None,))
    monkeypatch.setattr(psycopg2, "connect", lambda _dsn: conn)

    db = DBManager("dsn")
    assert db.get_avg_salary() is None

def test_get_vacancies_with_higher_salary(monkeypatch):
    rows = [("Comp", "Vac", 300000, "url")]
    conn, cur = _mk_conn(fetchall=rows)
    monkeypatch.setattr(psycopg2, "connect", lambda _dsn: conn)

    db = DBManager("dsn")
    got = db.get_vacancies_with_higher_salary()
    assert got == rows
    assert "WITH avg_salary AS" in str(cur.execute.call_args.args[0])

def test_get_vacancies_with_keyword(monkeypatch):
    rows = [("Comp", "Python Dev", 200000, "url")]
    conn, cur = _mk_conn(fetchall=rows)
    monkeypatch.setattr(psycopg2, "connect", lambda _dsn: conn)

    db = DBManager("dsn")
    got = db.get_vacancies_with_keyword("python")
    assert got == rows
    # проверяем шаблон ILIKE
    assert cur.execute.call_args.args[1] == ("%python%",)
