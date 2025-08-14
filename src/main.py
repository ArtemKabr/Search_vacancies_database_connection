from __future__ import annotations

from typing import Callable

from src.config import get_settings
from src.db_bootstrap import ensure_database, ensure_tables
from src.db_manager import DBManager
from src.loader import load_data


def _print_header(title: str) -> None:
    """Печатает заголовок раздела."""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def user_interface() -> None:
    """
    Простейший интерфейс взаимодействия с пользователем (консоль).
    Не выводит «сырые» коллекции — форматирует читаемые строки.
    """
    settings = get_settings()

    _print_header("1) Создание БД и таблиц (если их нет)")
    print(repr(settings.dsn_server)) # !!!!!!!!!!! временая отловля ошибки
    ensure_database(settings)
    ensure_tables(settings)
    print("✓ БД и таблицы готовы.")

    _print_header("2) Загрузка данных с hh.ru")
    load_data(settings)
    print("✓ Данные загружены / обновлены.")

    _print_header("3) Работа с DBManager")
    db = DBManager(settings.dsn_target)

    menu: dict[str, tuple[str, Callable[[], None]]] = {}

    def act_companies_count() -> None:
        rows = db.get_companies_and_vacancies_count()
        print("Компания — Количество вакансий")
        for company, cnt in rows:
            print(f"- {company} — {cnt}")

    def act_all_vacancies() -> None:
        rows = db.get_all_vacancies()
        print("Компания | Вакансия | Зарплата | Ссылка")
        for company, name, salary, url in rows:
            salary_txt = "не указана" if salary is None else str(salary)
            print(f"- {company} | {name} | {salary_txt} | {url}")

    def act_avg_salary() -> None:
        avg = db.get_avg_salary()
        print("Средняя зарплата:", "нет данных" if avg is None else round(avg))

    def act_higher_salary() -> None:
        rows = db.get_vacancies_with_higher_salary()
        if not rows:
            print("Нет вакансий выше средней (или нет данных по зарплатам).")
            return
        print("Компания | Вакансия | Зарплата | Ссылка (выше средней)")
        for company, name, salary, url in rows:
            print(f"- {company} | {name} | {salary} | {url}")

    def act_with_keyword() -> None:
        kw = input("Введите ключевое слово для поиска в названии вакансии: ").strip()
        rows = db.get_vacancies_with_keyword(kw)
        if not rows:
            print("Ничего не найдено.")
            return
        print(f"Найденные вакансии по ключу '{kw}':")
        for company, name, salary, url in rows:
            salary_txt = "не указана" if salary is None else str(salary)
            print(f"- {company} | {name} | {salary_txt} | {url}")

    menu["1"] = ("Список компаний и количество вакансий", act_companies_count)
    menu["2"] = ("Все вакансии (компания | вакансия | зарплата | ссылка)", act_all_vacancies)
    menu["3"] = ("Средняя зарплата", act_avg_salary)
    menu["4"] = ("Вакансии выше средней зарплаты", act_higher_salary)
    menu["5"] = ("Поиск вакансий по ключевому слову", act_with_keyword)
    menu["0"] = ("Выход", lambda: None)

    while True:
        print("\nМеню:")
        for key, (title, _) in sorted(menu.items()):
            print(f"  {key}. {title}")
        choice = input("Ваш выбор: ").strip()
        if choice == "0":
            print("Выход.")
            break
        action = menu.get(choice)
        if action:
            _, fn = action
            print()
            fn()
        else:
            print("Неизвестный пункт меню.")


if __name__ == "__main__":
    # Точка входа
    user_interface()
