# SuperInstance Monitoring Stack - Makefile

.PHONY: help start stop restart status logs test example backup clean install deps

# Default target
.DEFAULT_GOAL := help

# Variables
COMPOSE := docker compose
PYTHON := python3
VENV := venv
ACTIVATE := $(VENV)/bin/activate

# Colors
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

help: ## Show this help message
	@echo "$(BLUE)SuperInstance Monitoring Stack$(NC)"
	@echo ""
	@echo "$(GREEN)Usage:$(NC) make [target]"
	@echo ""
	@echo "$(GREEN)Targets:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

deps: ## Install Python dependencies
	@echo "$(GREEN)Installing Python dependencies...$(NC)"
	@test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	@. $(ACTIVATE) && pip install --quiet --upgrade pip
	@. $(ACTIVATE) && pip install --quiet -r requirements.txt
	@echo "$(GREEN)Dependencies installed!$(NC)"

install: deps ## Install all dependencies and setup environment
	@echo "$(GREEN)Setting up environment...$(NC)"
	@test -f .env || cp .env.example .env
	@mkdir -p prometheus grafana/provisioning grafana/dashboards alertmanager
	@echo "$(GREEN)Setup complete!$(NC)"

start: ## Start monitoring stack
	@echo "$(GREEN)Starting monitoring stack...$(NC)"
	$(COMPOSE) up -d
	@sleep 5
	@echo "$(GREEN)Monitoring stack started!$(NC)"
	@$(MAKE) status

stop: ## Stop monitoring stack
	@echo "$(YELLOW)Stopping monitoring stack...$(NC)"
	$(COMPOSE) down
	@echo "$(GREEN)Monitoring stack stopped!$(NC)"

restart: ## Restart monitoring stack
	@echo "$(YELLOW)Restarting monitoring stack...$(NC)"
	$(COMPOSE) restart
	@echo "$(GREEN)Monitoring stack restarted!$(NC)"
	@$(MAKE) status

status: ## Show service status
	@echo "$(BLUE)Service Status:$(NC)"
	@$(COMPOSE) ps
	@echo ""
	@echo "$(BLUE)Access URLs:$(NC)"
	@echo "  Grafana:       http://localhost:3000 (admin/admin)"
	@echo "  Prometheus:    http://localhost:9091"
	@echo "  Jaeger:        http://localhost:16686"
	@echo "  Alertmanager:  http://localhost:9093"
	@echo "  Metrics:       http://localhost:9090/metrics"

logs: ## Show logs from all services
	$(COMPOSE) logs -f

logs-prometheus: ## Show Prometheus logs
	$(COMPOSE) logs -f prometheus

logs-grafana: ## Show Grafana logs
	$(COMPOSE) logs -f grafana

logs-jaeger: ## Show Jaeger logs
	$(COMPOSE) logs -f jaeger

logs-alertmanager: ## Show Alertmanager logs
	$(COMPOSE) logs -f alertmanager

test: ## Run tests
	@echo "$(GREEN)Running tests...$(NC)"
	@test -d $(VENV) || $(MAKE) deps
	@. $(ACTIVATE) && pytest test_monitoring.py -v
	@echo "$(GREEN)Tests completed!$(NC)"

test-coverage: ## Run tests with coverage
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	@test -d $(VENV) || $(MAKE) deps
	@. $(ACTIVATE) && pytest test_monitoring.py --cov=. --cov-report=html
	@echo "$(GREEN)Coverage report generated: htmlcov/index.html$(NC)"

example: ## Run example usage
	@echo "$(GREEN)Running example...$(NC)"
	@test -d $(VENV) || $(MAKE) deps
	@. $(ACTIVATE) && python example_usage.py

backup: ## Backup configuration and data
	@echo "$(GREEN)Backing up monitoring data...$(NC)"
	@mkdir -p backups
	@tar -czf backups/backup_$$(date +%Y%m%d_%H%M%S).tar.gz \
		prometheus/ grafana/ alertmanager/ .env 2>/dev/null || true
	@echo "$(GREEN)Backup completed!$(NC)"

restore: ## Restore from backup (usage: make restore BACKUP=file.tar.gz)
	@test -n "$(BACKUP)" || (echo "$(YELLOW)Usage: make restore BACKUP=file.tar.gz$(NC)" && exit 1)
	@echo "$(YELLOW)Restoring from $(BACKUP)...$(NC)"
	@tar -xzf $(BACKUP)
	@echo "$(GREEN)Restore completed!$(NC)"

