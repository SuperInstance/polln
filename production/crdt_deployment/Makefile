# CRDT Coordination Service Makefile
# Convenient commands for development and deployment

.PHONY: help install test lint build start stop restart logs health metrics clean deploy-k8s

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
PIP := pip3
DOCKER_COMPOSE := docker-compose
KUBECTL := kubectl

# Colors for help output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

##@ General

help: ## Display this help message
	@echo "$(BLUE)CRDT Coordination Service$(NC)"
	@echo ""
	@echo "$(GREEN)Usage:$(NC)"
	@echo "  make <target>"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@gawk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

##@ Development

install: ## Install Python dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)Dependencies installed$(NC)"

test: ## Run test suite
	@echo "$(BLUE)Running tests...$(NC)"
	$(PYTHON) -m pytest test_crdt_service.py -v -s
	@echo "$(GREEN)Tests completed$(NC)"

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	$(PYTHON) -m pytest test_crdt_service.py -v --cov=crdt_coordination_service --cov-report=html
	@echo "$(GREEN)Coverage report generated in htmlcov/$(NC)"

lint: ## Run linting (flake8)
	@echo "$(BLUE)Linting code...$(NC)"
	flake8 crdt_coordination_service.py --max-line-length=120
	@echo "$(GREEN)Linting completed$(NC)"

format: ## Format code with black
	@echo "$(BLUE)Formatting code...$(NC)"
	black crdt_coordination_service.py test_crdt_service.py
	@echo "$(GREEN)Code formatted$(NC)"

run: ## Run service locally (without Docker)
	@echo "$(BLUE)Starting service locally...$(NC)"
	$(PYTHON) crdt_coordination_service.py

##@ Docker

build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	$(DOCKER_COMPOSE) build
	@echo "$(GREEN)Images built$(NC)"

rebuild: ## Rebuild Docker images without cache
	@echo "$(BLUE)Rebuilding Docker images...$(NC)"
	$(DOCKER_COMPOSE) build --no-cache
	@echo "$(GREEN)Images rebuilt$(NC)"

start: ## Start all services
	@echo "$(BLUE)Starting services...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)Services started$(NC)"
	@echo ""
	@echo "$(YELLOW)Services available at:$(NC)"
	@echo "  - Node 1: http://localhost:8001"
	@echo "  - Node 2: http://localhost:8002"
	@echo "  - Node 3: http://localhost:8003"
	@echo "  - Prometheus: http://localhost:9090"
	@echo "  - Grafana: http://localhost:3000"

stop: ## Stop all services
	@echo "$(BLUE)Stopping services...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)Services stopped$(NC)"

restart: ## Restart all services
	@echo "$(BLUE)Restarting services...$(NC)"
	$(DOCKER_COMPOSE) restart
	@echo "$(GREEN)Services restarted$(NC)"

logs: ## Show service logs (follow mode)
	@echo "$(BLUE)Showing logs...$(NC)"
	$(DOCKER_COMPOSE) logs -f

logs-node-1: ## Show logs for node 1
	$(DOCKER_COMPOSE) logs -f crdt-node-1

logs-node-2: ## Show logs for node 2
	$(DOCKER_COMPOSE) logs -f crdt-node-2

logs-node-3: ## Show logs for node 3
	$(DOCKER_COMPOSE) logs -f crdt-node-3

ps: ## Show running containers
	@$(DOCKER_COMPOSE) ps

##@ Testing & Debugging

health: ## Check service health
	@echo "$(BLUE)Checking health...$(NC)"
	@curl -sf http://localhost:8001/health | jq '.' || echo "$(YELLOW)Node 1 is unhealthy$(NC)"
	@curl -sf http://localhost:8002/health | jq '.' || echo "$(YELLOW)Node 2 is unhealthy$(NC)"
	@curl -sf http://localhost:8003/health | jq '.' || echo "$(YELLOW)Node 3 is unhealthy$(NC)"

test-api: ## Run API integration tests
	@echo "$(BLUE)Testing API...$(NC)"
	@echo "$(YELLOW)Testing read operation...$(NC)"
	@curl -s -X POST http://localhost:8001/operation \
		-H "Content-Type: application/json" \
		-d '{"op_id":"test-001","op_type":"read","key":"test"}' | jq '.'
	@echo ""
	@echo "$(YELLOW)Testing write operation...$(NC)"
	@curl -s -X POST http://localhost:8001/operation \
		-H "Content-Type: application/json" \
		-d '{"op_id":"test-002","op_type":"write","key":"test","value":"hello"}' | jq '.'
	@echo ""
	@echo "$(YELLOW)Testing metrics endpoint...$(NC)"
	@curl -s http://localhost:8001/metrics | jq '.'

metrics: ## Show metrics from all nodes
	@echo "$(BLUE)Fetching metrics...$(NC)"
	@echo "$(YELLOW)=== Node 1 ===$(NC)"
	@curl -s http://localhost:8001/metrics/detail | jq '.'
	@echo ""
	@echo "$(YELLOW)=== Node 2 ===$(NC)"
	@curl -s http://localhost:8002/metrics/detail | jq '.'
	@echo ""
	@echo "$(YELLOW)=== Node 3 ===$(NC)"
	@curl -s http://localhost:8003/metrics/detail | jq '.'

benchmark: ## Run performance benchmark
	@echo "$(BLUE)Running benchmark...$(NC)"
	@$(PYTHON) -c "
import asyncio
import time
import aiohttp

