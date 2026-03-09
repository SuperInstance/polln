#!/bin/bash
# Security scanning script for POLLN containers
# Uses Trivy for vulnerability scanning

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
IMAGE_NAME="${IMAGE_NAME:-polln:latest}"
REPORT_DIR="${PROJECT_ROOT}/reports/security"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=== POLLN Security Scan ==="
echo "Image: ${IMAGE_NAME}"
echo "Report directory: ${REPORT_DIR}"
echo

# Create report directory
mkdir -p "${REPORT_DIR}"

# Check if Trivy is installed
if ! command -v trivy &> /dev/null; then
    echo -e "${YELLOW}Trivy not found. Installing...${NC}"
    brew install trivy 2>/dev/null || {
        echo "Please install Trivy manually:"
        echo "  brew install trivy  # macOS"
        echo "  or visit https://aquasecurity.github.io/trivy/"
        exit 1
    }
fi

# Scan image for vulnerabilities
echo "Scanning image for vulnerabilities..."
trivy image \
    --severity HIGH,CRITICAL \
    --format json \
    --output "${REPORT_DIR}/vulnerabilities.json" \
    "${IMAGE_NAME}"

# Generate human-readable report
trivy image \
    --severity HIGH,CRITICAL \
    --format table \
    --output "${REPORT_DIR}/vulnerabilities.txt" \
    "${IMAGE_NAME}"

# Generate HTML report
trivy image \
    --severity HIGH,CRITICAL \
    --format template \
    --template "@contrib/html.tpl" \
    --output "${REPORT_DIR}/vulnerabilities.html" \
    "${IMAGE_NAME}" || true

# Check if critical vulnerabilities were found
CRITICAL_COUNT=$(jq -r '[.Results[]? | .Vulnerabilities[]? | select(.Severity=="CRITICAL")] | length' "${REPORT_DIR}/vulnerabilities.json" 2>/dev/null || echo "0")
HIGH_COUNT=$(jq -r '[.Results[]? | .Vulnerabilities[]? | select(.Severity=="HIGH")] | length' "${REPORT_DIR}/vulnerabilities.json" 2>/dev/null || echo "0")

echo
echo "=== Scan Results ==="
echo "Critical vulnerabilities: ${CRITICAL_COUNT}"
echo "High vulnerabilities: ${HIGH_COUNT}"

if [ "${CRITICAL_COUNT}" -gt 0 ]; then
    echo -e "${RED}❌ Critical vulnerabilities found!${NC}"
    echo "Please review the report at: ${REPORT_DIR}/vulnerabilities.html"
    exit 1
elif [ "${HIGH_COUNT}" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  High vulnerabilities found. Review recommended.${NC}"
    echo "Report available at: ${REPORT_DIR}/vulnerabilities.html"
    exit 0
else
    echo -e "${GREEN}✅ No critical or high vulnerabilities found!${NC}"
    exit 0
fi
