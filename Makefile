install_pre_commit:
	pre-commit install
	pre-commit install --hook-type commit-msg
	pre-commit autoupdate

fix:
	black src tests
	ruff check src tests --fix


check:
	black --check src tests
	ruff check src tests
	mypy --namespace-packages --explicit-package-bases src tests
	pytest tests


generate:
	alembic revision --m="$(NAME)" --autogenerate

migrate:
	alembic upgrade head
