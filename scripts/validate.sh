#!/bin/bash
# Pre-deployment validation script
# Constitution: Fail-Fast Validation (Principle VIII)

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

ERRORS=0

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
    ERRORS=$((ERRORS + 1))
}

echo ""
echo "=============================================="
echo "  Pre-Deployment Validation"
echo "=============================================="
echo ""

# =============================================================================
# Helm Lint
# =============================================================================

log_info "Running helm lint on all charts..."

for chart in todo-infrastructure todo-frontend todo-backend; do
    if helm lint "${PROJECT_ROOT}/charts/${chart}" &> /dev/null; then
        log_success "charts/${chart} passed lint"
    else
        log_error "charts/${chart} failed lint"
        helm lint "${PROJECT_ROOT}/charts/${chart}"
    fi
done

# =============================================================================
# Helm Template Validation
# =============================================================================

log_info "Validating helm templates..."

for chart in todo-infrastructure todo-frontend todo-backend; do
    if helm template "${PROJECT_ROOT}/charts/${chart}" &> /dev/null; then
        log_success "charts/${chart} templates render correctly"
    else
        log_error "charts/${chart} template rendering failed"
    fi
done

# =============================================================================
# Required Files Check
# =============================================================================

log_info "Checking required files..."

required_files=(
    "charts/todo-infrastructure/Chart.yaml"
    "charts/todo-frontend/Chart.yaml"
    "charts/todo-backend/Chart.yaml"
    "docker/frontend/Dockerfile"
    "docker/backend/Dockerfile"
    "env.example.frontend"
    "env.example.backend"
)

for file in "${required_files[@]}"; do
    if [ -f "${PROJECT_ROOT}/${file}" ]; then
        log_success "${file} exists"
    else
        log_error "${file} is missing"
    fi
done

# =============================================================================
# Summary
# =============================================================================

echo ""
echo "=============================================="

if [ $ERRORS -eq 0 ]; then
    log_success "All validations passed!"
    echo ""
    echo "Ready to deploy: ./scripts/deploy.sh"
    exit 0
else
    log_error "Validation failed with ${ERRORS} error(s)"
    exit 1
fi
