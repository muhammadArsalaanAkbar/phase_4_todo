#!/bin/bash
# Deploy script for AI Todo Chatbot on Minikube
# Constitution: Helm-Managed Deployments (Principle IV)

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="${NAMESPACE:-todo-dev}"
TIMEOUT="${TIMEOUT:-300s}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# =============================================================================
# Helper Functions
# =============================================================================

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

# =============================================================================
# Prerequisites Check
# =============================================================================

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check minikube
    if ! command -v minikube &> /dev/null; then
        log_error "minikube is not installed. Please install minikube 1.32+"
        exit 1
    fi

    # Check helm
    if ! command -v helm &> /dev/null; then
        log_error "helm is not installed. Please install Helm 3.x"
        exit 1
    fi

    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed. Please install kubectl"
        exit 1
    fi

    # Check minikube is running
    if ! minikube status &> /dev/null; then
        log_warn "minikube is not running. Starting minikube..."
        minikube start --cpus=4 --memory=8192 --driver=docker
    fi

    log_success "All prerequisites met"
}

# =============================================================================
# Docker Environment Setup
# =============================================================================

setup_docker_env() {
    log_info "Configuring Docker to use Minikube's daemon..."
    eval $(minikube docker-env)
    log_success "Docker environment configured"
}

# =============================================================================
# Build Images
# =============================================================================

build_images() {
    log_info "Building container images..."

    cd "${PROJECT_ROOT}"

    # Build frontend
    if [ -f "docker/frontend/Dockerfile" ]; then
        log_info "Building frontend image..."
        docker build -t todo-frontend:dev-latest -f docker/frontend/Dockerfile . || {
            log_warn "Frontend build failed - Dockerfile may need frontend source files"
        }
    fi

    # Build backend
    if [ -f "docker/backend/Dockerfile" ]; then
        log_info "Building backend image..."
        docker build -t todo-backend:dev-latest -f docker/backend/Dockerfile . || {
            log_warn "Backend build failed - Dockerfile may need backend source files"
        }
    fi

    log_success "Image build complete"
}

# =============================================================================
# Check Secrets
# =============================================================================

check_secrets() {
    log_info "Checking for required secrets..."

    if ! kubectl get secret todo-backend-secrets -n "${NAMESPACE}" &> /dev/null; then
        log_warn "Secret 'todo-backend-secrets' not found in namespace '${NAMESPACE}'"
        echo ""
        echo "Please create secrets before deployment:"
        echo "  ./scripts/create-secrets.sh"
        echo ""
        echo "Or create manually:"
        echo "  kubectl create secret generic todo-backend-secrets \\"
        echo "    --namespace ${NAMESPACE} \\"
        echo "    --from-literal=DATABASE_URL='your-connection-string' \\"
        echo "    --from-literal=OPENAI_API_KEY='your-api-key' \\"
        echo "    --from-literal=JWT_SECRET='your-jwt-secret'"
        echo ""
        read -p "Continue without secrets? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        log_success "Secrets found"
    fi
}

# =============================================================================
# Deploy Charts
# =============================================================================

deploy_infrastructure() {
    log_info "Deploying infrastructure chart..."

    helm upgrade --install todo-infrastructure \
        "${PROJECT_ROOT}/charts/todo-infrastructure" \
        --namespace "${NAMESPACE}" \
        --create-namespace \
        --wait \
        --timeout "${TIMEOUT}" \
        --atomic

    log_success "Infrastructure deployed"
}

deploy_backend() {
    log_info "Deploying backend chart..."

    helm upgrade --install todo-backend \
        "${PROJECT_ROOT}/charts/todo-backend" \
        --namespace "${NAMESPACE}" \
        --values "${PROJECT_ROOT}/charts/todo-backend/values-dev.yaml" \
        --wait \
        --timeout "${TIMEOUT}" \
        --atomic

    log_success "Backend deployed"
}

deploy_frontend() {
    log_info "Deploying frontend chart..."

    helm upgrade --install todo-frontend \
        "${PROJECT_ROOT}/charts/todo-frontend" \
        --namespace "${NAMESPACE}" \
        --values "${PROJECT_ROOT}/charts/todo-frontend/values-dev.yaml" \
        --wait \
        --timeout "${TIMEOUT}" \
        --atomic

    log_success "Frontend deployed"
}

# =============================================================================
# Verification
# =============================================================================

verify_deployment() {
    log_info "Verifying deployment..."

    echo ""
    echo "=== Pod Status ==="
    kubectl get pods -n "${NAMESPACE}"

    echo ""
    echo "=== Services ==="
    kubectl get svc -n "${NAMESPACE}"

    echo ""
    echo "=== Ingress ==="
    kubectl get ingress -n "${NAMESPACE}"

    log_success "Deployment verification complete"
}

print_access_info() {
    echo ""
    echo "=============================================="
    echo "  Deployment Complete!"
    echo "=============================================="
    echo ""
    echo "Access the application:"
    echo ""
    echo "  Option 1: Minikube tunnel (recommended)"
    echo "    minikube tunnel"
    echo "    Then access: http://todo.local"
    echo ""
    echo "  Option 2: NodePort"
    echo "    minikube service todo-frontend-svc -n ${NAMESPACE} --url"
    echo ""
    echo "  Add to /etc/hosts if needed:"
    echo "    echo \"\$(minikube ip) todo.local\" | sudo tee -a /etc/hosts"
    echo ""
}

# =============================================================================
# Main
# =============================================================================

main() {
    echo ""
    echo "=============================================="
    echo "  AI Todo Chatbot - Kubernetes Deployment"
    echo "=============================================="
    echo ""

    check_prerequisites
    setup_docker_env
    # build_images  # Uncomment when frontend/backend source exists
    deploy_infrastructure
    check_secrets
    deploy_backend
    deploy_frontend
    verify_deployment
    print_access_info
}

main "$@"
