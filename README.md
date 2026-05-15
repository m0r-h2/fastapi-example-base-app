# HiTalent — Тестовое Задание 

REST API на **FastAPI** для управления иерархией отделов и сотрудниками.

## Возможности

- CRUD отделов с древовидной структурой (`parent_id`)
- Уникальность имени отдела в рамках одного родителя
- Защита от циклов при смене родителя
- Сотрудники привязаны к отделу
- Получение поддерева с ограничением `depth` (1–5)
- Удаление отдела:
  - `mode=cascade` — каскадное удаление подотделов
  - `mode=reassign` — перенос сотрудников в другой отдел и удаление

## Архитектура

```
app/
├── api/              # HTTP-роуты (тонкий слой)
├── core/
│   ├── config.py     # настройки из .env
│   ├── crud/         # доступ к БД
│   ├── models/       # SQLAlchemy ORM
│   ├── schemas/      # Pydantic DTO
│   └── services/     # бизнес-логика
├── alembic/          # миграции
└── main.py           # точка входа
```

Поток запроса: **Router → Service → CRUD → Database**

## Быстрый старт (Docker)

```bash
cp .env.template .env
docker compose up --build -d
```

После запуска:

| URL | Описание |
|-----|----------|
| http://localhost:8000/docs | Swagger UI |
| http://localhost:8000/health | Health check |
| http://localhost:8000/api/v1/departments/ | API отделов |

Остановка:

```bash
docker compose down
```

С удалением данных БД:

```bash
docker compose down -v
```

## Локальная разработка

```bash
# зависимости
uv sync --group dev

# PostgreSQL (только БД)
docker compose up -d db

# миграции
uv run alembic -c app/alembic.ini upgrade head

# сервер
uv run uvicorn app.main:main_app --reload
```

## Тесты

Тесты используют in-memory SQLite и не требуют PostgreSQL:

```bash
uv run pytest tests/ -v
```

## Переменные окружения

См. [.env.template](.env.template). Префикс: `APP_CONFIG__`, вложенность через `__`.

Пример для Docker: `APP_CONFIG__DB__HOST=db` (задаётся в `docker-compose.yaml` для сервиса `app`).

## API (кратко)

| Метод | Путь | Описание |
|-------|------|----------|
| `POST` | `/api/v1/departments/` | Создать отдел |
| `GET` | `/api/v1/departments/{id}` | Дерево отдела (`depth`, `include_employees`) |
| `PATCH` | `/api/v1/departments/{id}` | Обновить имя / родителя |
| `DELETE` | `/api/v1/departments/{id}` | Удалить (`mode`, `reassign_to_department_id`) |
| `POST` | `/api/v1/departments/{id}/employees/` | Добавить сотрудника |

## Стек

Python 3.13 · FastAPI · SQLAlchemy 2 (async) · Alembic · PostgreSQL · Docker
