@/Users/optikrus/.codex/RTK.md

# AGENTS.md

Instructions for Codex agents working in this repository.

Проектный стандарт для `showcase_constructor`. Он адаптирован из
`project-template`, но локальные файлы текущего проекта имеют приоритет.

---

## Приоритеты

1. Локальные инструкции: `AGENTS.md`, `README.md`, `pyproject.toml`, `Makefile`.
2. Существующая структура и принятые паттерны проекта.
3. Референсы в `docs/references/examples/`.

Локальные конвенции всегда переопределяют общий reference. Не переписывать
архитектуру, именование, форматирование и структуру без явного запроса.

---

## Текущий стек

- Python 3.13.
- FastAPI, Dishka, Uvicorn.
- `uv` как пакетный менеджер.
- Ruff format/lint, strict mypy, pytest + pytest-asyncio.
- Тесты сейчас используют `httpx2` (`codes`, `Response`) и `fastapi.testclient.TestClient`.

Если добавляется новый сторонний API или есть сомнение в актуальном поведении библиотеки,
сначала проверить документацию через Context7. Особенно для FastAPI, Dishka, Pydantic,
pytest/pytest-asyncio, Ruff/mypy, SQLAlchemy/Alembic если эти слои появятся.

---

## Операционные протоколы

### Неопределённость и верификация

- Не изобретать поведение API, классы, методы, импорты, схемы БД без подтверждения в коде.
- Не предполагать структуру проекта: проверить реально существующие файлы.
- Не фабриковать имена интерфейсов, use cases, моделей, providers.
- При невозможности верификации явно сообщить о недостающей информации.

### Перед изменениями

1. Проверить существующие интерфейсы затронутого слоя.
2. Проверить импорты в редактируемых и соседних файлах.
3. Проверить тесты и helpers, уже применённые в проекте.
4. Убедиться, что именование соответствует локальным конвенциям.
5. Не вводить новые слои и абстракции без явного обоснования.
6. Не рефакторить несмежные файлы без запроса.

### Re-grounding

В длинных сессиях перечитывать затронутые файлы перед каждым блоком редактирования.
Текущее состояние кода важнее предположений из раннего контекста.

---

## Команды

Все shell-команды запускать через `rtk` согласно подключённому RTK-стандарту.

```bash
rtk make tests
rtk make lint
rtk make types
rtk make quality
```

Один тест:

```bash
rtk uv run pytest -vv -x src/tests/path/test_file.py::TestClass::test_name
```

При наличии `Makefile` использовать его targets. Не запускать plain `pytest`, `mypy`,
`ruff`, если есть `uv`/`make`.

---

## RALPHEX workflow

Для задач, связанных с RALPHEX, планами, prompt-файлами или review agents,
сначала читать `docs/references/examples/ralphex.md`.

- Новые RALPHEX plan-файлы по умолчанию сохранять в
  `docs/plans/backlog/<plan-name>.md`.
- Завершённые планы хранить в `docs/plans/completed/<plan-name>.md`.
- Каталог `docs/plans/backlog/completed/` запрещён. Если он появился, переместить
  файлы в `docs/plans/completed/` и удалить пустой invalid subtree.
- Не создавать новые plan-файлы в корне `docs/plans/`, если пользователь явно
  не попросил legacy/root path.
- `.ralphex/config` считается локальной runtime-конфигурацией и не должен
  содержать секреты, токены, chat IDs, `.env`-значения или машинно-зависимые пути.
- Versioned RALPHEX поведение держать в `.ralphex/prompts/`,
  `.ralphex/agents/`, `docs/plans/README.md` и
  `docs/references/examples/ralphex.md`; эти поверхности должны оставаться
  согласованными.
- Reviewer agents — read-only/finding-only: не редактируют файлы, не создают
  изменения схемы БД, не меняют public fields, auth/data contracts, global
  architecture rules и не коммитят.
