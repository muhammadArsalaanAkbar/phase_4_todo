#!/bin/bash
# Secret creation script for AI Todo Chatbot
# Constitution: Secrets Governance (Principle III)

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="${NAMESPACE:-todo-dev}"
SECRET_NAME="todo-backend-secrets"

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo ""
echo "=============================================="
echo "  Secret Creation for AI Todo Chatbot"
echo "=============================================="
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    log_error "kubectl is not installed"
    exit 1
fi

# Check if namespace exists
if ! kubectl get namespace "${NAMESPACE}" &> /dev/null; then
    log_info "Creating namespace ${NAMESPACE}..."
    kubectl create namespace "${NAMESPACE}"
fi

# Check if secret already exists
if kubectl get secret "${SECRET_NAME}" -n "${NAMESPACE}" &> /dev/null; then
    log_warn "Secret '${SECRET_NAME}' already exists in namespace '${NAMESPACE}'"
    read -p "Do you want to replace it? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl delete secret "${SECRET_NAME}" -n "${NAMESPACE}"
    else
        log_info "Keeping existing secret"
        exit 0
    fi
fi

# Prompt for secret values
echo ""
log_info "Please provide the following secret values:"
echo ""

read -p "DATABASE_URL (Neon PostgreSQL connection string): " DATABASE_URL
if [ -z "${DATABASE_URL}" ]; then
    log_error "DATABASE_URL is required"
    exit 1
fi

read -p "OPENAI_API_KEY: " OPENAI_API_KEY
if [ -z "${OPENAI_API_KEY}" ]; then
    log_error "OPENAI_API_KEY is required"
    exit 1
fi

read -p "JWT_SECRET (min 32 characters): " JWT_SECRET
if [ ${#JWT_SECRET} -lt 32 ]; then
    log_error "JWT_SECRET must be at least 32 characters"
    exit 1
fi

# Create the secret
log_info "Creating secret '${SECRET_NAME}' in namespace '${NAMESPACE}'..."

kubectl create secret generic "${SECRET_NAME}" \
    --namespace "${NAMESPACE}" \
    --from-literal=DATABASE_URL="${DATABASE_URL}" \
    --from-literal=OPENAI_API_KEY="${OPENAI_API_KEY}" \
    --from-literal=JWT_SECRET="${JWT_SECRET}"

log_success "Secret created successfully"

# Verify
echo ""
log_info "Verifying secret..."
kubectl get secret "${SECRET_NAME}" -n "${NAMESPACE}"

echo ""
log_success "Secret setup complete. You can now run ./scripts/deploy.sh"
