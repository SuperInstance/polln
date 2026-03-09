#!/bin/bash
# Restore POLLN data from backup

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
NAMESPACE="${NAMESPACE:-polln}"
RELEASE_NAME="${RELEASE_NAME:-polln}"
BACKUP_FILE="${1}"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ -z "${BACKUP_FILE}" ]; then
    echo -e "${RED}Usage: $0 <backup-file>${NC}"
    echo "Example: $0 backups/polln-backup-20240308_120000.tar.gz"
    exit 1
fi

if [ ! -f "${BACKUP_FILE}" ]; then
    echo -e "${RED}Backup file not found: ${BACKUP_FILE}${NC}"
    exit 1
fi

echo "=== POLLN Restore ==="
echo "Namespace: ${NAMESPACE}"
echo "Release: ${RELEASE_NAME}"
echo "Backup file: ${BACKUP_FILE}"
echo

# Warning
echo -e "${YELLOW}⚠️  WARNING: This will replace existing data!${NC}"
read -p "Are you sure? (yes/no): " confirm
if [ "${confirm}" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

# Scale down deployment
echo "Scaling down deployment..."
kubectl scale deployment/"${RELEASE_NAME}" -n "${NAMESPACE}" --replicas=0
kubectl rollout status deployment/"${RELEASE_NAME}" -n "${NAMESPACE}" --timeout=2m

# Create restore pod
echo "Creating restore pod..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
kubectl run "polln-restore-${TIMESTAMP}" \
    --namespace="${NAMESPACE}" \
    --image="alpine:3.18" \
    --restart=Never \
    -v "${RELEASE_NAME}-data:/data" \
    -v "${RELEASE_NAME}-agents:/agents" \
    --command -- sleep 3600 > /dev/null 2>&1 || true

echo "Waiting for pod to be ready..."
kubectl wait --for=condition=ready pod "polln-restore-${TIMESTAMP}" -n "${NAMESPACE}" --timeout=60s

# Extract backup to restore pod
echo "Restoring data..."
cat "${BACKUP_FILE}" | kubectl exec -i "polln-restore-${TIMESTAMP}" -n "${NAMESPACE}" -- tar xzf - -C /

# Copy data to persistent volumes
kubectl exec "polln-restore-${TIMESTAMP}" -n "${NAMESPACE}" -- sh -c "
    cp -r /backup/app/.polln/* /data/ 2>/dev/null || true
    cp -r /backup/app/.agents/* /agents/ 2>/dev/null || true
"

# Cleanup restore pod
echo "Cleaning up..."
kubectl delete pod "polln-restore-${TIMESTAMP}" -n "${NAMESPACE}" --wait=false

# Scale up deployment
echo "Scaling up deployment..."
kubectl scale deployment/"${RELEASE_NAME}" -n "${NAMESPACE}" --replicas=3
kubectl rollout status deployment/"${RELEASE_NAME}" -n "${NAMESPACE}" --timeout=5m

echo -e "${GREEN}✓ Restore complete${NC}"
echo
echo "Verify restore:"
echo "  kubectl get pods -n ${NAMESPACE}"
echo "  kubectl logs -f deployment/${RELEASE_NAME} -n ${NAMESPACE}"
