.PHONY: install format lint test up down migrate run

install:      ## install dependencies
	uv sync

format_accounts:       ## auto-format code
	uv run ruff format ./src/accounts

format_auth:       ## auto-format code
	uv run ruff format ./src/auth

format_pets:       ## auto-format code
	uv run ruff format ./src/pets

lint_accounts:         ## check style & catch errors
	uv run ruff check ./src/accounts

lint_auth:         ## check style & catch errors
	uv run ruff check ./src/auth

lint_pets:         ## check style & catch errors
	uv run ruff check ./src/pets

test_accounts:         ## run unit tests
	uv run pytest ./src/accounts

test_auth:         ## run unit tests
	uv run pytest ./src/auth

test_pets:         ## run unit tests
	uv run pytest ./src/pets

up:           ## start postgres + redis
	docker-compose --env-file .env -f deployment/docker-compose.yml up

down:         ## stop postgres + redis
	docker-compose --env-file .env -f deployment/docker-compose.yml down

down_volume:         ## stop postgres + redis and remove volumes
	docker-compose --env-file .env -f deployment/docker-compose.yml down -v

migrate:      ## apply latest db migrations`
	uv run alembic upgrade head

run_accounts:      ## run the accounts service (example)
	uv run uvicorn src.accounts.main:app --reload --port 8001

run_auth:          ## run the auth service (example)
	uv run uvicorn src.auth.main:app --reload --port 8002

run_pets:          ## run the pets service (example)
	uv run uvicorn src.pets.main:app --reload --port 8003

