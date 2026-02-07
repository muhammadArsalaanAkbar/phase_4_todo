# Quickstart: Kubernetes Deployment

**Feature**: 001-k8s-deployment
**Time to Deploy**: ~5 minutes

## Prerequisites

Before deploying, ensure you have:

- [ ] Minikube 1.32+ installed and running
- [ ] Helm 3.x installed
- [ ] kubectl configured for Minikube
- [ ] Docker CLI available
- [ ] At least 4 CPU cores and 8GB RAM allocated to Minikube

### Verify Prerequisites

```bash
# Check Minikube
minikube version
minikube status

# Check Helm
helm version

# Check kubectl
kubectl version --client

# Check Minikube resources
minikube config view
```

---

## Quick Deploy (Single Command)

```bash
# From repository root
./scripts/deploy.sh
```

This script will:
1. Verify prerequisites
2. Configure Docker to use Minikube's daemon
3. Build container images
4. Create namespaces and secrets
5. Deploy all Helm charts
6. Wait for pods to be ready
7. Print access URLs

---

## Manual Deployment Steps

### 1. Start Minikube (if not running)

```bash
minikube start --cpus=4 --memory=8192 --driver=docker
minikube addons enable ingress
minikube addons enable metrics-server
```

### 2. Configure Docker Environment

```bash
# Point Docker CLI to Minikube's daemon
eval $(minikube docker-env)
```

### 3. Build Container Images

```bash
# Build frontend
docker build -t todo-frontend:dev-latest -f docker/frontend/Dockerfile .

# Build backend
docker build -t todo-backend:dev-latest -f docker/backend/Dockerfile .
```

### 4. Create Namespace

```bash
kubectl create namespace todo-dev
```

### 5. Create Secrets

```bash
# Create secrets from environment file
./scripts/create-secrets.sh

# Or manually:
kubectl create secret generic todo-backend-secrets \
  --namespace todo-dev \
  --from-literal=DATABASE_URL="your-neon-connection-string" \
  --from-literal=OPENAI_API_KEY="your-openai-key" \
  --from-literal=JWT_SECRET="your-jwt-secret"
```

### 6. Deploy Infrastructure Chart

```bash
helm upgrade --install todo-infrastructure charts/todo-infrastructure \
  --namespace todo-dev \
  --wait
```

### 7. Deploy Backend

```bash
helm upgrade --install todo-backend charts/todo-backend \
  --namespace todo-dev \
  --values charts/todo-backend/values-dev.yaml \
  --wait --atomic
```

### 8. Deploy Frontend

```bash
helm upgrade --install todo-frontend charts/todo-frontend \
  --namespace todo-dev \
  --values charts/todo-frontend/values-dev.yaml \
  --wait --atomic
```

### 9. Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n todo-dev

# Check services
kubectl get svc -n todo-dev

# Check ingress
kubectl get ingress -n todo-dev
```

---

## Accessing the Application

### Via Minikube Tunnel

```bash
# Start tunnel (run in separate terminal)
minikube tunnel

# Access at http://todo.local (add to /etc/hosts if needed)
```

### Via NodePort

```bash
# Get service URL
minikube service todo-frontend-svc -n todo-dev --url
```

### Add Local DNS Entry

```bash
# Add to /etc/hosts (Linux/Mac) or C:\Windows\System32\drivers\etc\hosts (Windows)
echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts
```

---

## Updating the Deployment

```bash
# Rebuild image with new tag
docker build -t todo-backend:dev-$(git rev-parse --short HEAD) -f docker/backend/Dockerfile .

# Upgrade with new image
helm upgrade todo-backend charts/todo-backend \
  --namespace todo-dev \
  --set image.tag=dev-$(git rev-parse --short HEAD) \
  --wait --atomic
```

---

## Rolling Back

```bash
# List revisions
helm history todo-backend -n todo-dev

# Rollback to previous
helm rollback todo-backend -n todo-dev

# Rollback to specific revision
helm rollback todo-backend 2 -n todo-dev
```

---

## Viewing Logs

```bash
# All backend logs
kubectl logs -l app.kubernetes.io/component=backend -n todo-dev -f

# Specific pod
kubectl logs todo-backend-xxx -n todo-dev -f
```

---

## Viewing Metrics

```bash
# Port-forward Grafana
kubectl port-forward svc/grafana -n todo-system 3000:3000

# Access at http://localhost:3000
```

---

## Cleanup

```bash
# Uninstall all releases
helm uninstall todo-frontend -n todo-dev
helm uninstall todo-backend -n todo-dev
helm uninstall todo-infrastructure -n todo-dev

# Delete namespace
kubectl delete namespace todo-dev

# Stop Minikube (optional)
minikube stop
```

---

## Troubleshooting

### Pods not starting

```bash
# Check events
kubectl describe pod <pod-name> -n todo-dev

# Check logs
kubectl logs <pod-name> -n todo-dev
```

### Image pull errors

```bash
# Ensure Docker is using Minikube's daemon
eval $(minikube docker-env)

# Verify image exists
docker images | grep todo
```

### Secret errors

```bash
# Verify secret exists
kubectl get secret todo-backend-secrets -n todo-dev

# Check secret keys
kubectl describe secret todo-backend-secrets -n todo-dev
```

### Ingress not working

```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# Check ingress status
kubectl describe ingress -n todo-dev
```

---

## AI-Assisted Operations (Optional)

If kubectl-ai is installed:

```bash
# Query cluster state
kubectl-ai "show me all pods in todo-dev namespace"

# Debug issues
kubectl-ai "why is the backend pod not ready?"
```
