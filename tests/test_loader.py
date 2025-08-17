from unittest.mock import MagicMock
import psycopg2

from src.loader import load_data
from src.config import Settings

class FakeAPI:
    def __init__(self): pass
    def iter_vacancies_by_employer(self, employer_id):
        # одна вакансия валидная, одна с пустым employer (пропускается)
        yield {
            "id": "100",
            "name": "Python Dev",
            "salary": {"from": 200000, "to": 300000},
            "alternate_url": "v100",
            "employer": {"id": "1740", "name": "Яндекс", "alternate_url": "e1740"},
        }
        yield {
            "id": "101",
            "name": "NoEmployer",
            "salary": None,
            "alternate_url": "v101",
            # нет employer -> будет пропуск
        }
    @staticmethod
    def normalize_salary(s):
        return 250000 if s else None

def _settings() -> Settings:
    return Settings(
        pg_host="h", pg_port=5432, pg_user="u", pg_password="p", pg_db="db",
        employer_ids=["1740"], hh_per_page=100
    )

def test_load_data_inserts(monkeypatch):
    # подменим HH API на наш фейк
    monkeypatch.setattr("src.loader.HeadHunterAPI", lambda per_page: FakeAPI())

    # подменим psycopg2.connect на заглушку с курсором и логом вызовов
    cur = MagicMock(); cur.__enter__.return_value = cur
    conn = MagicMock(); conn.__enter__.return_value = conn; conn.cursor.return_value = cur
    monkeypatch.setattr(psycopg2, "connect", lambda _dsn: conn)

    load_data(_settings())

    # Должны быть INSERT в employers и затем INSERT в vacancies (только для валидной вакансии)
    sqls = [str(c.args[0]) for c in cur.execute.call_args_list]
    params = [c.args[1] for c in cur.execute.call_args_list]

    # Проверим, что был UPSERT работодателя
    assert any("INSERT INTO employers" in s for s in sqls)
    # И UPSERT вакансии
    assert any("INSERT INTO vacancies" in s for s in sqls)

    # Проверим параметры для вакансии (id, employer_id, name, salary, url)
    vac_params = None
    for s, p in zip(sqls, params):
        if "INSERT INTO vacancies" in s:
            vac_params = p
            break

    assert vac_params is not None
    assert vac_params[0] == 100            # id
    assert vac_params[1] == 1740           # employer_id
    assert vac_params[2] == "Python Dev"   # name
    assert vac_params[3] == 250000         # salary (нормализованная)
    assert vac_params[4] == "v100"         # alternate_url
