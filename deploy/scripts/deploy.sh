#!/bin/bash
# POLLN deployment script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HELM_CHART="${PROJECT_ROOT}/deploy/helm/polln"
NAMESPACE="${NAMESPACE:-polln}"
RELEASE_NAME="${RELEASE_NAME:-polln}"
VALUES_FILE="${VALUES_FILE:-${HELM_CHART}/values.prod.yaml}"
ACTION="${1:-install}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=== POLLN Deployment Script ==="
echo "Action: ${ACTION}"
echo "Namespace: ${NAMESPACE}"
echo "Release: ${RELEASE_NAME}"
echo "Values file: ${VALUES_FILE}"
echo

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl not found. Please install kubectl.${NC}"
    exit 1
fi

# Check if helm is available
if ! command -v helm &> /dev/null; then
    echo -e "${RED}❌ helm not found. Please install helm.${NC}"
    exit 1
fi

# Create namespace if it doesn't exist
echo "Creating namespace..."
kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -
echo -e "${GREEN}✓ Namespace ready${NC}"
echo

# Check if secrets exist
echo "Checking secrets..."
if ! kubectl get secret "${RELEASE_NAME}-secret" -n "${NAMESPACE}" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Secrets not found. Generating...${NC}"
    bash "${SCRIPT_DIR}/generate-secrets.sh"
fi
echo -e "${GREEN}✓ Secrets ready${NC}"
echo

# Update Helm dependencies
echo "Updating Helm dependencies..."
helm dependency update "${HELM_CHART}"
echo -e "${GREEN}✓ Dependencies updated${NC}"
echo

# Deploy using Helm
echo "Deploying POLLN..."
case "${ACTION}" in
    install)
        helm install "${RELEASE_NAME}" "${HELM_CHART}" \
            --namespace "${NAMESPACE}" \
            --values "${VALUES_FILE}" \
            --wait \
            --timeout 5m
        ;;
    upgrade)
        helm upgrade "${RELEASE_NAME}" "${HELM_CHART}" \
            --namespace "${NAMESPACE}" \
            --values "${VALUES_FILE}" \
            --wait \
            --timeout 5m
        ;;
    uninstall)
        helm uninstall "${RELEASE_NAME}" --namespace "${NAMESPACE}"
        echo -e "${GREEN}✓ POLLN uninstalled${NC}"
        exit 0
        ;;
    status)
        helm status "${RELEASE_NAME}" --namespace "${NAMESPACE}"
        exit 0
        ;;
    *)
        echo -e "${RED}Unknown action: ${ACTION}${NC}"
        echo "Usage: $0 {install|upgrade|uninstall|status}"
        exit 1
        ;;
esac

echo -e "${GREEN}✓ POLLN deployed successfully${NC}"
echo

# Wait for deployment to be ready
echo "Waiting for deployment to be ready..."
kubectl rollout status deployment/"${RELEASE_NAME}" -n "${NAMESPACE}" --timeout=5m
echo -e "${GREEN}✓ Deployment ready${NC}"
echo

# Show status
echo "=== Deployment Status ==="
kubectl get pods -n "${NAMESPACE}" -l "app.kubernetes.io/name=polln"
echo

echo "=== Services ==="
kubectl get svc -n "${NAMESPACE}" -l "app.kubernetes.io/name=polln"
echo

echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo "View logs: kubectl logs -f deployment/${RELEASE_NAME} -n ${NAMESPACE}"
echo "Port forward: kubectl port-forward deployment/${RELEASE_NAME} 3000:3000 -n ${NAMESPACE}"
