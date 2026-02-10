# Quickstart: Phase 5 Microservices Platform

**Feature**: `002-microservices-dapr-kafka`
**Goal**: Get all 5 microservices running on Minikube with Dapr and Kafka in
under 10 minutes.

## Prerequisites

- Docker Desktop running (3.7GB+ memory allocated)
- Minikube installed (`minikube version` >= 1.32)
- kubectl installed
- Dapr CLI installed (`dapr --version` >= 1.14)
- A Neon DB (or PostgreSQL) connection string

## Quick Deploy (Automated)

The fastest way to deploy everything:

```bash
./scripts/deploy-phase5.sh "postgresql+asyncpg://user:pass@host/db?sslmode=require"
```

This single script handles all 10 steps below automatically.

## Manual Deploy (Step by Step)

### Step 1: Start Minikube

```bash
minikube start --memory=3072 --cpus=2 --driver=docker
```

### Step 2: Install Dapr on Kubernetes

```bash
dapr init -k --wait
# Verify:
dapr status -k
```

### Step 3: Deploy Redpanda (Kafka)

```bash
kubectl apply -f k8s/deployments/redpanda.yaml
# Wait for Redpanda to be ready:
kubectl wait --for=condition=ready pod -l app=redpanda -n todo-dev --timeout=120s
```

### Step 4: Create Kafka Topics

```bash
REDPANDA_POD=$(kubectl get pod -l app=redpanda -n todo-dev -o jsonpath='{.items[0].metadata.name}')
kubectl exec "$REDPANDA_POD" -n todo-dev -- rpk topic create task-events --partitions 1 --replicas 1
kubectl exec "$REDPANDA_POD" -n todo-dev -- rpk topic create task-updates --partitions 1 --replicas 1
kubectl exec "$REDPANDA_POD" -n todo-dev -- rpk topic create reminders --partitions 1 --replicas 1
```

### Step 5: Deploy Dapr Components

```bash
kubectl apply -f k8s/dapr-components/kafka-pubsub.yaml
kubectl apply -f k8s/dapr-components/statestore.yaml
kubectl apply -f k8s/dapr-components/kubernetes-secrets.yaml
# Verify:
kubectl get components -n todo-dev
```

### Step 6: Create Kubernetes Secrets

```bash
bash k8s/secrets/create-secrets.sh "postgresql+asyncpg://user:pass@host/db?sslmode=require"
```

### Step 7: Build Docker Images

```bash
eval $(minikube docker-env)
docker build -t todo-service:latest -f services/todo-service/Dockerfile services/
docker build -t audit-service:latest -f services/audit-service/Dockerfile services/
docker build -t websocket-service:latest -f services/websocket-service/Dockerfile services/
docker build -t notification-service:latest -f services/notification-service/Dockerfile services/
docker build -t recurring-task-service:latest -f services/recurring-task-service/Dockerfile services/
```

### Step 8: Deploy Microservices

```bash
kubectl apply -f k8s/deployments/todo-service.yaml
kubectl apply -f k8s/deployments/audit-service.yaml
kubectl apply -f k8s/deployments/websocket-service.yaml
kubectl apply -f k8s/deployments/notification-service.yaml
kubectl apply -f k8s/deployments/recurring-task-service.yaml
# Wait for all pods:
kubectl wait --for=condition=ready pod --all -n todo-dev --timeout=180s
```

### Step 9: Verify

```bash
# Check all pods are running:
kubectl get pods -n todo-dev

# Test Todo Service health:
kubectl port-forward svc/todo-service 8001:8001 -n todo-dev &
curl http://localhost:8001/health

# Create a test task:
curl -X POST http://localhost:8001/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "description": "Hello Phase 5"}'

# Check audit trail:
kubectl port-forward svc/audit-service 8002:8002 -n todo-dev &
curl http://localhost:8002/api/v1/audit
```

### Step 10: Validate (Optional)

Run the full validation suite:

```bash
./scripts/validate-phase5.sh
```

## Port Assignments

| Service | Port | Access |
|---------|------|--------|
| Todo Service | 8001 | `kubectl port-forward svc/todo-service 8001:8001 -n todo-dev` |
| Audit Service | 8002 | `kubectl port-forward svc/audit-service 8002:8002 -n todo-dev` |
| WebSocket Service | 8003 | `kubectl port-forward svc/websocket-service 8003:8003 -n todo-dev` |
| Notification Service | 8004 | `kubectl port-forward svc/notification-service 8004:8004 -n todo-dev` |
| Recurring Task Service | 8005 | `kubectl port-forward svc/recurring-task-service 8005:8005 -n todo-dev` |
| Redpanda (Kafka) | 9092 | Internal only (ClusterIP) |

## Environment Variables

Each service reads from environment variables. See `.env.example` in each service directory:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes* | `""` | PostgreSQL asyncpg connection string |
| `DAPR_HTTP_PORT` | No | `3500` | Dapr sidecar HTTP port |
| `DAPR_GRPC_PORT` | No | `50001` | Dapr sidecar gRPC port |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG/INFO/WARNING/ERROR) |

*Not required for WebSocket Service (stateless).

## Troubleshooting

**Dapr sidecar not injecting**: Ensure Dapr annotations are in pod template metadata:
```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "service-name"
  dapr.io/app-port: "8001"
```

**Events not flowing**: Check Dapr Pub/Sub component and topic subscriptions:
```bash
kubectl logs <pod-name> -c daprd -n todo-dev | grep pubsub
curl http://localhost:<port>/dapr/subscribe
```

**Database connection failed**: Verify secret exists:
```bash
kubectl get secret dapr-db-secret -n todo-dev
kubectl get secret dapr-db-secret -n todo-dev -o jsonpath='{.data.connectionString}' | base64 -d
```

**Pod CrashLoopBackOff**: Check container logs:
```bash
kubectl logs <pod-name> -n todo-dev
kubectl describe pod <pod-name> -n todo-dev
```

**Images not found (ErrImagePull)**: Ensure you built inside Minikube:
```bash
eval $(minikube docker-env)
docker images | grep service
```