- Findings перед исправлением классифицируются как ровно одна категория:
  `correctness/security defect`, `missing test coverage`,
  `product decision required`, `optional performance improvement`,
  `simplification`, `false positive`.
- Для API/auth/user-visible data план должен содержать
  `## Product/Security Decisions`; нерешённые public/auth/identifier вопросы
  фиксируются как `product decision required`, а не решаются имплицитно.
- Для планирования, выполнения или review задач по admin API, public storefront,
  persistence, custom domains, audit/events, analytics/billing или custom code
  сначала читать `docs/decisions/mvp-boundaries.md`; unresolved пункты оттуда
  остаются `product decision required`.
- RALPHEX plans используют checkbox actions только внутри `### Task N: ...`.

---

## TDD и workflow

Никакого production-кода для бизнес-логики без предварительно упавшего теста.

TDD обязателен для:

- business rules;
- use cases;
- domain behavior;
- persistence behavior;
- user-facing API behavior.

TDD можно пропустить для безопасных изменений без изменения поведения: документация,
typing-only правки, механический рефактор, форматирование, конфигурация, DI-wiring.

После реализации: точечные тесты затронутого слоя, затем `rtk make quality`, если реалистично.

---

## Структура

Текущая минимальная структура:

```text
src/
  api/          # FastAPI app factory, root router, common endpoints
  di/           # Dishka container
  tests/        # pytest fixtures, helpers, API tests
```

При добавлении бизнес-доменов использовать clean architecture layout:

```text
src/
  api/          # delivery: endpoints, boundary schemas, exception mapping
  core/         # use cases, domain schemas, exceptions, storage interfaces
  storages/     # persistence implementations and ORM models
  services/     # adapters/orchestration around external clients
  clients/      # async HTTP clients and external API schemas
  di/           # Dishka providers and container
  config/       # pydantic-settings, constants
  migrations/   # Alembic migrations, if DB layer exists
  tests/        # tests by layer
```

Не создавать `core/`, `storages/`, `config/` или `migrations/` заранее без задачи, которая
требует этот слой.

---

## Архитектура

- `api/` парсит вход, вызывает один use case, преобразует ответ. Никакой бизнес-логики.
- `core/` содержит бизнес-правила и зависит только от интерфейсов.
- `storages/` реализует core-интерфейсы. Слой данных называется `storages/`, не `repositories/`.
- `clients/` содержат внешние HTTP API; `services/` адаптируют clients к core-сценариям.
- `di/` собирает зависимости. Контейнер создаётся через `src/di/container.py`.

Reference:

- `docs/references/examples/core.md`
- `docs/references/examples/storages.md`
- `docs/references/examples/di.md`

---

## API

- `src/api/routers.py` содержит `root_router = APIRouter()`.
- `src/api/boundary.py::BoundaryModel` и `SnakeBoundaryModel` должны иметь
  совместимые helpers `parse()`, `parse_json()` и `dict()`, где `dict()` вызывает
  `model_dump(mode="json", by_alias=True, **kwargs)`.
- Все common/domain routers регистрируются только в `src/api/routers.py` через
  `root_router.include_router(...)`.
- `create_app()` подключает только `root_router`, exception handlers/middleware при наличии,
  но не импортирует feature endpoints напрямую.
- Endpoint делает только auth/validation/boundary conversion/use case call.
- Один endpoint — один use case. Ветвление между use cases внутри endpoint запрещено.
- HTTP exception mapping централизовать в `src/api/exceptions.py`, когда появятся доменные ошибки.
- Все вызовы с именованными аргументами, если это не ухудшает читаемость стандартного API.

Reference:

- `docs/references/examples/api.md`
- `docs/references/examples/main_py.md`

---

## DI

