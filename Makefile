.PHONY: install format lint test up down migrate run

install:      ## install dependencies
	uv sync

format:       ## auto-format code
	uv run ruff format .

lint:         ## check style & catch errors
	uv run ruff check .

test:         ## run unit tests
	uv run pytest

up:           ## start db + redis
	docker-compose -f src/accounts/docker-compose.yml up -d
	docker-compose -f src/auth/docker-compose.yml up -d
	docker-compose -f src/pets/docker-compose.yml up -d

down:         ## stop db + redis
	docker-compose -f src/accounts/docker-compose.yml down
	docker-compose -f src/auth/docker-compose.yml down
	docker-compose -f src/pets/docker-compose.yml down

migrate:      ## apply latest db migrations
	uv run alembic upgrade head

run_accounts:          ## run the accounts service (example)
	uv run uvicorn src.accounts.main:app --reload --port 8001

run_auth:          ## run the auth service (example)
	uv run uvicorn src.auth.main:app --reload --port 8002

run_pets:          ## run the pets service (example)
	uv run uvicorn src.pets.main:app --reload --port 8003