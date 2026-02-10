#!/usr/bin/env bash
# Task: T073 — Minikube deployment script for Phase 5 microservices
#
# Performs:
#   1. Prerequisite checks (minikube, dapr, kubectl)
#   2. Ensure Minikube is running
#   3. Install Dapr on K8s (if not already installed)
#   4. Deploy Redpanda (Kafka broker)
#   5. Create Kafka topics
#   6. Apply Dapr components
#   7. Create K8s secrets (requires DB connection string argument)
#   8. Build Docker images inside Minikube
#   9. Deploy all 5 microservices
#  10. Verify health endpoints
#
# Usage:
#   ./scripts/deploy-phase5.sh <neon-db-connection-string>
#
# Example:
#   ./scripts/deploy-phase5.sh "postgresql+asyncpg://user:pass@host/db?sslmode=require"

set -euo pipefail

NAMESPACE="todo-dev"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

info()  { echo -e "${GREEN}[INFO]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# ─── Step 1: Prerequisite checks ────────────────────────────────────────
info "Checking prerequisites..."

command -v minikube >/dev/null 2>&1 || error "minikube not found. Install: https://minikube.sigs.k8s.io/"
command -v kubectl  >/dev/null 2>&1 || error "kubectl not found. Install: https://kubernetes.io/docs/tasks/tools/"
command -v dapr     >/dev/null 2>&1 || error "dapr CLI not found. Install: https://docs.dapr.io/getting-started/install-dapr-cli/"
command -v docker   >/dev/null 2>&1 || error "docker not found. Install Docker Desktop."

if [ $# -lt 1 ]; then
    error "Usage: $0 <neon-db-connection-string>\n  Example: $0 \"postgresql+asyncpg://user:pass@host/db?sslmode=require\""
fi

DB_CONNECTION_STRING="$1"
info "Prerequisites OK"

# ─── Step 2: Ensure Minikube is running ──────────────────────────────────
if ! minikube status --format='{{.Host}}' 2>/dev/null | grep -q "Running"; then
    info "Starting Minikube (memory=3072MB)..."
    minikube start --memory=3072 --cpus=2 --driver=docker
else
    info "Minikube is already running"
fi

# ─── Step 3: Install Dapr on K8s ────────────────────────────────────────
if ! kubectl get namespace dapr-system >/dev/null 2>&1; then
    info "Installing Dapr on Kubernetes..."
    dapr init -k --wait
else
    info "Dapr already installed on Kubernetes"
fi

# ─── Step 4: Create namespace and deploy Redpanda ────────────────────────
info "Deploying Redpanda..."
kubectl apply -f "$PROJECT_ROOT/k8s/deployments/redpanda.yaml"

info "Waiting for Redpanda to be ready..."
kubectl wait --for=condition=ready pod \
    -l app=redpanda \
    -n "$NAMESPACE" \
    --timeout=120s

# ─── Step 5: Create Kafka topics ─────────────────────────────────────────
info "Creating Kafka topics..."
REDPANDA_POD=$(kubectl get pod -l app=redpanda -n "$NAMESPACE" -o jsonpath='{.items[0].metadata.name}')

for TOPIC in task-events task-updates reminders; do
    if kubectl exec "$REDPANDA_POD" -n "$NAMESPACE" -- \
        rpk topic list 2>/dev/null | grep -q "$TOPIC"; then
        info "Topic '$TOPIC' already exists"
    else
        kubectl exec "$REDPANDA_POD" -n "$NAMESPACE" -- \
            rpk topic create "$TOPIC" --partitions 1 --replicas 1
        info "Topic '$TOPIC' created"
    fi
done

# ─── Step 6: Apply Dapr components ───────────────────────────────────────
info "Applying Dapr components..."
kubectl apply -f "$PROJECT_ROOT/k8s/dapr-components/kafka-pubsub.yaml"
kubectl apply -f "$PROJECT_ROOT/k8s/dapr-components/statestore.yaml"
kubectl apply -f "$PROJECT_ROOT/k8s/dapr-components/kubernetes-secrets.yaml"

# ─── Step 7: Create K8s secrets ──────────────────────────────────────────
info "Creating K8s secrets..."
bash "$PROJECT_ROOT/k8s/secrets/create-secrets.sh" "$DB_CONNECTION_STRING"

# ─── Step 8: Build Docker images inside Minikube ─────────────────────────
info "Configuring Docker to use Minikube's daemon..."
eval $(minikube docker-env)

SERVICES=(todo-service audit-service websocket-service notification-service recurring-task-service)

for SERVICE in "${SERVICES[@]}"; do
    info "Building $SERVICE..."
    docker build \
        -t "$SERVICE:latest" \
        -f "$PROJECT_ROOT/services/$SERVICE/Dockerfile" \
        "$PROJECT_ROOT/services/"
done

info "All images built"

# ─── Step 9: Deploy all services ─────────────────────────────────────────
info "Deploying microservices..."
for SERVICE in "${SERVICES[@]}"; do
    kubectl apply -f "$PROJECT_ROOT/k8s/deployments/$SERVICE.yaml"
done

# ─── Step 10: Verify health endpoints ────────────────────────────────────
info "Waiting for all services to be ready (timeout: 180s)..."

for SERVICE in "${SERVICES[@]}"; do
    info "Waiting for $SERVICE..."
    kubectl wait --for=condition=ready pod \
        -l "app=$SERVICE" \
        -n "$NAMESPACE" \
        --timeout=180s || {
            warn "$SERVICE did not become ready in time"
            kubectl logs -l "app=$SERVICE" -n "$NAMESPACE" --tail=20
        }
done

# Health check verification via port-forward
info "Verifying health endpoints..."
PORTS=(8001 8002 8003 8004 8005)
ALL_HEALTHY=true

for i in "${!SERVICES[@]}"; do
    SERVICE="${SERVICES[$i]}"
    PORT="${PORTS[$i]}"

    # Quick port-forward test
    kubectl port-forward "svc/$SERVICE" "$PORT:$PORT" -n "$NAMESPACE" &
    PF_PID=$!
    sleep 2

    if curl -sf "http://localhost:$PORT/health" >/dev/null 2>&1; then
        info "$SERVICE health check: PASS"
    else
        warn "$SERVICE health check: FAIL"
        ALL_HEALTHY=false
    fi

    kill $PF_PID 2>/dev/null || true
    wait $PF_PID 2>/dev/null || true
done

# ─── Summary ─────────────────────────────────────────────────────────────
echo ""
echo "=========================================="
if $ALL_HEALTHY; then
    info "Phase 5 deployment COMPLETE — all services healthy"
else
    warn "Phase 5 deployment COMPLETE — some services unhealthy (check logs)"
fi
echo "=========================================="
echo ""
echo "Namespace: $NAMESPACE"
echo "Services:  ${SERVICES[*]}"
echo ""
echo "Useful commands:"
echo "  kubectl get pods -n $NAMESPACE"
echo "  kubectl logs -f <pod-name> -n $NAMESPACE"
echo "  kubectl port-forward svc/todo-service 8001:8001 -n $NAMESPACE"
