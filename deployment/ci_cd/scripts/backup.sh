#!/bin/bash
# SuperInstance Research Platform - Backup Script
# Backup databases and configurations

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Configuration
CLUSTER_NAME="superinstance-production"
AWS_REGION="us-east-1"
NAMESPACE="superinstance"
BACKUP_BUCKET="s3://superinstance-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

backup_postgres() {
    log_info "Backing up PostgreSQL database..."
    
    # Get postgres pod
    POSTGRES_POD=$(kubectl get pod -n ${NAMESPACE} -l app=postgres -o jsonpath='{.items[0].metadata.name}')
    
    # Create backup
    kubectl exec -n ${NAMESPACE} ${POSTGRES_POD} -- pg_dumpall -U superinstance | \
        aws s3 cp - ${BACKUP_BUCKET}/postgres/${TIMESTAMP}.sql
    
    log_info "PostgreSQL backup completed: ${BACKUP_BUCKET}/postgres/${TIMESTAMP}.sql"
}

backup_redis() {
    log_info "Backing up Redis data..."
    
    # Get redis pod
    REDIS_POD=$(kubectl get pod -n ${NAMESPACE} -l app=redis -o jsonpath='{.items[0].metadata.name}')
    
    # Create backup
    kubectl exec -n ${NAMESPACE} ${REDIS_POD} -- redis-cli SAVE
    kubectl cp ${NAMESPACE}/${REDIS_POD}:/data/dump.rdb /tmp/redis_${TIMESTAMP}.rdb
    aws s3 cp /tmp/redis_${TIMESTAMP}.rdb ${BACKUP_BUCKET}/redis/${TIMESTAMP}.rdb
    rm /tmp/redis_${TIMESTAMP}.rdb
    
    log_info "Redis backup completed: ${BACKUP_BUCKET}/redis/${TIMESTAMP}.rdb"
}

backup_kubernetes_configs() {
    log_info "Backing up Kubernetes configurations..."
    
    # Backup all resources
    kubectl get all -n ${NAMESPACE} -o yaml > /tmp/k8s_configs_${TIMESTAMP}.yaml
    aws s3 cp /tmp/k8s_configs_${TIMESTAMP}.yaml ${BACKUP_BUCKET}/kubernetes/${TIMESTAMP}.yaml
    rm /tmp/k8s_configs_${TIMESTAMP}.yaml
    
    log_info "Kubernetes configs backup completed: ${BACKUP_BUCKET}/kubernetes/${TIMESTAMP}.yaml"
}

main() {
    log_info "Starting backup process..."
    backup_postgres
    backup_redis
    backup_kubernetes_configs
    log_info "Backup completed successfully!"
}

main
