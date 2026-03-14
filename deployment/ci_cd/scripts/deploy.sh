#!/bin/bash
# SuperInstance Research Platform - Deployment Script
# One-command production deployment

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REGISTRY="ghcr.io/superinstance"
CLUSTER_NAME="superinstance-production"
AWS_REGION="us-east-1"
NAMESPACE="superinstance"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed"
        exit 1
    fi
    
    # Check if aws cli is installed
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed"
        exit 1
    fi
    
    # Check if logged into container registry
    if ! docker info | grep -q "Username"; then
        log_warn "Not logged into container registry"
        log_info "Please run: docker login ghcr.io"
        exit 1
    fi
    
    log_info "Prerequisites check passed"
}

build_images() {
    log_info "Building Docker images..."
    
    # Build API image
    log_info "Building API image..."
    docker build -t ${REGISTRY}/api:latest -f deployment/docker/Dockerfile.api .
    docker tag ${REGISTRY}/api:latest ${REGISTRY}/api:${IMAGE_TAG:-latest}
    
    # Build Worker image
    log_info "Building Worker image..."
    docker build -t ${REGISTRY}/worker:latest -f deployment/docker/Dockerfile.worker .
    docker tag ${REGISTRY}/worker:latest ${REGISTRY}/worker:${IMAGE_TAG:-latest}
    
    # Build Web image
    log_info "Building Web image..."
    docker build -t ${REGISTRY}/web:latest -f deployment/docker/Dockerfile.web .
    docker tag ${REGISTRY}/web:latest ${REGISTRY}/web:${IMAGE_TAG:-latest}
    
    log_info "Docker images built successfully"
}

push_images() {
    log_info "Pushing Docker images..."
    
    docker push ${REGISTRY}/api:latest
    docker push ${REGISTRY}/api:${IMAGE_TAG:-latest}
    docker push ${REGISTRY}/worker:latest
    docker push ${REGISTRY}/worker:${IMAGE_TAG:-latest}
    docker push ${REGISTRY}/web:latest
    docker push ${REGISTRY}/web:${IMAGE_TAG:-latest}
    
    log_info "Docker images pushed successfully"
}

deploy_kubernetes() {
    log_info "Deploying to Kubernetes..."
    
    # Update kubeconfig
    log_info "Updating kubeconfig..."
    aws eks update-kubeconfig --name ${CLUSTER_NAME} --region ${AWS_REGION}
    
    # Create namespace
    log_info "Creating namespace..."
    kubectl apply -f deployment/kubernetes/namespace.yaml
    
    # Apply configurations
    log_info "Apply configurations..."
    kubectl apply -f deployment/kubernetes/configmap.yaml
    kubectl apply -f deployment/kubernetes/secrets.yaml
    kubectl apply -f deployment/kubernetes/pvc.yaml
    
    # Deploy databases
    log_info "Deploying databases..."
    kubectl apply -f deployment/kubernetes/postgres-deployment.yaml
    
    # Wait for databases
    log_info "Waiting for databases to be ready..."
    kubectl wait --for=condition=ready pod -l app=postgres -n ${NAMESPACE} --timeout=300s
    
    # Deploy applications
    log_info "Deploying applications..."
    kubectl apply -f deployment/kubernetes/api-deployment.yaml
    kubectl apply -f deployment/kubernetes/worker-deployment.yaml
    kubectl apply -f deployment/kubernetes/web-deployment.yaml
    
    # Deploy monitoring
    log_info "Deploying monitoring..."
    kubectl apply -f deployment/kubernetes/monitoring.yaml
    
    # Deploy ingress
    log_info "Deploying ingress..."
    kubectl apply -f deployment/kubernetes/ingress.yaml
    
    log_info "Kubernetes deployment completed"
}

verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check pods
    log_info "Checking pod status..."
    kubectl get pods -n ${NAMESPACE}
    
    # Check services
    log_info "Checking services..."
    kubectl get services -n ${NAMESPACE}
    
    # Check ingress
    log_info "Checking ingress..."
    kubectl get ingress -n ${NAMESPACE}
    
    # Wait for rollout
    log_info "Waiting for rollout to complete..."
    kubectl rollout status deployment/superinstance-api -n ${NAMESPACE} --timeout=300s
    kubectl rollout status deployment/superinstance-web -n ${NAMESPACE} --timeout=300s
    
    # Run health check
    log_info "Running health check..."
    kubectl run health-check --image=curlimages/curl:latest --rm -i --restart=Never -n ${NAMESPACE} -- \
        curl -f http://superinstance-api.${NAMESPACE}.svc.cluster.local:8000/health
    
    log_info "Deployment verification completed"
}

main() {
    log_info "Starting SuperInstance Platform deployment..."
    
    check_prerequisites
    build_images
    push_images
    deploy_kubernetes
    verify_deployment
    
    log_info "Deployment completed successfully!"
    log_info "Access the application at: https://superinstance.ai"
    log_info "Access monitoring at: https://monitoring.superinstance.ai"
}

# Run main function
main "$@"
