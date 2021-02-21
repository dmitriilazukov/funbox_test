lint:
	black .
	isort .
	flake8

test:
	docker-compose run --rm links pytest --ds=links.settings && docker-compose stop

start:
	docker-compose up