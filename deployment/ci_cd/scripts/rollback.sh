#!/bin/bash
# SuperInstance Research Platform - Rollback Script
# Quick rollback to previous deployment

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
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

rollback_deployment() {
    log_info "Starting rollback..."
    
    # Update kubeconfig
    log_info "Updating kubeconfig..."
    aws eks update-kubeconfig --name ${CLUSTER_NAME} --region ${AWS_REGION}
    
    # Rollback API deployment
    log_info "Rolling back API deployment..."
    kubectl rollout undo deployment/superinstance-api -n ${NAMESPACE}
    
    # Rollback Web deployment
    log_info "Rolling back Web deployment..."
    kubectl rollout undo deployment/superinstance-web -n ${NAMESPACE}
    
    # Wait for rollback
    log_info "Waiting for rollback to complete..."
    kubectl rollout status deployment/superinstance-api -n ${NAMESPACE} --timeout=300s
    kubectl rollout status deployment/superinstance-web -n ${NAMESPACE} --timeout=300s
    
    # Verify rollback
    log_info "Verifying rollback..."
    kubectl get pods -n ${NAMESPACE}
    
    log_info "Rollback completed successfully!"
}

# Run rollback
rollback_deployment
