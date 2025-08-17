import os
import pytest

@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    # Чистим переменные окружения между тестами
    for k in ["PG_HOST","PG_PORT","PG_USER","PG_PASSWORD","PG_DB","HH_EMPLOYER_IDS","HH_PER_PAGE"]:
        monkeypatch.delenv(k, raising=False)
    yield

@pytest.fixture
def hh_page_1():
    return {
        "items": [
            {
                "id": "100",
                "name": "Python Dev",
                "salary": {"from": 200000, "to": 300000, "currency": "RUR"},
                "alternate_url": "https://hh.ru/vacancy/100",
                "employer": {"id": "1740", "name": "Яндекс", "alternate_url": "https://hh.ru/employer/1740"},
            },
        ],
        "pages": 2,
        "page": 0,
    }

@pytest.fixture
def hh_page_2():
    return {
        "items": [
            {
                "id": "101",
                "name": "Data Engineer",
                "salary": None,
                "alternate_url": "https://hh.ru/vacancy/101",
                "employer": {"id": "1740", "name": "Яндекс", "alternate_url": "https://hh.ru/employer/1740"},
            },
        ],
        "pages": 2,
        "page": 1,
    }
