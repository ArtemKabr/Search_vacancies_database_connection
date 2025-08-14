from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv

load_dotenv()


def _clean(value: str) -> str:
    """Удаляет неразрывные пробелы и обрезает лишние пробелы."""
    return value.replace("\u00A0", " ").strip()


def _get_env(name: str, default: str = "") -> str:
    v = os.getenv(name, "")
    return v.replace("\u00A0", " ").strip() or default


@dataclass(frozen=True)
class Settings:
    """Настройки приложения, загружаемые из окружения."""

    pg_host: str
    pg_port: int
    pg_user: str
    pg_password: str
    pg_db: str
    employer_ids: List[str]
    hh_per_page: int

    @property
    def dsn_server(self) -> str:
        """
        DSN для подключения к серверу Postgres (к БД 'postgres'),
        нужен для создания целевой БД.
        """
        return (
            f"host={self.pg_host} port={self.pg_port} dbname=postgres "
            f"user={self.pg_user} password={self.pg_password}"
        )

    @property
    def dsn_target(self) -> str:
        """DSN для подключения к целевой БД проекта."""
        return (
            f"host={self.pg_host} port={self.pg_port} dbname={self.pg_db} "
            f"user={self.pg_user} password={self.pg_password}"
        )


def get_settings() -> Settings:
    """
    Собирает и возвращает настройки приложения из .env.
    """
    employers_raw = _get_env("HH_EMPLOYER_IDS", "")
    employer_ids = [e.strip() for e in employers_raw.split(",") if e.strip()]
    return Settings(
        pg_host=_get_env("PG_HOST", "127.0.0.1"),
        pg_port=int(_get_env("PG_PORT", "5432")),
        pg_user=_get_env("PG_USER", "postgres"),
        pg_password=_get_env("PG_PASSWORD", "postgres"),
        pg_db=_get_env("PG_DB", "hh_vacancies"),
        employer_ids=employer_ids,
        hh_per_page=int(_get_env("HH_PER_PAGE", "100")),
    )
