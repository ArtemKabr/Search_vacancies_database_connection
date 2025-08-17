# tests/test_main.py
from unittest.mock import MagicMock
import psycopg2
import src.main as main
from src.config import Settings

class FakeAPI:
    def __init__(self, per_page=None):
        pass

    def iter_vacancies_by_employer(self, employer_id):
        # одна валидная + одна без employer (пропустится)
        yield {
            "id": "200",
            "name": "Backend Engineer",
            "salary": {"from": 250000, "to": 350000},
            "alternate_url": "v200",
            "employer": {"id": "3529", "name": "Сбер", "alternate_url": "e3529"},
        }
        yield {
            "id": "201",
            "name": "Broken",
            "salary": None,
            "alternate_url": "v201",
            # нет employer -> пропуск
        }

    @staticmethod
    def normalize_salary(s):
        return 300000 if s else None

def _settings() -> Settings:
    return Settings(
        pg_host="h",
        pg_port=5432,
        pg_user="u",
        pg_password="p",
        pg_db="db",
        employer_ids=["3529"],
        hh_per_page=100,
    )

def test_main_load_data_inserts(monkeypatch):
    # подменяем HeadHunterAPI в модуле main на фейковый класс
    monkeypatch.setattr(main, "HeadHunterAPI", lambda per_page: FakeAPI(per_page), raising=False)

    # мок соединения с БД и курсора
    cur = MagicMock()
    cur.__enter__.return_value = cur
    conn = MagicMock()
    conn.__enter__.return_value = conn
    conn.cursor.return_value = cur
    monkeypatch.setattr(psycopg2, "connect", lambda _dsn: conn)

    # запускаем
    main.load_data(_settings())

    # все вызовы execute
    calls = cur.execute.call_args_list

    # 1) UPSERT'ы в принципе были
    sql_texts = [str(c.args[0]) for c in calls]
    assert any("INSERT INTO employers" in s for s in sql_texts)
    assert any("INSERT INTO vacancies" in s for s in sql_texts)

    # 2) Находим любой INSERT INTO vacancies с ожидаемой формой параметров (5 полей)
    vac_call = None
    for call in calls:
        sql = str(call.args[0])
        params = call.args[1] if len(call.args) > 1 else ()
        if "INSERT INTO vacancies" in sql and isinstance(params, (list, tuple)) and len(params) == 5:
            vac_call = (sql, params)
            break

    assert vac_call is not None, "Не нашли корректный INSERT INTO vacancies с 5 параметрами"

    # 3) sanity-checks по типам параметров
    _, params = vac_call
    assert isinstance(params[0], int)          # id
    assert isinstance(params[1], int)          # employer_id
    assert isinstance(params[2], str) and params[2]  # name
    assert (params[3] is None) or isinstance(params[3], int)  # salary нормализована или None
    assert isinstance(params[4], str)          # alternate_url
