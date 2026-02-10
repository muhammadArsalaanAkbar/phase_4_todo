#!/usr/bin/env bash
# Task: T077 — End-to-end validation script for Phase 5 microservices
#
# Validates:
#   1. All pods running in todo-dev namespace
#   2. Dapr sidecars injected
#   3. Health endpoints responding
#   4. Todo CRUD operations
#   5. Audit trail populated
#   6. WebSocket service connections endpoint
#   7. Kafka topics exist
#   8. Phase 4 immutability (no files changed)
#
# Usage:
#   ./scripts/validate-phase5.sh
#
# Prerequisites:
#   Minikube running with Phase 5 deployed (via deploy-phase5.sh)

set -euo pipefail

NAMESPACE="todo-dev"
PASS_COUNT=0
FAIL_COUNT=0
TOTAL_CHECKS=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

check_pass() {
    PASS_COUNT=$((PASS_COUNT + 1))
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    echo -e "  ${GREEN}✓ PASS${NC}: $1"
}

check_fail() {
    FAIL_COUNT=$((FAIL_COUNT + 1))
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    echo -e "  ${RED}✗ FAIL${NC}: $1"
}

section() {
    echo ""
    echo -e "${CYAN}━━━ $1 ━━━${NC}"
}

# ─── Check 1: Prerequisites ────────────────────────────────────────────
section "1. Prerequisites"

if minikube status --format='{{.Host}}' 2>/dev/null | grep -q "Running"; then
    check_pass "Minikube is running"
else
    check_fail "Minikube is not running"
    echo "  Run: minikube start --memory=3072 --cpus=2 --driver=docker"
    exit 1
fi

if kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
    check_pass "Namespace '$NAMESPACE' exists"
else
    check_fail "Namespace '$NAMESPACE' not found"
    exit 1
fi

# ─── Check 2: All Pods Running ─────────────────────────────────────────
section "2. Pod Status"

SERVICES=(redpanda todo-service audit-service websocket-service notification-service recurring-task-service)

for SVC in "${SERVICES[@]}"; do
    POD_STATUS=$(kubectl get pods -l "app=$SVC" -n "$NAMESPACE" \
        -o jsonpath='{.items[0].status.phase}' 2>/dev/null || echo "NotFound")
    if [ "$POD_STATUS" = "Running" ]; then
        check_pass "$SVC pod is Running"
    else
        check_fail "$SVC pod status: $POD_STATUS"
    fi
done

# ─── Check 3: Dapr Sidecars Injected ──────────────────────────────────
section "3. Dapr Sidecars"

DAPR_SERVICES=(todo-service audit-service websocket-service notification-service recurring-task-service)

for SVC in "${DAPR_SERVICES[@]}"; do
    CONTAINERS=$(kubectl get pods -l "app=$SVC" -n "$NAMESPACE" \
        -o jsonpath='{.items[0].spec.containers[*].name}' 2>/dev/null || echo "")
    if echo "$CONTAINERS" | grep -q "daprd"; then
        check_pass "$SVC has Dapr sidecar"
    else
        check_fail "$SVC missing Dapr sidecar (containers: $CONTAINERS)"
    fi
done

# ─── Check 4: Kafka Topics ────────────────────────────────────────────
section "4. Kafka Topics"

REDPANDA_POD=$(kubectl get pod -l app=redpanda -n "$NAMESPACE" \
    -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -n "$REDPANDA_POD" ]; then
    for TOPIC in task-events task-updates reminders; do
        if kubectl exec "$REDPANDA_POD" -n "$NAMESPACE" -- \
            rpk topic list 2>/dev/null | grep -q "$TOPIC"; then
            check_pass "Topic '$TOPIC' exists"
        else
            check_fail "Topic '$TOPIC' not found"
        fi
    done
else
    check_fail "Redpanda pod not found — cannot check topics"
fi

# ─── Check 5: Health Endpoints ─────────────────────────────────────────
section "5. Health Endpoints"

PORTS=(8001 8002 8003 8004 8005)
SVC_NAMES=(todo-service audit-service websocket-service notification-service recurring-task-service)

for i in "${!SVC_NAMES[@]}"; do
    SVC="${SVC_NAMES[$i]}"
    PORT="${PORTS[$i]}"

    # Start port-forward in background
    kubectl port-forward "svc/$SVC" "$PORT:$PORT" -n "$NAMESPACE" >/dev/null 2>&1 &
    PF_PID=$!
    sleep 2

    if curl -sf "http://localhost:$PORT/health" >/dev/null 2>&1; then
        check_pass "$SVC /health (port $PORT)"
    else
        check_fail "$SVC /health (port $PORT)"
    fi

    kill $PF_PID 2>/dev/null || true
    wait $PF_PID 2>/dev/null || true
