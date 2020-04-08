include environ
PIP=.venv/bin/pip3
PIPENV=.venv/bin/pipenv
lint:
	$(PIPENV) run black . --config black.toml
	$(PIPENV) run isort -y
	$(PIPENV) run flake8

test:
	$(PIPENV) run pytest --ds=links.settings

init:
	python3 -m pipenv --python 3.7
	$(PIP) install pipenv
	$(PIPENV) sync
	$(PIPENV) run python manage.py migrate --noinput

start:
	$(PIPENV) run python manage.py runserver 0.0.0.0:8080
