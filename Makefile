COMPOSE=docker compose

# Load .env file if it exists
ifneq (,$(wildcard .env))
	include .env
	export
endif

install:
	pip install -r requirements.txt
	pip install pytest flake8

run:
	set DATABASE_URL=$(DATABASE_URL) && python app/main.py

# ── Local test setup ─────────────────────────────────────────────────────────

db-start:
	@echo "Starting database container..."
	$(COMPOSE) up -d db
	@echo "Waiting for database to become healthy..."
	@until docker inspect --format='{{.State.Health.Status}}' $$($(COMPOSE) ps -q db) | grep -q healthy; do \
		echo "  still waiting..."; \
		sleep 2; \
	done
	@echo "Database is healthy."

db-stop:
	@echo "Stopping database container..."
	$(COMPOSE) down
	@echo "Database is down."

test: db-start
	@echo "Running tests..."
	DATABASE_URL=$(DATABASE_URL) pytest app/test_main.py -v
	@echo "Tests complete."

# ── Other commands ───────────────────────────────────────────────────────────

lint:
	black .

clean:
	rm app/__pycache__

docker-up:
	$(COMPOSE) up --build

docker-down:
	$(COMPOSE) down

docker-clean:
	$(COMPOSE) down -v