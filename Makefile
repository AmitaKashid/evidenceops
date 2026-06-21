SHELL := /bin/bash

.PHONY: up down backend-install backend-test backend-lint frontend-install frontend-lint seed demo

up:
	docker compose up --build

down:
	docker compose down --remove-orphans

backend-install:
	cd backend && python -m pip install -e '.[dev]'

backend-test:
	cd backend && pytest -q

backend-lint:
	cd backend && ruff check app tests && mypy app

frontend-install:
	cd frontend && npm install

frontend-lint:
	cd frontend && npm run lint && npm run typecheck

seed:
	cd backend && python -m app.services.seed_demo

demo:
	curl -s -X POST http://localhost:8000/api/v1/tasks/runs \
		-H 'Content-Type: application/json' \
		-d '{"title":"Vendor selection brief","request":"Review the approved vendor documents, compare vendors against internal security requirements, calculate a three-year total cost of ownership, identify policy gaps, and prepare a management decision brief with evidence citations.","model_profile":"enterprise-balanced"}' | python -m json.tool
