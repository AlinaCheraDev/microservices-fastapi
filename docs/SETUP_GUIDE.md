# Project Setup Guide

A step-by-step guide to bootstrap this FastAPI microservices monorepo **before writing any
business logic**. The goal of this phase is to have an empty-but-runnable skeleton: dependencies
install, services start, linting/formatting/tests run, containers come up, and CI is green.

Follow the steps in order. Each tool has a short **Why** so you understand *what problem it solves*,
not just *how to type the command*.

> Scope reference: this covers section **1. Project repository and setup** from `tasks.md`.
> The stack is defined in `Technical_decisions.md`.

---

## 0. Prerequisites (install once on your machine)

Before touching the repo, make sure these exist system-wide.

| Tool | Why you need it |
|------|-----------------|
| **Python 3.13** (latest stable) | The language the services are written in. We pin an exact version so every developer and CI runner behaves identically. |
| **uv** | Fast Python package & environment manager (replaces `pip` + `venv` + `pip-tools`). It creates the virtual environment, resolves and locks dependencies, and runs tools. Chosen because it's dramatically faster and gives reproducible installs via a lockfile. |
| **Docker + Docker Compose** | Runs PostgreSQL and Redis locally without installing them natively. Compose lets us describe those services in one file and start them all with one command — so "works on my machine" stops being a problem. |
| **Git** | Version control. This is a monorepo hosted on GitHub. |
| **make** | Runs the shortcut commands defined in the `Makefile` (lint, format, test, migrate, run). Usually already installed on Linux/macOS. |

Install uv (Linux/macOS):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify everything:
```bash
python3 --version
uv --version
docker --version
docker compose version
git --version
make --version
```

---

## 1. Create the repository

**Why:** a clean repo with the right ignore rules keeps secrets and generated files out of version
control from commit #1 — much harder to fix later.

1. Create a new GitHub repository (monorepo — all services live in one repo).
2. Clone it and enter the folder.
3. Add a **`.gitignore`** using GitHub's Python template. It ignores `__pycache__/`, `.venv/`,
   `*.pyc`, `.env`, build artifacts, etc.
   - **Why:** prevents committing your virtual environment, compiled bytecode, and — critically —
     your real `.env` secrets.

```bash
git clone <your-repo-url>
cd microservices_fastpi
curl -o .gitignore https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore
```

---

## 2. Pin the Python version

Create a **`.python-version`** file containing the exact version:

```
3.13
```

**Why:** `uv` and most IDEs read this file to automatically select the correct interpreter for the
project. It guarantees you, your teammates, and CI all run the same Python.

---

## 3. Initialize the project with uv

**Why:** `uv init` scaffolds a `pyproject.toml` (the single source of truth for dependencies and
tool config) and sets up the project layout. `uv` then manages an isolated `.venv` so project
dependencies never pollute your system Python.

```bash
uv init
uv venv          # creates the .venv virtual environment
```

**Why a virtual environment (venv):** it isolates this project's packages from every other project.
Without it, installing a library for one project could break another.

---

## 4. Add dependencies with uv

Add packages in logical groups. `uv add` installs them **and** records the exact version in
`pyproject.toml` + `uv.lock` (the lockfile that makes installs reproducible).

> Rule from `Technical_decisions.md`: always pin the **latest stable, exact version**.

### Runtime dependencies
```bash
uv add fastapi uvicorn
uv add sqlalchemy alembic
uv add "psycopg[binary]"        # PostgreSQL driver for SQLAlchemy
uv add redis
uv add pydantic pydantic-settings
uv add "python-jose[cryptography]"   # JWT handling for OAuth flows (optional; or use FastAPI security utils)
uv add bcrypt
uv add slowapi
uv add grpcio grpcio-tools
uv add dependency-injector
uv add loguru
```

### Development-only dependencies
```bash
uv add --dev ruff pytest pytest-asyncio httpx
```

**Why each tool:**