clean: ## Clean up
	@echo "$(YELLOW)Cleaning up...$(NC)"
	@rm -rf $(VENV)
	@rm -rf htmlcov/
	@rm -rf .pytest_cache/
	@rm -rf __pycache__/
	@rm -rf .coverage
	@echo "$(GREEN)Cleanup completed!$(NC)"

clean-docker: ## Clean up Docker resources
	@echo "$(YELLOW)Cleaning Docker resources...$(NC)"
	$(COMPOSE) down -v
	@docker system prune -f
	@echo "$(GREEN)Docker cleanup completed!$(NC)"

rebuild: ## Rebuild all containers
	@echo "$(YELLOW)Rebuilding containers...$(NC)"
	$(COMPOSE) build --no-cache
	@echo "$(GREEN)Rebuild completed!$(NC)"

pull: ## Pull latest images
	@echo "$(GREEN)Pulling latest images...$(NC)"
	$(COMPOSE) pull
	@echo "$(GREEN)Pull completed!$(NC)"

update: pull rebuild ## Update monitoring stack (pull and rebuild)

config-prometheus: ## Validate Prometheus configuration
	@echo "$(GREEN)Validating Prometheus configuration...$(NC)"
	@docker run --rm -v $$(pwd)/prometheus:/etc/prometheus \
		prom/prometheus:latest \
		promtool check config /etc/prometheus/prometheus.yml

config-alertmanager: ## Validate Alertmanager configuration
	@echo "$(GREEN)Validating Alertmanager configuration...$(NC)"
	@docker run --rm -v $$(pwd)/alertmanager:/etc/alertmanager \
		prom/alertmanager:latest \
		amtool check-config /etc/alertmanager/alertmanager.yml

validate: config-prometheus config-alertmanager ## Validate all configurations

metrics: ## View metrics endpoint
	@curl -s http://localhost:9090/metrics | less

health: ## Check health of all services
	@echo "$(BLUE)Checking service health...$(NC)"
	@echo -n "Prometheus: "
	@curl -s http://localhost:9091/-/healthy && echo "$(GREEN)OK$(NC)" || echo "$(RED)DOWN$(NC)"
	@echo -n "Grafana: "
	@curl -s http://localhost:3000/api/health && echo "$(GREEN)OK$(NC)" || echo "$(RED)DOWN$(NC)"
	@echo -n "Jaeger: "
	@curl -s http://localhost:16686/api/status && echo "$(GREEN)OK$(NC)" || echo "$(RED)DOWN$(NC)"
	@echo -n "Alertmanager: "
	@curl -s http://localhost:9093/-/ready && echo "$(GREEN)OK$(NC)" || echo "$(RED)DOWN$(NC)"

# Development targets
dev-setup: install ## Setup development environment
	@echo "$(GREEN)Setting up development environment...$(NC)"
	@. $(ACTIVATE) && pip install --quiet pytest pytest-asyncio pytest-cov black mypy
	@echo "$(GREEN)Dev environment ready!$(NC)"

fmt: ## Format Python code with black
	@echo "$(GREEN)Formatting code...$(NC)"
	@test -d $(VENV) || $(MAKE) deps
	@. $(ACTIVATE) && black monitoring_stack.py example_usage.py test_monitoring.py
	@echo "$(GREEN)Code formatted!$(NC)"

lint: ## Run linting with mypy
	@echo "$(GREEN)Linting code...$(NC)"
	@test -d $(VENV) || $(MAKE) deps
	@. $(ACTIVATE) && mypy monitoring_stack.py
	@echo "$(GREEN)Linting completed!$(NC)"

# CI/CD targets
ci: deps validate test ## Run CI pipeline (deps, validate, test)
	@echo "$(GREEN)CI pipeline passed!$(NC)"

# Production targets
prod-start: ## Start in production mode
	@echo "$(GREEN)Starting production monitoring stack...$(NC)"
	$(COMPOSE) -f docker-compose.yml -f docker-compose.prod.yml up -d
	@$(MAKE) status

prod-stop: ## Stop production monitoring stack
	@echo "$(YELLOW)Stopping production monitoring stack...$(NC)"
	$(COMPOSE) -f docker-compose.yml -f docker-compose.prod.yml down

prod-deploy: validate prod-start ## Deploy to production (validate then start)
	@echo "$(GREEN)Production deployment completed!$(NC)"
