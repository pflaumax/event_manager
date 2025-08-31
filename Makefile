docker_build_dev:
	docker compose -f docker-compose.dev.yml up --build

docker_run_dev:
	docker compose -f docker-compose.dev.yml up -d

docker_stop_dev:
	docker compose -f docker-compose.dev.yml down

docker_restart_dev_web:
	docker compose -f docker-compose.dev.yml restart web

docker_build_prod:
	docker compose -f docker-compose.prod.yml up -d --build