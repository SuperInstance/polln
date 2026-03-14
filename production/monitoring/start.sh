#!/bin/bash
# SuperInstance Monitoring Stack - Quick Start Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    # Check Docker Compose
    if ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    print_info "Prerequisites check passed!"
}

# Create .env file if not exists
setup_environment() {
    print_info "Setting up environment..."

    if [ ! -f .env ]; then
        cat > .env << EOF
# SuperInstance Monitoring Configuration

# Monitoring
PROMETHEUS_PORT=9090
LOG_LEVEL=INFO

# Jaeger Tracing
JAEGER_HOST=jaeger
JAEGER_PORT=6831

# Alerting
SLACK_WEBHOOK_URL=

# Grafana
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin
EOF
        print_info "Created .env file. Please edit it with your configuration."
    else
        print_info ".env file already exists."
    fi
}

# Install Python dependencies
install_python_deps() {
    print_info "Installing Python dependencies..."

    if [ -d "venv" ]; then
        print_warn "Virtual environment already exists. Skipping creation."
    else
        python3 -m venv venv
        print_info "Created virtual environment."
    fi

    # Activate venv and install
    source venv/bin/activate
    pip install --quiet --upgrade pip
    pip install --quiet -r requirements.txt

    print_info "Python dependencies installed!"
}

# Create necessary directories
create_directories() {
    print_info "Creating directories..."

    mkdir -p prometheus
    mkdir -p grafana/provisioning
    mkdir -p grafana/dashboards
    mkdir -p alertmanager

    print_info "Directories created!"
}

# Start monitoring stack
start_stack() {
    print_info "Starting monitoring stack..."

    docker compose up -d

    print_info "Waiting for services to be healthy..."
    sleep 10

    # Check service status
    docker compose ps

    print_info "Monitoring stack started!"
}

# Stop monitoring stack
stop_stack() {
    print_info "Stopping monitoring stack..."

    docker compose down

    print_info "Monitoring stack stopped!"
}

# Restart monitoring stack
restart_stack() {
    print_info "Restarting monitoring stack..."

    docker compose restart

    print_info "Monitoring stack restarted!"
}

# Show logs
show_logs() {
    SERVICE=${1:-}
    if [ -z "$SERVICE" ]; then
        docker compose logs -f
    else
        docker compose logs -f "$SERVICE"
    fi
}

# Show status
show_status() {
    print_info "Service status:"
    docker compose ps

    echo ""
    print_info "Access URLs:"
    echo "  Grafana:       http://localhost:3000 (admin/admin)"
    echo "  Prometheus:    http://localhost:9091"
    echo "  Jaeger:        http://localhost:16686"
    echo "  Alertmanager:  http://localhost:9093"
    echo "  Metrics:       http://localhost:9090/metrics"
}

# Run tests
run_tests() {
    print_info "Running tests..."

    source venv/bin/activate
    pytest test_monitoring.py -v

    print_info "Tests completed!"
}

# Run example
run_example() {
    print_info "Running example..."

    source venv/bin/activate
    python example_usage.py

    print_info "Example completed!"
}

# Backup configuration and data
backup_data() {
    print_info "Backing up monitoring data..."

    BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"

    # Backup configurations
    cp -r prometheus "$BACKUP_DIR/"
    cp -r grafana "$BACKUP_DIR/"
    cp -r alertmanager "$BACKUP_DIR/"
    cp .env "$BACKUP_DIR/"

    print_info "Backup completed: $BACKUP_DIR"
}

# Show help
show_help() {
    cat << EOF
SuperInstance Monitoring Stack - Quick Start Script

Usage: $0 [COMMAND]

Commands:
    start       Start the monitoring stack
    stop        Stop the monitoring stack
    restart     Restart the monitoring stack
    status      Show service status and access URLs
    logs        Show logs (optional service name)
    test        Run tests
    example     Run example usage
    backup      Backup configuration and data
    help        Show this help message

Examples:
    $0 start
    $0 logs prometheus
    $0 status

For more information, see README.md
EOF
}

# Main script
main() {
    case "${1:-}" in
        start)
            check_prerequisites
            setup_environment
            install_python_deps
            create_directories
            start_stack
            show_status
            ;;
        stop)
            stop_stack
            ;;
        restart)
            restart_stack
            show_status
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs "$2"
            ;;
        test)
            run_tests
            ;;
        example)
            run_example
            ;;
        backup)
            backup_data
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: ${1:-}"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
