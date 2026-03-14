#!/bin/bash
# CRDT Coordination Service Deployment Script
# Automates deployment, testing, and monitoring setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
NETWORK_NAME="crdt-network"
SERVICE_NAME="crdt-coordination"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    log_success "Prerequisites check passed"
}

build_images() {
    log_info "Building Docker images..."

    docker-compose build

    log_success "Docker images built successfully"
}

start_services() {
    log_info "Starting CRDT Coordination Service..."

    docker-compose up -d

    log_success "Services started"
}

stop_services() {
    log_info "Stopping CRDT Coordination Service..."

    docker-compose down

    log_success "Services stopped"
}

restart_services() {
    log_info "Restarting CRDT Coordination Service..."

    docker-compose restart

    log_success "Services restarted"
}

check_health() {
    log_info "Checking service health..."

    # Wait for services to be ready
    sleep 10

    # Check node 1
    if curl -sf http://localhost:8001/health > /dev/null; then
        log_success "Node 1 is healthy"
    else
        log_error "Node 1 health check failed"
        return 1
    fi

    # Check node 2
    if curl -sf http://localhost:8002/health > /dev/null; then
        log_success "Node 2 is healthy"
    else
        log_error "Node 2 health check failed"
        return 1
    fi

    # Check node 3
    if curl -sf http://localhost:8003/health > /dev/null; then
        log_success "Node 3 is healthy"
    else
        log_error "Node 3 health check failed"
        return 1
    fi

    log_success "All nodes are healthy"
}

run_tests() {
    log_info "Running integration tests..."

    # Test read operation
    log_info "Testing read operation..."
    response=$(curl -s -X POST http://localhost:8001/operation \
        -H "Content-Type: application/json" \
        -d '{
            "op_id": "test-read-001",
            "op_type": "read",
            "key": "test_key"
        }')

    if echo "$response" | grep -q '"status":"success"'; then
        log_success "Read operation test passed"
    else
        log_error "Read operation test failed"
        return 1
    fi

    # Test write operation
    log_info "Testing write operation..."
    response=$(curl -s -X POST http://localhost:8001/operation \
        -H "Content-Type: application/json" \
        -d '{
            "op_id": "test-write-001",
            "op_type": "write",
            "key": "test_key",
            "value": "test_value"
        }')

    if echo "$response" | grep -q '"status":"success"'; then
        log_success "Write operation test passed"
    else
        log_error "Write operation test failed"
        return 1
    fi

    # Test metrics endpoint
    log_info "Testing metrics endpoint..."
    response=$(curl -s http://localhost:8001/metrics)

    if echo "$response" | grep -q '"node_id"'; then
        log_success "Metrics endpoint test passed"
    else
        log_error "Metrics endpoint test failed"
        return 1
    fi

    log_success "All integration tests passed"
}

show_logs() {
    log_info "Showing service logs (Ctrl+C to exit)..."
    docker-compose logs -f
}

show_status() {
    log_info "Service status:"
    docker-compose ps
}

show_metrics() {
    log_info "Fetching metrics from all nodes..."

    echo ""
    echo "=== Node 1 Metrics ==="
    curl -s http://localhost:8001/metrics | jq '.'

    echo ""
    echo "=== Node 2 Metrics ==="
    curl -s http://localhost:8002/metrics | jq '.'

    echo ""
    echo "=== Node 3 Metrics ==="
    curl -s http://localhost:8003/metrics | jq '.'
}

scale_nodes() {
    local new_scale=$1

    if [ -z "$new_scale" ]; then
        log_error "Please specify the number of nodes"
        echo "Usage: $0 scale <number_of_nodes>"
        exit 1
    fi

    log_info "Scaling to $new_scale nodes..."
    docker-compose up -d --scale crdt-node=$new_scale
    log_success "Scaled to $new_scale nodes"
}

setup_monitoring() {
    log_info "Setting up monitoring stack..."

    # Check if Prometheus is accessible
    if curl -sf http://localhost:9090/-/healthy > /dev/null; then
        log_success "Prometheus is running at http://localhost:9090"
    else
        log_warning "Prometheus is not accessible"
    fi

    # Check if Grafana is accessible
    if curl -sf http://localhost:3000/api/health > /dev/null; then
        log_success "Grafana is running at http://localhost:3000"
        log_info "Default credentials: admin / admin"
    else
        log_warning "Grafana is not accessible"
    fi
}

clean_deployment() {
    log_warning "Cleaning up deployment..."

    # Stop services
    docker-compose down

    # Remove volumes
    docker-compose down -v

    # Remove network (if it exists)
    docker network rm $NETWORK_NAME 2>/dev/null || true

    log_success "Cleanup complete"
}

# Main command dispatcher
case "${1:-}" in
    "start")
        check_prerequisites
        build_images
        start_services
        check_health
        setup_monitoring
        log_success "Deployment complete!"
        echo ""
        echo "Services available at:"
        echo "  - Node 1: http://localhost:8001"
        echo "  - Node 2: http://localhost:8002"
        echo "  - Node 3: http://localhost:8003"
        echo "  - Prometheus: http://localhost:9090"
        echo "  - Grafana: http://localhost:3000"
        ;;

    "stop")
        stop_services
        ;;

    "restart")
        restart_services
        check_health
        ;;

    "status")
        show_status
        ;;

    "logs")
        show_logs
        ;;

    "health")
        check_health
        ;;

    "test")
        run_tests
        ;;

    "metrics")
        show_metrics
        ;;

    "scale")
        scale_nodes $2
        ;;

    "monitor")
        setup_monitoring
        ;;

    "clean")
        clean_deployment
        ;;

    "rebuild")
        stop_services
        build_images
        start_services
        check_health
        ;;

    *)
        echo "CRDT Coordination Service Deployment Script"
        echo ""
        echo "Usage: $0 <command>"
        echo ""
        echo "Commands:"
        echo "  start       - Start the deployment (build, start, health check)"
        echo "  stop        - Stop all services"
        echo "  restart     - Restart all services"
        echo "  status      - Show service status"
        echo "  logs        - Show service logs (follow mode)"
        echo "  health      - Check service health"
        echo "  test        - Run integration tests"
        echo "  metrics     - Show metrics from all nodes"
        echo "  scale <n>   - Scale to n nodes"
        echo "  monitor     - Setup monitoring stack info"
        echo "  clean       - Stop and remove all containers, volumes, networks"
        echo "  rebuild     - Rebuild and restart services"
        echo ""
        echo "Examples:"
        echo "  $0 start              # Initial deployment"
        echo "  $0 test               # Run tests"
        echo "  $0 metrics            # View metrics"
        echo "  $0 scale 5            # Scale to 5 nodes"
        ;;
esac
