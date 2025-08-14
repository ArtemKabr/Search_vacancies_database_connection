from src.db_manager import DBManager


def test_dbmanager_has_methods():
    db = DBManager("host=localhost port=5432 dbname=postgres user=postgres password=postgres")
    assert hasattr(db, "get_companies_and_vacancies_count")
    assert hasattr(db, "get_all_vacancies")
    assert hasattr(db, "get_avg_salary")
    assert hasattr(db, "get_vacancies_with_higher_salary")
    assert hasattr(db, "get_vacancies_with_keyword")
