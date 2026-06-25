# Showcase Constructor

Backend для конструктора партнёрских финансовых витрин. Сервис помогает партнёру
собирать витрины финансовых офферов, управлять draft-настройками, блоками и
офферами, публиковать immutable snapshot и отдавать публичный read-path для
готовой витрины с сохранением CPA-трекинга.

## Stack

- Python 3.13
- FastAPI, Dishka, Uvicorn
- PostgreSQL, SQLAlchemy asyncio, Alembic
- uv, Ruff, mypy, pytest

## Run

Подготовить PostgreSQL и при необходимости переопределить `DB_*` переменные.
По умолчанию сервис ожидает базу `showcase_constructor` на локальном PostgreSQL.

```bash
uv sync
rtk uv run python -m src.main
```

Приложение стартует на `http://127.0.0.1:8080`.

## Tests And Coverage

```bash
rtk make tests
rtk make tests-coverage
rtk make quality
```

Coverage-настройки лежат в `pyproject.toml`; `tests-coverage` запускает тесты
под coverage и печатает итоговый отчёт.

## Production-Ready Plan

- Провести тестирование на соответствие требованиям из ТЗ: admin write-path,
  public read-path, публикация snapshot, CPA-редиректы, custom code boundary и
  ожидаемая нагрузка.
- Добавить инфраструктуру запуска и деплоя: `Dockerfile`, `docker-compose` для
  локального окружения и Kubernetes Helm charts для staging/production.
- При необходимости провести небольшой рефакторинг кода и тюнинг оркестратора
  RALPHEX, если на текущем сервисе появятся новые фичи или укрупнённые задачи.
