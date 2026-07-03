1. Project repository and setup + access lui Darius
- github repository with .gitignore (template de fastapi sau python) - look for fastapi cli
- uv (venv)
- cu uv adaug requirements
- docker compose (db, redis) - alipine, fixed version
- pyproject.toml file generat de uv, aici se pun reguli in plus, ca formatting (120), linting rules - pot intreba ai
- folder structure
- makefile
- .python-version - ajuta ide sa isi dea seama ce python este folosit de proiect
- readme: stack, ce vrem sa faca, architecture, pot pune poze aici
- .env.example
- ci/cd github actions: run "build"/erori, format test, linting, unit teste
- claude context CLAUDE.md
- FUTURE: Dockefile to build the app and prepare for deployment

2. Account service
- create account repository and tables with initial setup script (for admin and roles / permissions)
- account retrieval (all and by id)
- account creation (with roles / permissions)
- account update (with roles / permissions)
- account soft delete
- account validate (user / pass match)

3. Autentificare si autorizare
- register with default roles/permissions
- login and see a home page
- logout
- password recovery

4. Pet service
- create account repository and table
- pet retrieval (all, filtered and by id)
- pet creation
- pet update
- pet soft delete

5. Caching (Redis, db)
