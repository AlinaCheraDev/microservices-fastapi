1. Tech stack used 
- take latest stable version with exact version !!!!!!!!!!!!!!!!!!
- python for services
- FastAPI for APIs
- SQLAlchemy for ORM
- Alembic for db migration
- redis-py
- slowapi for rate limiting in FastAPI
- oauth from FastAPI for security
- pydantic for DTOs, data validation
- Swagger/OpenAPI for API documentation from FastAPI
- bcrypt for password hashing
- grpcio, grpcio-tools for gRPC and protocol buffer compiler
- Dependency Injector for dependency injection
- uvicorn for FastAPI deployment
- Makefile for commands (like prettify, lint, deploy 1 or all, migrations)
- loguru for logging


2. Communication protocols
- REST between users and Auth service
- grpc between Auth, Account and Pet services


3. Other design decisions such as coding standards like linting, typing, prettifying, CI/CD, unit testing, integration testing, version control
- Github for version control, monorepo
- Github Actions for CI/CD, build, linting, formatting, unit testing, ...
- uv for python dependencies
- ruff for linting and code formatting
- pytest for unit testing
- docker-compose for dependencies
- integration testing


4. Folder structure
/src
/src/libs    # connecting to db, html - grpc convertor, errors, anything shared

/src/pets
/src/pets/controllers
/src/pets/controllers/http
/src/pets/controllers/http/v1
/src/pets/controllers/grpc
/src/pets/controllers/grpc/v1
/src/pets/tests
/src/pets/services/    # bussiness logic, repository is used, can have method versioning
/src/pets/modules/     # dependecy injection like repository
/src/pets/main.py

/src/auth
/src/accounts
...

/integration-tests

/migrations


5. Required external services (like database or caching)
- PostgreSQL for persistent storage
- Redis for caching
