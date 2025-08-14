from __future__ import annotations

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from src.config import Settings


def ensure_database(settings: Settings) -> None:
    """
    Создаёт целевую БД, если она не существует.

    Args:
        settings: Настройки подключения.

    Raises:
        psycopg2.Error: При ошибках подключения/DDL.
    """
    # Подключаемся к системной БД 'postgres', чтобы выполнить CREATE DATABASE
    conn = psycopg2.connect(settings.dsn_server)
    conn.set_client_encoding('UTF8')
    try:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        try:
            cur.execute(
                sql.SQL("SELECT 1 FROM pg_database WHERE datname = {db}")
                .format(db=sql.Literal(settings.pg_db))
            )
            exists = cur.fetchone()
            if not exists:
                cur.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(settings.pg_db)
                    )
                )
        finally:
            cur.close()
    finally:
        conn.close()


def ensure_tables(settings: Settings) -> None:
    """
    Создаёт необходимые таблицы в целевой БД, если их нет.

    Таблицы:
        employers:
            id            BIGINT PRIMARY KEY
            name          TEXT NOT NULL
            url           TEXT
        vacancies:
            id            BIGINT PRIMARY KEY
            employer_id   BIGINT NOT NULL REFERENCES employers(id) ON DELETE CASCADE
            name          TEXT NOT NULL
            salary        INTEGER NULL
            alternate_url TEXT NOT NULL

    Args:
        settings: Настройки подключения.
    """
    ddl_employers = """
    CREATE TABLE IF NOT EXISTS employers (
        id BIGINT PRIMARY KEY,
        name TEXT NOT NULL,
        url TEXT
    );
    """

    ddl_vacancies = """
    CREATE TABLE IF NOT EXISTS vacancies (
        id BIGINT PRIMARY KEY,
        employer_id BIGINT NOT NULL REFERENCES employers(id) ON DELETE CASCADE,
        name TEXT NOT NULL,
        salary INTEGER NULL,
        alternate_url TEXT NOT NULL
    );
    """

    conn = psycopg2.connect(settings.dsn_target)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(ddl_employers)
                cur.execute(ddl_vacancies)
    finally:
        conn.close()
