#!/bin/bash
# Verify POLLN deployment

set -e

NAMESPACE="${NAMESPACE:-polln}"
RELEASE_NAME="${RELEASE_NAME:-polln}"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

FAILURES=0

echo "=== POLLN Deployment Verification ==="
echo "Namespace: ${NAMESPACE}"
echo "Release: ${RELEASE_NAME}"
echo

# Function to check resource
check_resource() {
    local resource_type=$1
    local resource_name=$2
    local namespace=$3

    if kubectl get "${resource_type}" "${resource_name}" -n "${namespace}" &> /dev/null; then
        echo -e "${GREEN}✓${NC} ${resource_type}/${resource_name}"
        return 0
    else
        echo -e "${RED}✗${NC} ${resource_type}/${resource_name}"
        ((FAILURES++))
        return 1
    fi
}

# Function to check pod status
check_pod() {
    local pod_name=$1
    local namespace=$2

    local phase=$(kubectl get pod "${pod_name}" -n "${namespace}" -o jsonpath='{.status.phase}')
    local ready=$(kubectl get pod "${pod_name}" -n "${namespace}" -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}')

    if [ "${phase}" == "Running" ] && [ "${ready}" == "True" ]; then
        echo -e "${GREEN}✓${NC} Pod ${pod_name} is running and ready"
        return 0
    else
        echo -e "${RED}✗${NC} Pod ${pod_name} - Phase: ${phase}, Ready: ${ready}"
        ((FAILURES++))
        return 1
    fi
}

# Function to check endpoint
check_endpoint() {
    local endpoint=$1
    local description=$2

    local status_code=$(curl -s -o /dev/null -w "%{http_code}" "${endpoint}" || echo "000")

    if [ "${status_code}" == "200" ]; then
        echo -e "${GREEN}✓${NC} ${description} (${endpoint})"
        return 0
    else
        echo -e "${RED}✗${NC} ${description} (${endpoint}) - Status: ${status_code}"
        ((FAILURES++))
        return 1
    fi
}

echo "=== Checking Resources ==="
check_resource "deployment" "${RELEASE_NAME}" "${NAMESPACE}"
check_resource "service" "${RELEASE_NAME}" "${NAMESPACE}"
check_resource "configmap" "${RELEASE_NAME}-config" "${NAMESPACE}"
check_resource "secret" "${RELEASE_NAME}-secret" "${NAMESPACE}"
if kubectl get hpa "${RELEASE_NAME}" -n "${NAMESPACE}" &> /dev/null; then
    check_resource "hpa" "${RELEASE_NAME}" "${NAMESPACE}"
fi
echo

echo "=== Checking Pods ==="
PODS=$(kubectl get pods -n "${NAMESPACE}" -l "app.kubernetes.io/name=polln" -o jsonpath='{.items[*].metadata.name}')
for pod in ${PODS}; do
    check_pod "${pod}" "${NAMESPACE}"
done
echo

echo "=== Checking Endpoints ==="
# Port forward to check endpoints
kubectl port-forward deployment/"${RELEASE_NAME}" 3000:3000 -n "${NAMESPACE}" &
PF_PID=$!
sleep 5

check_endpoint "http://localhost:3000/health" "Health check"
check_endpoint "http://localhost:3000/ready" "Readiness check"
check_endpoint "http://localhost:3000/metrics" "Metrics endpoint"

# Cleanup port forward
kill ${PF_PID} 2>/dev/null || true
echo

echo "=== Checking Resource Limits ==="
POD=$(kubectl get pod -n "${NAMESPACE}" -l "app.kubernetes.io/name=polln" -o jsonpath='{.items[0].metadata.name}')
if [ -n "${POD}" ]; then
    CPU_LIMIT=$(kubectl get pod "${POD}" -n "${NAMESPACE}" -o jsonpath='{.spec.containers[0].resources.limits.cpu}')
    MEMORY_LIMIT=$(kubectl get pod "${POD}" -n "${NAMESPACE}" -o jsonpath='{.spec.containers[0].resources.limits.memory}')
    CPU_REQUEST=$(kubectl get pod "${POD}" -n "${NAMESPACE}" -o jsonpath='{.spec.containers[0].resources.requests.cpu}')
    MEMORY_REQUEST=$(kubectl get pod "${POD}" -n "${NAMESPACE}" -o jsonpath='{.spec.containers[0].resources.requests.memory}')

    echo "CPU Request: ${CPU_REQUEST}, Limit: ${CPU_LIMIT}"
    echo "Memory Request: ${MEMORY_REQUEST}, Limit: ${MEMORY_LIMIT}"

    if [ -n "${CPU_LIMIT}" ] && [ -n "${MEMORY_LIMIT}" ]; then
        echo -e "${GREEN}✓${NC} Resource limits configured"
    else
        echo -e "${YELLOW}⚠${NC} Resource limits not configured"
        ((FAILURES++))
    fi
fi
echo

echo "=== Checking Persistent Volumes ==="
PVC_DATA="${RELEASE_NAME}-data"
PVC_AGENTS="${RELEASE_NAME}-agents"
check_resource "pvc" "${PVC_DATA}" "${NAMESPACE}"
check_resource "pvc" "${PVC_AGENTS}" "${NAMESPACE}"
echo

echo "=== Checking Security ==="
# Check if running as non-root
SECURITY_CONTEXT=$(kubectl get pod -n "${NAMESPACE}" -l "app.kubernetes.io/name=polln" -o jsonpath='{.items[0].spec.securityContext}')
if echo "${SECURITY_CONTEXT}" | grep -q "runAsNonRoot.*true"; then
    echo -e "${GREEN}✓${NC} Running as non-root"
else
    echo -e "${YELLOW}⚠${NC} Not configured to run as non-root"
    ((FAILURES++))
fi

# Check for read-only root filesystem
READ_ONLY=$(kubectl get pod -n "${NAMESPACE}" -l "app.kubernetes.io/name=polln" -o jsonpath='{.items[0].spec.containers[0].securityContext.readOnlyRootFilesystem}')
if [ "${READ_ONLY}" == "true" ]; then
    echo -e "${GREEN}✓${NC} Read-only root filesystem"
else
    echo -e "${YELLOW}⚠${NC} Root filesystem is not read-only"
fi
echo

echo "=== Summary ==="
if [ ${FAILURES} -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ ${FAILURES} check(s) failed${NC}"
    exit 1
fi
