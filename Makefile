tests:
	uv run pytest -vv -x

tests-coverage:
	uv run coverage run -m pytest -vv -x
	uv run coverage report

lint:
	uv run ruff check src

types:
	uv run mypy --explicit-package-bases src

fix:
	uv run ruff format src
	uv run ruff check --fix src

quality: lint types tests
