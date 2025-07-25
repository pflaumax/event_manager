local_run:
	cp config/.env.local config/.env
	python manage.py runserver

docker_build:
	docker compose up --build

docker_run:
	docker compose up

docker_stop:
	docker compose down

