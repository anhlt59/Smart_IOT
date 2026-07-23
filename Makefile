# POC on-prem IIoT — root Makefile.
# `make up` from a clean machine brings the full edge stack up.

BACKEND_DIR   := apps/backend
EDGE_DIR      := infra/edge
COMPOSE       := docker compose -f $(EDGE_DIR)/docker-compose.yml --env-file $(EDGE_DIR)/.env

.PHONY: help init up down logs ps build test lint fmt tidy migrate-up migrate-down run-all

help: ## List targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-14s %s\n", $$1, $$2}'

init: ## Create local config from templates (.env, EMQX users) if missing
	@test -f $(EDGE_DIR)/.env || { cp $(EDGE_DIR)/.env.example $(EDGE_DIR)/.env; echo "created $(EDGE_DIR)/.env — change the *_change_me values"; }
	@test -f $(EDGE_DIR)/emqx/users-bootstrap.csv || { cp $(EDGE_DIR)/emqx/users-bootstrap.csv.example $(EDGE_DIR)/emqx/users-bootstrap.csv; echo "created $(EDGE_DIR)/emqx/users-bootstrap.csv — keep passwords in sync with .env"; }

up: init ## Build and start the full edge stack (7 containers + migrate)
	$(COMPOSE) up -d --build

down: init ## Stop the stack (volumes preserved)
	$(COMPOSE) down

ps: init ## Container status + health
	$(COMPOSE) ps

logs: init ## Tail logs of all services
	$(COMPOSE) logs -f --tail=100

build: ## Compile the backend
	cd $(BACKEND_DIR) && go build ./...

test: ## Run backend unit tests
	cd $(BACKEND_DIR) && go test ./...

lint: ## go vet + golangci-lint (if installed)
	cd $(BACKEND_DIR) && go vet ./...
	@command -v golangci-lint >/dev/null 2>&1 && (cd $(BACKEND_DIR) && golangci-lint run) || echo "golangci-lint not installed — skipped (CI runs it)"

fmt: ## gofmt all backend code
	cd $(BACKEND_DIR) && gofmt -w .

tidy: ## go mod tidy
	cd $(BACKEND_DIR) && go mod tidy

migrate-up: init ## Apply pending migrations (one-shot container)
	$(COMPOSE) run --rm migrate

migrate-down: init ## Roll back the last migration
	@set -a; . $(EDGE_DIR)/.env; set +a; \
	$(COMPOSE) run --rm migrate -path=/migrations \
		-database "postgres://$${POSTGRES_USER}:$${POSTGRES_PASSWORD}@postgres:5432/$${POSTGRES_DB}?sslmode=disable" down 1

run-all: init ## Run the app on the host (role=all) against the compose services
	@set -a; . $(EDGE_DIR)/.env; set +a; \
	export POSTGRES_DSN="postgres://$${POSTGRES_USER}:$${POSTGRES_PASSWORD}@localhost:5433/$${POSTGRES_DB}?sslmode=disable"; \
	export REDIS_ADDR=localhost:6379 MQTT_BROKER_URL=tcp://localhost:1883; \
	cd $(BACKEND_DIR) && go run ./cmd/app --role=all
