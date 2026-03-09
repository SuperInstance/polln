#!/bin/bash
# Test POLLN health endpoints

set -e

NAMESPACE="${NAMESPACE:-polln}"
RELEASE_NAME="${RELEASE_NAME:-polln}"
TIMEOUT="${TIMEOUT:-300}"

echo "=== POLLN Health Endpoint Tests ==="
echo "Namespace: ${NAMESPACE}"
echo "Release: ${RELEASE_NAME}"
echo

# Port forward
echo "Setting up port forward..."
kubectl port-forward deployment/"${RELEASE_NAME}" 3000:3000 -n "${NAMESPACE}" &
PF_PID=$!
trap "kill ${PF_PID} 2>/dev/null || true" EXIT

# Wait for port forward to be ready
echo "Waiting for connection..."
START_TIME=$(date +%s)
while true; do
    if curl -s http://localhost:3000/health > /dev/null 2>&1; then
        echo "✓ Connection established"
        break
    fi

    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    if [ ${ELAPSED} -gt ${TIMEOUT} ]; then
        echo "✗ Timeout waiting for connection"
        exit 1
    fi
    sleep 2
done
echo

# Test health endpoint
echo "Testing /health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:3000/health)
echo "Response: ${HEALTH_RESPONSE}"
HEALTH_STATUS=$(echo "${HEALTH_RESPONSE}" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
if [ "${HEALTH_STATUS}" == "ok" ]; then
    echo "✓ Health check passed"
else
    echo "✗ Health check failed"
    exit 1
fi
echo

# Test readiness endpoint
echo "Testing /ready endpoint..."
READY_RESPONSE=$(curl -s http://localhost:3000/ready)
echo "Response: ${READY_RESPONSE}"
READY_STATUS=$(echo "${READY_RESPONSE}" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
if [ "${READY_STATUS}" == "ready" ]; then
    echo "✓ Readiness check passed"
else
    echo "✗ Readiness check failed"
    exit 1
fi
echo

# Test metrics endpoint
echo "Testing /metrics endpoint..."
METRICS_RESPONSE=$(curl -s http://localhost:3000/metrics)
if echo "${METRICS_RESPONSE}" | grep -q "polln_api_uptime_seconds"; then
    echo "✓ Metrics endpoint working"
    echo "Sample metrics:"
    echo "${METRICS_RESPONSE}" | head -20
else
    echo "✗ Metrics endpoint failed"
    exit 1
fi
echo

echo "=== All Health Tests Passed ==="