- Providers размещать в `src/di/providers/`, один файл на домен или инфраструктурную группу.
- Use cases, storages, clients, services: `Scope.REQUEST` по умолчанию.
- Test mock use cases: `Scope.APP` + `AsyncMock(spec=UseCaseClass)`.
- FastAPI интеграция: `setup_dishka_fastapi(...)`; для endpoints с DI использовать `DishkaRoute`.
- DI-managed DB session является Unit of Work: транзакция начинается и завершается только в provider.
- `session.commit()`/`session.begin()` в storage/use case запрещены.

Reference: `docs/references/examples/di.md`.

---

## Config и migrations

Добавлять только когда появляется runtime-конфигурация или DB layer.

- Settings через `pydantic-settings`; каждый settings-класс со своим `env_prefix`.
- Секреты хранить как `SecretStr`.
- Пути/директории — в `src/config/constants.py`, если они реально нужны.
- Миграции Alembic: имена файлов без дат, например `0001_create_entities.py`.
- `migrations/commands.py` использует `constants.DIRS.SRC / "migrations" / "alembic.ini"`.

Reference:

- `docs/references/examples/config.md`
- `docs/references/examples/migrations.md`

---

## Tests

- Новые тесты писать только внутри `class Test*`.
- Общие fixtures живут в `src/tests/conftest.py`.
- Fixture mixins живут в `src/tests/fixtures.py`.
- Helpers живут в `src/tests/helpers/`.
- API tests используют `APIFixture` и `APIHelper`; не создавать `FastAPI`, `TestClient`,
  `AsyncClient` или Dishka container локально в test-файле.
- Для domain objects/params/results использовать `FactoryHelper`, когда он есть или должен быть
  добавлен для нового домена.
- Блоки Arrange/Act/Assert разделяются пустыми строками.
- Переменные по роли: `container`, `app`, `use_case`, не `c`, `a`, `uc`.

Reference: `docs/references/examples/tests.md`.

---

## Строгие запреты

| Запрет | Причина |
| --- | --- |
| Production-код бизнес-логики до предварительно упавшего теста | Нарушает TDD |
| Бизнес-логика в FastAPI endpoints | Delivery-слой только делегирует |
| Прямой ORM/ODM доступ из use cases | Use cases работают через interfaces |
| `session.commit()` в storage-классах | Транзакцией управляет DI provider |
| Новый слой `repositories/` или `repos/` | Слой данных называется `storages/` |
| Тесты-функции `def test_*` вне `class Test*` для нового кода | Тесты группируются классами |
| `# noqa`, `# type: ignore`, `# pyright: ignore` без явного разрешения | Сначала исправить причину |
| Plain `pytest`, `mypy`, `ruff` при наличии `uv`/`make` | Запускать через `uv run` или `make` |
| Однобуквенные и сокращённые имена в тестах/conftest | Имена отражают роль |
| Регистрация feature/common routers напрямую в `create_app()` | Routers собираются через `root_router` |
| Fixtures внутри `src/tests/api/*`, `src/tests/core/*`, `src/tests/storages/*` | Инфраструктура централизована |
| Прямые HTTP/SQL setup-вызовы в тестах вместо helpers | Helpers фиксируют общий тестовый контракт |

Исключения допустимы только для существующего legacy-кода при явной локальной причине.

---

## Ruff, mypy, formatting

- Python 3.13, line length 100, двойные кавычки, Ruff format.
- Ruff `select = ["ALL"]`, strict mypy, type annotations на всех функциях.
- Black не использовать в новых правках.
- Эталонные настройки см. в `docs/references/examples/pyproject.toml`; локальный
  `pyproject.toml` имеет приоритет.

---

## Чеклист завершения

- [ ] Затронутые тесты запущены и зелёные, если реалистично.
- [ ] `rtk make quality` запущен, если реалистично.
- [ ] Импорты проверены, нет несуществующих имён.
- [ ] API контракты не нарушены.
- [ ] Изменены только целевые файлы.
- [ ] Именование соответствует конвенциям проекта.
- [ ] Нет мёртвого кода.
- [ ] Архитектурные слои не нарушены.
