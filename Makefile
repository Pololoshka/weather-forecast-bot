install_pre_commit:
	pre-commit install
	pre-commit install --hook-type commit-msg
	pre-commit autoupdate

fix:
	black src tests
	isort src tests


check:
	black --check src tests
	isort --check src tests
	mypy --namespace-packages --explicit-package-bases src tests
	flake8 src tests
	pytest tests