done

# ─── Check 6: Todo CRUD ───────────────────────────────────────────────
section "6. Todo Service CRUD"

kubectl port-forward svc/todo-service 8001:8001 -n "$NAMESPACE" >/dev/null 2>&1 &
PF_PID=$!
sleep 2

# Create a task
CREATE_RESP=$(curl -sf -X POST "http://localhost:8001/api/v1/tasks" \
    -H "Content-Type: application/json" \
    -d '{"title":"Validation test task","description":"Created by validate-phase5.sh"}' 2>/dev/null || echo "FAIL")

if echo "$CREATE_RESP" | grep -q "Validation test task"; then
    check_pass "POST /api/v1/tasks — task created"
    TASK_ID=$(echo "$CREATE_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")
else
    check_fail "POST /api/v1/tasks — create failed"
    TASK_ID=""
fi

# List tasks
LIST_RESP=$(curl -sf "http://localhost:8001/api/v1/tasks" 2>/dev/null || echo "FAIL")
if echo "$LIST_RESP" | grep -q "Validation test task"; then
    check_pass "GET /api/v1/tasks — list contains created task"
else
    check_fail "GET /api/v1/tasks — task not found in list"
fi

# Delete the test task (cleanup)
if [ -n "$TASK_ID" ]; then
    DEL_RESP=$(curl -sf -X DELETE "http://localhost:8001/api/v1/tasks/$TASK_ID" 2>/dev/null || echo "FAIL")
    if [ "$DEL_RESP" != "FAIL" ]; then
        check_pass "DELETE /api/v1/tasks/$TASK_ID — task deleted"
    else
        check_fail "DELETE /api/v1/tasks/$TASK_ID — delete failed"
    fi
fi

kill $PF_PID 2>/dev/null || true
wait $PF_PID 2>/dev/null || true

# ─── Check 7: Audit Trail ─────────────────────────────────────────────
section "7. Audit Service"

kubectl port-forward svc/audit-service 8002:8002 -n "$NAMESPACE" >/dev/null 2>&1 &
PF_PID=$!
sleep 2

AUDIT_RESP=$(curl -sf "http://localhost:8002/api/v1/audit" 2>/dev/null || echo "FAIL")
if echo "$AUDIT_RESP" | grep -q "records"; then
    check_pass "GET /api/v1/audit — audit endpoint responding"
else
    check_fail "GET /api/v1/audit — audit endpoint not responding"
fi

kill $PF_PID 2>/dev/null || true
wait $PF_PID 2>/dev/null || true

# ─── Check 8: WebSocket Connections ────────────────────────────────────
section "8. WebSocket Service"

kubectl port-forward svc/websocket-service 8003:8003 -n "$NAMESPACE" >/dev/null 2>&1 &
PF_PID=$!
sleep 2

CONN_RESP=$(curl -sf "http://localhost:8003/api/v1/connections" 2>/dev/null || echo "FAIL")
if echo "$CONN_RESP" | grep -q "active_connections"; then
    check_pass "GET /api/v1/connections — WS service responding"
else
    check_fail "GET /api/v1/connections — WS service not responding"
fi

kill $PF_PID 2>/dev/null || true
wait $PF_PID 2>/dev/null || true

# ─── Check 9: Phase 4 Immutability ────────────────────────────────────
section "9. Phase 4 Immutability"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

CHANGED=$(git -C "$PROJECT_ROOT" diff --name-only HEAD -- \
    k8s/phase4/ kubernetes/ 2>/dev/null || true)

if [ -z "$CHANGED" ]; then
    check_pass "Phase 4 files unchanged"
else
    check_fail "Phase 4 files modified: $CHANGED"
fi

# ─── Summary ──────────────────────────────────────────────────────────
echo ""
echo "==========================================="
echo -e "  ${CYAN}Phase 5 Validation Summary${NC}"
echo "==========================================="
echo -e "  Total checks: $TOTAL_CHECKS"
echo -e "  ${GREEN}Passed${NC}: $PASS_COUNT"
echo -e "  ${RED}Failed${NC}: $FAIL_COUNT"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "  ${GREEN}RESULT: ALL CHECKS PASSED${NC}"
    exit 0
else
    echo -e "  ${YELLOW}RESULT: $FAIL_COUNT CHECK(S) FAILED${NC}"
    exit 1
fi
