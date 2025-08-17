import time
import requests
import requests_mock
import pytest

from src.api_hh import HeadHunterAPI

BASE = "https://api.hh.ru"

def test_normalize_salary_basic():
    assert HeadHunterAPI.normalize_salary(None) is None
    assert HeadHunterAPI.normalize_salary({}) is None
    assert HeadHunterAPI.normalize_salary({"from": 200, "to": 300}) == 250
    assert HeadHunterAPI.normalize_salary({"from": 200, "to": None}) == 200
    assert HeadHunterAPI.normalize_salary({"from": 0, "to": 300.0}) == 150

def test_init_clamps_per_page_and_pause():
    api = HeadHunterAPI(per_page=1000, pause_sec=-5)
    assert api.per_page == 100
    assert api.pause_sec == 0.0

def test_iter_vacancies_pagination(hh_page_1, hh_page_2, monkeypatch):
    api = HeadHunterAPI(per_page=100, pause_sec=0.2)

    # не спим в тестах
    monkeypatch.setattr(time, "sleep", lambda _x: None)

    with requests_mock.Mocker() as m:
        m.get(f"{BASE}/vacancies", [{"json": hh_page_1, "status_code": 200},
                                    {"json": hh_page_2, "status_code": 200}])
        rows = list(api.iter_vacancies_by_employer("1740"))

    assert [r["id"] for r in rows] == ["100", "101"]
    # проверим, что действительно ходили два раза
    assert m.call_count == 2
