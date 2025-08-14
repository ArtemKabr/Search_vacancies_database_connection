from __future__ import annotations

from typing import Iterable, List, Tuple

import psycopg2


class DBManager:
    """
    Класс для работы с данными БД PostgreSQL.

    Методы соответствуют требованиям задания.
    """

    def __init__(self, dsn: str) -> None:
        """
        Инициализация.

        Args:
            dsn: DSN-строка подключения к целевой БД.
        """
        self._dsn = dsn

    def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
        """
        Получает список всех компаний и количество вакансий у каждой.

        Returns:
            Список кортежей (company_name, vacancies_count).
        """
        sql_text = """
        SELECT e.name AS company, COUNT(v.id) AS vacancies_count
        FROM employers e
        LEFT JOIN vacancies v ON v.employer_id = e.id
        GROUP BY e.name
        ORDER BY vacancies_count DESC, e.name ASC;
        """
        conn = psycopg2.connect(self._dsn)
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql_text)
                    return [(r[0], int(r[1])) for r in cur.fetchall()]
        finally:
            conn.close()

    def get_all_vacancies(self) -> List[Tuple[str, str, int | None, str]]:
        """
        Получает список всех вакансий:
        - название компании
        - название вакансии
        - зарплата (нормализованная, может быть None)
        - ссылка на вакансию

        Returns:
            Список кортежей (company, vacancy_name, salary, url).
        """
        sql_text = """
        SELECT e.name AS company, v.name AS vacancy, v.salary, v.alternate_url
        FROM vacancies v
        JOIN employers e ON e.id = v.employer_id
        ORDER BY e.name ASC, v.name ASC;
        """
        conn = psycopg2.connect(self._dsn)
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql_text)
                    return [
                        (r[0], r[1], (None if r[2] is None else int(r[2])), r[3])
                        for r in cur.fetchall()
                    ]
        finally:
            conn.close()

    def get_avg_salary(self) -> float | None:
        """
        Получает среднюю зарплату по всем вакансиям, где она указана.

        Returns:
            Средняя зарплата или None, если данных нет.
        """
        sql_text = """
        SELECT AVG(v.salary)::FLOAT
        FROM vacancies v
        WHERE v.salary IS NOT NULL;
        """
        conn = psycopg2.connect(self._dsn)
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql_text)
                    row = cur.fetchone()
                    return None if row is None or row[0] is None else float(row[0])
        finally:
            conn.close()

    def get_vacancies_with_higher_salary(self) -> List[Tuple[str, str, int, str]]:
        """
        Получает список вакансий с зарплатой выше средней.

        Returns:
            Список кортежей (company, vacancy_name, salary, url).
        """
        sql_text = """
        WITH avg_salary AS (
            SELECT AVG(salary) AS avg_val
            FROM vacancies
            WHERE salary IS NOT NULL
        )
        SELECT e.name AS company, v.name AS vacancy, v.salary, v.alternate_url
        FROM vacancies v
        JOIN employers e ON e.id = v.employer_id
        CROSS JOIN avg_salary a
        WHERE v.salary IS NOT NULL AND v.salary > a.avg_val
        ORDER BY v.salary DESC;
        """
        conn = psycopg2.connect(self._dsn)
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql_text)
                    return [
                        (r[0], r[1], int(r[2]), r[3]) for r in cur.fetchall()
                    ]
        finally:
            conn.close()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Tuple[str, str, int | None, str]]:
        """
        Получает список вакансий, в названии которых содержится слово (LIKE, case-insensitive).

        Args:
            keyword: Ключевое слово (например, 'python').

        Returns:
            Список кортежей (company, vacancy_name, salary, url).
        """
        sql_text = """
        SELECT e.name AS company, v.name AS vacancy, v.salary, v.alternate_url
        FROM vacancies v
        JOIN employers e ON e.id = v.employer_id
        WHERE v.name ILIKE %s
        ORDER BY e.name ASC, v.name ASC;
        """
        pattern = f"%{keyword}%"
        conn = psycopg2.connect(self._dsn)
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql_text, (pattern,))
                    return [
                        (r[0], r[1], (None if r[2] is None else int(r[2])), r[3])
                        for r in cur.fetchall()
                    ]
        finally:
            conn.close()
