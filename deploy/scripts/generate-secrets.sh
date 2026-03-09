#!/bin/bash
# Generate secrets for POLLN deployment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
NAMESPACE="${NAMESPACE:-polln}"
RELEASE_NAME="${RELEASE_NAME:-polln}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=== POLLN Secret Generation ==="
echo "Namespace: ${NAMESPACE}"
echo "Release: ${RELEASE_NAME}"
echo

# Generate JWT secret
JWT_SECRET=$(openssl rand -base64 32)
echo -e "${GREEN}✓ Generated JWT secret${NC}"

# Generate database password
DB_PASSWORD=$(openssl rand -base64 16)
echo -e "${GREEN}✓ Generated database password${NC}"

# Generate Redis password
REDIS_PASSWORD=$(openssl rand -base64 16)
echo -e "${GREEN}✓ Generated Redis password${NC}"

# Create secret
echo
echo "Creating Kubernetes secret..."
kubectl create secret generic "${RELEASE_NAME}-secret" \
    --from-literal=jwt-secret="${JWT_SECRET}" \
    --from-literal=database-url="postgresql://polln:${DB_PASSWORD}@${RELEASE_NAME}-postgresql:5432/polln" \
    --from-literal=redis-password="${REDIS_PASSWORD}" \
    --namespace="${NAMESPACE}" \
    --dry-run=client -o yaml | kubectl apply -f -

echo -e "${GREEN}✓ Secret created successfully${NC}"

# Save secrets to file (for backup)
SECRET_FILE="${PROJECT_ROOT}/secrets/${NAMESPACE}-${RELEASE_NAME}-secrets.txt"
mkdir -p "$(dirname "${SECRET_FILE}")"
cat > "${SECRET_FILE}" <<EOF
# POLLN Secrets for ${NAMESPACE}/${RELEASE_NAME}
# Generated: $(date)

JWT Secret: ${JWT_SECRET}
Database URL: postgresql://polln:${DB_PASSWORD}@${RELEASE_NAME}-postgresql:5432/polln
Database Password: ${DB_PASSWORD}
Redis Password: ${REDIS_PASSWORD}

# Keep this file secure and DO NOT commit to version control!
EOF

echo -e "${YELLOW}⚠️  Secrets backed up to: ${SECRET_FILE}${NC}"
echo -e "${YELLOW}⚠️  Keep this file secure and DO NOT commit to version control!${NC}"

echo
echo "=== Secret Generation Complete ==="
