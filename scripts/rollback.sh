#!/bin/bash
# Rollback script for AI Todo Chatbot
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
RELEASE="${1:-}"

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

show_usage() {
    echo ""
    echo "Usage: $0 <release-name> [revision]"
    echo ""
    echo "Arguments:"
    echo "  release-name   Name of the Helm release (todo-frontend, todo-backend)"
    echo "  revision       Optional revision number to rollback to"
    echo ""
    echo "Examples:"
    echo "  $0 todo-backend           # Rollback to previous revision"
    echo "  $0 todo-backend 2         # Rollback to specific revision"
    echo ""
    echo "Available releases:"
    helm list -n "${NAMESPACE}" --short 2>/dev/null || echo "  (none found in ${NAMESPACE})"
    echo ""
}

show_history() {
    local release=$1
    echo ""
    echo "=== Release History: ${release} ==="
    helm history "${release}" -n "${NAMESPACE}" 2>/dev/null || {
        log_error "Release '${release}' not found in namespace '${NAMESPACE}'"
        exit 1
    }
    echo ""
}

rollback_release() {
    local release=$1
    local revision="${2:-}"

    # Show history
    show_history "${release}"

    # Get current revision
    local current_rev
    current_rev=$(helm list -n "${NAMESPACE}" -f "^${release}$" -o json | jq -r '.[0].revision')

    if [ -z "${revision}" ]; then
        # Calculate previous revision
        revision=$((current_rev - 1))
        if [ "${revision}" -lt 1 ]; then
            log_error "No previous revision available to rollback to"
            exit 1
        fi
        log_info "Rolling back to previous revision: ${revision}"
    else
        log_info "Rolling back to revision: ${revision}"
    fi

    # Confirmation
    echo ""
    log_warn "This will rollback '${release}' from revision ${current_rev} to revision ${revision}"
    read -p "Are you sure you want to proceed? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Rollback cancelled"
        exit 0
    fi

    # Perform rollback
    log_info "Performing rollback..."
    helm rollback "${release}" "${revision}" \
        --namespace "${NAMESPACE}" \
        --wait \
        --timeout 120s

    log_success "Rollback complete"

    # Verify
    echo ""
    log_info "Verifying rollback..."
    kubectl get pods -n "${NAMESPACE}" -l "app.kubernetes.io/instance=${release}"

    echo ""
    log_info "Updated release history:"
    helm history "${release}" -n "${NAMESPACE}" --max 5
}

# =============================================================================
# Main
# =============================================================================

echo ""
echo "=============================================="
echo "  AI Todo Chatbot - Rollback"
echo "=============================================="

if [ -z "${RELEASE}" ]; then
    show_usage
    exit 1
fi

rollback_release "${RELEASE}" "${2:-}"
