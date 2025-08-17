# Search Vacancies Database Connection

Проект для получения данных о работодателях и вакансиях с сайта [hh.ru](https://hh.ru) через публичный API, сохранения их в базу данных PostgreSQL и работы с ними через класс `DBManager`.

## 📌 Возможности
- Получение данных о работодателях и их вакансиях через API hh.ru.
- Автоматическое создание базы данных и таблиц.
- Сохранение данных в PostgreSQL.
- Запросы через `DBManager`:
  - Список компаний и количество вакансий.
  - Все вакансии с указанием компании, зарплаты и ссылки.
  - Средняя зарплата по всем вакансиям.
  - Вакансии с зарплатой выше средней.
  - Поиск вакансий по ключевым словам.

## 📂 Структура проекта
Search_vacancies_database_connection/
│── src/
│ ├── api_hh.py # Модуль для работы с API hh.ru
│ ├── config.py # Загрузка настроек из .env
│ ├── db_bootstrap.py # Создание базы данных и таблиц
│ ├── db_manager.py # Класс для работы с данными в БД
│ ├── loader.py # Загрузка данных в БД
│ └── main.py # Точка входа
│
│── tests/ # Тесты проекта
│
│── .env_template # Шаблон переменных окружения
│── requirements.txt # Зависимости
│── README.md # Описание проекта



## ⚙ Установка и запуск

### 1. Клонировать репозиторий
```bash
git clone https://github.com/ArtemKabr/Search_vacancies_database_connection.git
cd Search_vacancies_database_connection


2. Создать виртуальное окружение и активировать его
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / MacOS
source .venv/bin/activate


3. Установить зависимости
pip install -r requirements.txt


4. Создать .env на основе .env_template

PG_HOST=127.0.0.1
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=postgres ---------- указать в .env свой пороль
PG_DB=hh_vacancies

HH_EMPLOYER_IDS=1740,3529,78638,2180,15478,3388,4219,39305,1122462,84585
HH_PER_PAGE=100


5. Запустить проект

python -m src.main


🗄 Структура базы данных

Таблица employers
| Поле   | Тип    | Описание          |
| ------ | ------ | ----------------- |
| id     | SERIAL | Первичный ключ    |
| hh\_id | INT    | ID работодателя   |
| name   | TEXT   | Название компании |
| url    | TEXT   | Ссылка на hh.ru   |

Таблица vacancies
| Поле         | Тип    | Описание           |
| ------------ | ------ | ------------------ |
| id           | SERIAL | Первичный ключ     |
| employer\_id | INT    | FK → employers.id  |
| title        | TEXT   | Название вакансии  |
| salary\_from | INT    | Зарплата от        |
| salary\_to   | INT    | Зарплата до        |
| url          | TEXT   | Ссылка на вакансию |


🔍 Примеры SQL-запросов
Все работодатели

SELECT * FROM employers;

Все вакансии

SELECT * FROM vacancies;

Топ-10 компаний по количеству вакансий

SELECT e.name, COUNT(v.id) AS vacancies_count
FROM employers e
LEFT JOIN vacancies v ON e.id = v.employer_id
GROUP BY e.name
ORDER BY vacancies_count DESC
LIMIT 10;
