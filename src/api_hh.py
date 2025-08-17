from __future__ import annotations

import time
from typing import Any, Dict, Iterable, List, Optional

import requests


class HeadHunterAPI:
    """
    Клиент для работы с публичным API hh.ru.

    Примечания:
        - Документация: https://api.hh.ru/openapi/redoc
        - Используем эндпоинт /vacancies с фильтром employer_id.
    """

    BASE_URL: str = "https://api.hh.ru"

    def __init__(self, per_page: int = 100, pause_sec: float = 0.2) -> None:
        """
        Инициализация клиента.

        Args:
            per_page: Количество вакансий на страницу (максимум 100).
            pause_sec: Пауза между запросами, чтобы не получить 429.
        """
        self.per_page = min(max(per_page, 1), 100)
        self.pause_sec = max(pause_sec, 0.0)

    def iter_vacancies_by_employer(self, employer_id: str) -> Iterable[Dict[str, Any]]:
        """
        Итератор по всем вакансиям работодателя.

        Args:
            employer_id: ID работодателя на hh.ru.

        Yields:
            Сырые словари вакансий, как возвращает API.
        """
        page = 0
        while True:
            params = {
                "employer_id": employer_id,
                "page": page,
                "per_page": self.per_page,
                "only_with_salary": "false",
            }
            resp = requests.get(f"{self.BASE_URL}/vacancies", params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            items = data.get("items", [])
            for it in items:
                yield it

            pages = data.get("pages", 0)
            page += 1
            if page >= pages:
                break

            time.sleep(self.pause_sec)

    @staticmethod
    def normalize_salary(s: Optional[Dict[str, Any]]) -> Optional[int]:
        """
        Нормализует объект salary к одному числу (среднее из from/to),
        либо возвращает None, если зарплата не указана.

        Args:
            s: Объект salary из hh (ключи from/to/currency/gross).

        Returns:
            Целое значение зарплаты в валюте вакансии или None.
        """
        if not s:
            return None
        frm = s.get("from")
        to = s.get("to")
        nums: List[int] = [x for x in (frm, to) if isinstance(x, (int, float))]
        if not nums:
            return None
        return int(sum(nums) / len(nums))


def get_employers():
    return None


def get_vacancies_by_employer():
    return None