| Tool | Utility |
|------|---------|
| **FastAPI** | The web framework for building the REST/HTTP APIs. Gives async support, automatic validation, and free Swagger docs. |
| **uvicorn** | The ASGI server that actually *runs* a FastAPI app (development and deployment). |
| **SQLAlchemy** | ORM — lets you work with database rows as Python objects instead of raw SQL. |
| **Alembic** | Database migration tool for SQLAlchemy. Versions your schema changes so the DB structure evolves safely and reproducibly. |
| **psycopg** | The PostgreSQL driver SQLAlchemy uses to talk to the database. |
| **redis (redis-py)** | Client for Redis — used for caching. |
| **pydantic** | Data validation & DTOs (the request/response models). Validates and parses input automatically. |
| **pydantic-settings** | Loads configuration from environment variables into typed settings objects (used for `DEBUG`, `ENVIRONMENT`, DB URL, etc.). |
| **bcrypt** | Securely hashes passwords so you never store them in plain text. |
| **slowapi** | Rate limiting for FastAPI — protects endpoints from abuse/brute-force. |
| **grpcio / grpcio-tools** | gRPC runtime + the protobuf compiler. Used for fast internal service-to-service communication (Auth ↔ Account ↔ Pet). |
| **dependency-injector** | Dependency injection framework — wires repositories/services together cleanly and makes them easy to swap/test. |
| **loguru** | Simpler, more powerful logging than the stdlib `logging`. |
| **ruff** | Linter *and* formatter in one. Enforces code style and catches bugs. Fast, replaces flake8+black+isort. |
| **pytest** | The unit testing framework. |
| **httpx** | Async HTTP client — used by tests to call FastAPI endpoints. |

---

## 5. Configure `pyproject.toml`

Beyond dependencies, add tool configuration here. **Why:** one file, checked into git, means every
developer and CI use identical linting/formatting rules — no arguments about style.

Add a section like:

```toml
[tool.ruff]
line-length = 120        # per Technical_decisions.md
target-version = "py313"

[tool.ruff.lint]
# Enable a sensible rule set: pyflakes (F), pycodestyle (E/W),
# isort (I), bugbear (B), etc.
select = ["E", "F", "W", "I", "B", "UP"]

[tool.pytest.ini_options]
testpaths = ["src", "integration-tests"]
```

**Why line-length 120:** a team convention — wide enough for readable code, narrow enough for
side-by-side diffs.

---

## 6. Create the folder structure

**Why:** a consistent per-service layout means anyone can navigate any service. Each service is
independent (its own `main.py`, controllers, services, modules) but shares common code via
`src/libs`.

Create this skeleton (from `Technical_decisions.md`):

```
src/
  libs/                     # shared: db connection, grpc<->model converters, errors, constants
  pets/
    controllers/
      http/v1/              # REST endpoints, versioned
      grpc/v1/              # gRPC endpoints, versioned
    services/               # business logic (calls repositories; can version methods)
    modules/                # dependency-injection wiring (e.g. repositories)
    tests/                  # unit tests for this service
    main.py                 # service entrypoint
  accounts/                 # same structure as pets/
  auth/                     # same structure as pets/
integration-tests/          # cross-service tests
migrations/                 # Alembic migration scripts
```

```bash
mkdir -p src/libs
for svc in pets accounts auth; do
  mkdir -p src/$svc/controllers/http/v1 \
           src/$svc/controllers/grpc/v1 \
           src/$svc/services \
           src/$svc/modules \
           src/$svc/tests
  touch src/$svc/main.py
done
mkdir -p integration-tests migrations
```

**Why versioned controllers (`v1`):** API versioning (a stated requirement) lets you introduce
breaking changes as `v2` without breaking existing clients.

---

## 7. Environment configuration

Create **`.env.example`** — a *template* of every environment variable the app needs, with dummy
values.

**Why:** it documents required config for new developers, and it's safe to commit (no real secrets).
Each developer copies it to `.env` (which is git-ignored) and fills in real values.

```bash
# .env.example
ENVIRONMENT=development        # drives DEBUG on/off, CORS, etc.
DEBUG=true

POSTGRES_USER=app
POSTGRES_PASSWORD=changeme
POSTGRES_DB=microservices
DATABASE_URL=postgresql+psycopg://app:changeme@localhost:5432/microservices

REDIS_URL=redis://localhost:6379/0

JWT_SECRET=replace-with-a-long-random-string
```

Then:
```bash
cp .env.example .env
```

**Why `ENVIRONMENT` drives `DEBUG`:** a requirement — you want verbose errors locally but never in
production. Deriving one from the other prevents accidentally shipping debug mode.

---

## 8. Docker Compose for dependencies

Create **`docker-compose.yml`** to run PostgreSQL and Redis locally.