async def benchmark():
    async with aiohttp.ClientSession() as session:
        tasks = []
        start = time.time()

        for i in range(100):
            payload = {
                'op_id': f'bench-{i}',
                'op_type': 'write',
                'key': f'key-{i}',
                'value': f'value-{i}'
            }
            tasks.append(session.post(
                'http://localhost:8001/operation',
                json=payload
            ))

        responses = await asyncio.gather(*tasks)
        elapsed = time.time() - start

        success = sum(1 for r in responses if r.status == 200)
        throughput = success / elapsed

        print(f'Successful: {success}/100')
        print(f'Time: {elapsed:.2f}s')
        print(f'Throughput: {throughput:.2f} ops/sec')

asyncio.run(benchmark())
"

shell-node-1: ## Open shell in node 1 container
	$(DOCKER_COMPOSE) exec crdt-node-1 /bin/bash

shell-node-2: ## Open shell in node 2 container
	$(DOCKER_COMPOSE) exec crdt-node-2 /bin/bash

shell-node-3: ## Open shell in node 3 container
	$(DOCKER_COMPOSE) exec crdt-node-3 /bin/bash

##@ Kubernetes

deploy-k8s: ## Deploy to Kubernetes
	@echo "$(BLUE)Deploying to Kubernetes...$(NC)"
	$(KUBECTL) apply -f kubernetes-deployment.yaml
	@echo "$(GREEN)Deployed to Kubernetes$(NC)"
	@echo ""
	@echo "$(YELLOW)Waiting for pods to be ready...$(NC)"
	$(KUBECTL) wait --for=condition=ready pod -l app=crdt-coordination -n crdt-coordination --timeout=120s

undeploy-k8s: ## Remove from Kubernetes
	@echo "$(BLUE)Removing from Kubernetes...$(NC)"
	$(KUBECTL) delete -f kubernetes-deployment.yaml
	@echo "$(GREEN)Removed from Kubernetes$(NC)"

k8s-logs: ## Show Kubernetes pod logs
	$(KUBECTL) logs -l app=crdt-coordination -n crdt-coordination -f

k8s-status: ## Show Kubernetes resources status
	@echo "$(BLUE)Kubernetes Resources:$(NC)"
	@echo ""
	@echo "$(YELLOW)Pods:$(NC)"
	@$(KUBECTL) get pods -n crdt-coordination
	@echo ""
	@echo "$(YELLOW)Services:$(NC)"
	@$(KUBECTL) get svc -n crdt-coordination
	@echo ""
	@echo "$(YELLOW)StatefulSets:$(NC)"
	@$(KUBECTL) get statefulsets -n crdt-coordination

k8s-scale: ## Scale Kubernetes deployment (usage: make k8s-scale N=5)
	@echo "$(BLUE)Scaling to $(N) replicas...$(NC)"
	$(KUBECTL) scale statefulset crdt-coordination --replicas=$(N) -n crdt-coordination

k8s-port-forward: ## Port forward to local (usage: make k8s-port-forward POD=pod-name)
	$(KUBECTL) port-forward $(POD) -n crdt-coordination 8001:8001

##@ Monitoring

prometheus: ## Open Prometheus in browser
	@echo "$(BLUE)Opening Prometheus...$(NC)"
	@command -v xdg-open >/dev/null && xdg-open http://localhost:9090 || open http://localhost:9090 || echo "Open http://localhost:9090 in your browser"

grafana: ## Open Grafana in browser
	@echo "$(BLUE)Opening Grafana...$(NC)"
	@command -v xdg-open >/dev/null && xdg-open http://localhost:3000 || open http://localhost:3000 || echo "Open http://localhost:3000 in your browser (admin/admin)"

dashboards: ## Setup Grafana dashboards
	@echo "$(BLUE)Setting up dashboards...$(NC)"
	@echo "Grafana is available at http://localhost:3000"
	@echo "Default credentials: admin / admin"
	@echo "Prometheus datasource should be auto-configured"

##@ Cleanup

clean: ## Stop and remove all containers, volumes, networks
	@echo "$(BLUE)Cleaning up...$(NC)"
	$(DOCKER_COMPOSE) down -v
	@echo "$(GREEN)Cleanup complete$(NC)"

clean-all: clean ## Clean everything including images
	@echo "$(BLUE)Removing images...$(NC)"
	docker rmi crdt-deployment_crdt-node-1 crdt-deployment_crdt-node-2 crdt-deployment_crdt-node-3 2>/dev/null || true
	@echo "$(GREEN)Full cleanup complete$(NC)"

reset: clean-all ## Reset everything to initial state
	@echo "$(BLUE)Resetting to initial state...$(NC)"
	git clean -fdx
	@echo "$(GREEN)Reset complete$(NC)"

##@ Utilities

check-prereqs: ## Check prerequisites
	@echo "$(BLUE)Checking prerequisites...$(NC)"
	@command -v docker >/dev/null || (echo "$(YELLOW)Docker not found$(NC)" && exit 1)
	@command -v docker-compose >/dev/null || (echo "$(YELLOW)Docker Compose not found$(NC)" && exit 1)
	@command -v python3 >/dev/null || (echo "$(YELLOW)Python 3 not found$(NC)" && exit 1)
	@echo "$(GREEN)All prerequisites met$(NC)"

version: ## Show version information
	@echo "$(BLUE)CRDT Coordination Service$(NC)"
	@echo "Version: 1.0.0"
	@echo ""
	@echo "$(YELLOW)Tool versions:$(NC)"
	@docker --version
	@docker-compose --version
	@python3 --version
