#!/bin/bash
# Backup POLLN data

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
NAMESPACE="${NAMESPACE:-polln}"
RELEASE_NAME="${RELEASE_NAME:-polln}"
BACKUP_DIR="${PROJECT_ROOT}/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/polln-backup-${TIMESTAMP}.tar.gz"

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m'

echo "=== POLLN Backup ==="
echo "Namespace: ${NAMESPACE}"
echo "Release: ${RELEASE_NAME}"
echo "Backup file: ${BACKUP_FILE}"
echo

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Create a pod to perform the backup
echo "Creating backup pod..."
kubectl run "polln-backup-${TIMESTAMP}" \
    --namespace="${NAMESPACE}" \
    --image="alpine:3.18" \
    --restart=Never \
    --command -- sleep 3600 > /dev/null 2>&1 || true

echo "Waiting for pod to be ready..."
kubectl wait --for=condition=ready pod "polln-backup-${TIMESTAMP}" -n "${NAMESPACE}" --timeout=60s

# Copy data from persistent volumes
echo "Copying data from persistent volumes..."
kubectl exec "polln-backup-${TIMESTAMP}" -n "${NAMESPACE}" -- mkdir -p /backup

# Copy data from polln-data PVC
DATA_POD=$(kubectl get pod -n "${NAMESPACE}" -l "app.kubernetes.io/name=polln" -o jsonpath='{.items[0].metadata.name}')
if [ -n "${DATA_POD}" ]; then
    echo "Copying .polln data..."
    kubectl exec "${DATA_POD}" -n "${NAMESPACE}" -- tar czf - /app/.polln | \
        kubectl exec -i "polln-backup-${TIMESTAMP}" -n "${NAMESPACE}" -- tar xzf - -C /backup

    echo "Copying .agents data..."
    kubectl exec "${DATA_POD}" -n "${NAMESPACE}" -- tar czf - /app/.agents | \
        kubectl exec -i "polln-backup-${TIMESTAMP}" -n "${NAMESPACE}" -- tar xzf - -C /backup
fi

# Copy backup from pod to local
echo "Downloading backup..."
kubectl exec "polln-backup-${TIMESTAMP}" -n "${NAMESPACE}" -- tar czf - /backup | \
    cat > "${BACKUP_FILE}"

# Cleanup backup pod
echo "Cleaning up..."
kubectl delete pod "polln-backup-${TIMESTAMP}" -n "${NAMESPACE}" --wait=false

echo -e "${GREEN}✓ Backup complete: ${BACKUP_FILE}${NC}"

# Show backup size
BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
echo "Backup size: ${BACKUP_SIZE}"
