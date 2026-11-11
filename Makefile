COMPOSE ?= docker compose
.PHONY: init up down logs migrate check schema
init:
	python3 scripts/init_env.py
up: init
	$(COMPOSE) up --build -d
down:
	$(COMPOSE) down
logs:
	$(COMPOSE) logs --tail=100 -f api worker
migrate:
	uv run --project backend python backend/manage.py migrate
check:
	uv run --project backend ruff check --config backend/pyproject.toml backend scripts
	uv run --project backend ruff format --config backend/pyproject.toml --check backend scripts
	uv run --project backend pytest backend/tests
	uv run --project backend python backend/manage.py makemigrations --check --dry-run
	cd frontend && npm run lint && npm run typecheck && npm test && npm run build && npm audit --audit-level=high
schema:
	uv run --project backend python backend/manage.py spectacular --file docs/openapi.yaml --validate --fail-on-warn

.PHONY: prod-config prod-up prod-down package
PROD_ENV ?= .env.production
PROD_COMPOSE = $(COMPOSE) --env-file $(PROD_ENV) -f compose.production.yaml
prod-config:
	$(PROD_COMPOSE) config --quiet
prod-up:
	$(PROD_COMPOSE) up --build -d --wait --wait-timeout 180
prod-down:
	$(PROD_COMPOSE) down
package:
	python3 scripts/package_delivery.py --output entregas/unieuro-revista-docker.zip