**Why:** instead of installing and configuring Postgres/Redis on your OS, Compose spins up
pinned, throwaway containers. Everyone gets the identical versions.

> Rule: use **Alpine** images with **fixed versions** (small + reproducible).

```yaml
services:
  db:
    image: postgres:17-alpine       # fixed version, alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine           # fixed version, alpine
    ports:
      - "6379:6379"

volumes:
  pgdata:
```

Start them:
```bash
docker compose up -d
```

**Why the named volume (`pgdata`):** it persists database data across container restarts, so you
don't lose your tables every time you stop the container.

---

## 9. Makefile for common commands

Create a **`Makefile`** so long commands become short, memorable ones.

**Why:** nobody remembers `uv run ruff format . && uv run ruff check --fix .`. `make format` is
easier, self-documenting, and used identically by humans and CI.

```makefile
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
	docker compose up -d

down:         ## stop db + redis
	docker compose down

migrate:      ## apply latest db migrations
	uv run alembic upgrade head

run:          ## run the pets service (example)
	uv run uvicorn src.pets.main:app --reload
```

---

## 10. Continuous Integration (GitHub Actions)

Create **`.github/workflows/ci.yml`**.

**Why:** CI runs your checks automatically on every push/PR, so broken formatting, lint errors, or
failing tests are caught *before* they reach the main branch — not after.

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v5

      - name: Set up Python
        run: uv python install

      - name: Install dependencies
        run: uv sync

      - name: Format check
        run: uv run ruff format --check .

      - name: Lint
        run: uv run ruff check .

      - name: Unit tests
        run: uv run pytest
```

**Why `ruff format --check` (not `format`) in CI:** CI should *verify*, not modify. It fails if code
isn't already formatted, forcing the fix to happen on the developer's machine.

---

## 11. Documentation files

### `README.md`
**Why:** the front door of the repo. A new developer (or future you) should be able to read it and
get running. Include:
- the tech stack,
- what the project does,
- the architecture (embed images from `diagrams/` / the `.excalidraw` diagram),
- setup + run instructions (link to this guide).

### `CLAUDE.md`
**Why:** context file for Claude Code. It tells the AI assistant the project conventions (stack,
folder structure, commands, coding standards) so its help stays consistent with your standards.
You can generate a starter with the `/init` command.

---

## 12. Alembic initialization (migrations skeleton)

**Why:** even before real tables exist, set up Alembic so schema changes are versioned from the
start. Each future model change becomes a reviewable, reversible migration script.

```bash
uv run alembic init migrations
```

Then point `sqlalchemy.url` in the generated config at your `DATABASE_URL` (read it from the
environment rather than hard-coding). No tables yet — that comes with the Account/Pet services.

---

## Verification checklist

Before moving on to implementing services, confirm the skeleton works:

- [ ] `uv sync` installs cleanly and creates `.venv`
- [ ] `docker compose up -d` starts `db` and `redis` (check `docker compose ps`)
- [ ] `make lint` and `make format` run with no errors
- [ ] `make test` runs (even with zero tests) and exits successfully
- [ ] `.env` exists locally and is git-ignored; `.env.example` is committed
- [ ] Pushing to a branch triggers the GitHub Actions CI and it passes
- [ ] `README.md` and `CLAUDE.md` exist

Once all boxes are checked, you have a runnable skeleton and can start on **section 2 (Account
service)** from `tasks.md`.

---

## Quick reference: what each tool is for

| Category | Tool | One-line purpose |
|----------|------|------------------|
| Env/deps | uv | Manage venv + dependencies + lockfile |
| Runtime | FastAPI + uvicorn | Build and serve the HTTP APIs |
| Data | SQLAlchemy + Alembic + psycopg | ORM, migrations, Postgres driver |
| Cache | redis-py | Talk to Redis for caching |
| Validation | pydantic (+settings) | DTOs, input validation, config |
| Security | bcrypt, slowapi, OAuth/JWT | Hash passwords, rate-limit, auth |
| Internal comms | grpcio + grpcio-tools | Fast service-to-service calls |
| Structure | dependency-injector | Wire services/repositories |
| Logging | loguru | Structured, readable logs |
| Quality | ruff, pytest | Lint/format + unit tests |
| Ops | Docker Compose, Makefile, GitHub Actions | Local deps, command shortcuts, CI |
