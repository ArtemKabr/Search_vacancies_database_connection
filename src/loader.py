from __future__ import annotations

from typing import Any, Dict

import psycopg2

from src.api_hh import HeadHunterAPI
from src.config import Settings


def _insert_employer(cur, employer: Dict[str, Any]) -> None:
    """
    Вставляет работодателя (UPSERT по id).
    """
    cur.execute(
        """
        INSERT INTO employers (id, name, url)
        VALUES (%s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            url = EXCLUDED.url;
        """,
        (int(employer["id"]), employer["name"], employer.get("alternate_url")),
    )


def _insert_vacancy(cur, vac: Dict[str, Any], employer_id: int, salary: int | None) -> None:
    """
    Вставляет вакансию (UPSERT по id).
    """
    cur.execute(
        """
        INSERT INTO vacancies (id, employer_id, name, salary, alternate_url)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            employer_id = EXCLUDED.employer_id,
            name = EXCLUDED.name,
            salary = EXCLUDED.salary,
            alternate_url = EXCLUDED.alternate_url;
        """,
        (
            int(vac["id"]),
            employer_id,
            vac["name"],
            salary,
            vac.get("alternate_url") or "",
        ),
    )


def load_data(settings: Settings) -> None:
    """
    Загружает работодателей и их вакансии в БД.

    Шаги:
        1) Для каждого employer_id забираем вакансии из hh.ru.
        2) Вставляем запись о работодателе (из поля vacancy['employer']).
        3) Вставляем все вакансии.

    Args:
        settings: Настройки подключения.
    """
    api = HeadHunterAPI(per_page=settings.hh_per_page)
    conn = psycopg2.connect(settings.dsn_target)
    try:
        with conn:
            with conn.cursor() as cur:
                for employer_id in settings.employer_ids:
                    for vac in api.iter_vacancies_by_employer(employer_id):
                        emp = vac.get("employer") or {}
                        if not emp or "id" not in emp:
                            # Пропускаем, если нет информации о работодателе
                            continue

                        # Вставка/обновление работодателя
                        _insert_employer(cur, emp)

                        # Нормализация зарплаты
                        salary_norm = api.normalize_salary(vac.get("salary"))

                        # Вставка/обновление вакансии
                        _insert_vacancy(cur, vac, int(emp["id"]), salary_norm)
    finally:
        conn.close()
