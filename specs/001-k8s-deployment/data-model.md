# Data Model: Kubernetes Deployment

**Feature**: 001-k8s-deployment
**Date**: 2025-02-07
**Status**: Complete

## Overview

This feature is infrastructure-focused. The "data model" consists of Kubernetes
resource definitions and Helm value schemas rather than application entities.

---

## Kubernetes Resources

### 1. Deployment

Represents a running instance of a service (frontend or backend).

| Field | Type | Description |
|-------|------|-------------|
| name | string | Service identifier (todo-frontend, todo-backend) |
| replicas | int | Number of pod instances (1-5) |
| image | string | Container image with tag or SHA |
| resources | ResourceSpec | CPU/memory requests and limits |
| probes | ProbeSpec | Health check configurations |
| env | []EnvVar | Environment variables from ConfigMap/Secret |

**Relationships**:
- References ConfigMap for public configuration
- References Secret for sensitive configuration
- Managed by HorizontalPodAutoscaler

---

### 2. Service

Exposes a Deployment to network traffic.

| Field | Type | Description |
|-------|------|-------------|
| name | string | Service identifier |
| type | string | ClusterIP (internal) or NodePort (external) |
| port | int | Exposed port number |
| targetPort | int | Container port to forward to |

**Relationships**:
- Selects pods via label selector
- Referenced by Ingress for external access

---

### 3. ConfigMap

Stores non-sensitive configuration.

| Field | Type | Description |
|-------|------|-------------|
| name | string | ConfigMap identifier |
| data | map[string]string | Key-value configuration pairs |

**Frontend ConfigMap Keys**:
- `NODE_ENV`: Environment mode (development/production)
- `NEXT_PUBLIC_API_URL`: Backend API endpoint

**Backend ConfigMap Keys**:
- `LOG_LEVEL`: Logging verbosity (DEBUG/INFO/WARN/ERROR)
- `CORS_ORIGINS`: Allowed CORS origins

---

### 4. Secret

Stores sensitive configuration (encrypted at rest).

| Field | Type | Description |
|-------|------|-------------|
| name | string | Secret identifier |
| type | string | Opaque (generic secret) |
| data | map[string][]byte | Base64-encoded secret values |

**Backend Secret Keys**:
- `DATABASE_URL`: Neon PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key for AI features
- `JWT_SECRET`: JWT signing key

---

### 5. HorizontalPodAutoscaler

Manages automatic scaling based on metrics.

| Field | Type | Description |
|-------|------|-------------|
| name | string | HPA identifier |
| minReplicas | int | Minimum pod count |
| maxReplicas | int | Maximum pod count |
| targetCPU | int | CPU utilization target (%) |

**Relationships**:
- Targets a Deployment by name

---

### 6. NetworkPolicy

Controls network traffic between pods.

| Field | Type | Description |
|-------|------|-------------|
| name | string | Policy identifier |
| podSelector | LabelSelector | Pods this policy applies to |
| ingress | []IngressRule | Allowed incoming traffic |
| egress | []EgressRule | Allowed outgoing traffic |

---

### 7. Ingress

Exposes services externally via HTTP/HTTPS.

| Field | Type | Description |
|-------|------|-------------|
| name | string | Ingress identifier |
| host | string | Hostname for routing |
| paths | []PathRule | URL path to service mappings |

---

## State Transitions

### Deployment Lifecycle

```
┌──────────┐     helm install     ┌──────────┐
│  Empty   │ ──────────────────→  │ Running  │
└──────────┘                      └──────────┘
                                       │
                                       │ helm upgrade
                                       ▼
                                  ┌──────────┐
                                  │ Updating │
                                  └──────────┘
                                       │
                         ┌─────────────┼─────────────┐
                         │ success     │             │ failure
                         ▼             │             ▼
                    ┌──────────┐       │       ┌──────────┐
                    │ Running  │       │       │ Rollback │
                    │ (new)    │       │       └──────────┘
                    └──────────┘       │             │
                                       │             │ automatic
                                       │             ▼
                                       │       ┌──────────┐
                                       └──────→│ Running  │
                                               │ (prev)   │
                                               └──────────┘
```

### Pod Lifecycle

```
┌──────────┐    scheduled    ┌──────────┐   startup    ┌──────────┐
│ Pending  │ ─────────────→  │ Starting │ ──────────→  │  Ready   │
└──────────┘                 └──────────┘   probe OK   └──────────┘
                                  │                         │
                                  │ startup                 │ readiness
                                  │ probe fail              │ probe fail
                                  ▼                         ▼
                             ┌──────────┐            ┌──────────┐
                             │  Failed  │            │ Not Ready│
                             └──────────┘            └──────────┘
```

---

## Validation Rules

### Resource Constraints

| Resource | Min | Max | Reason |
|----------|-----|-----|--------|
| CPU Request | 50m | 2000m | Cluster capacity |
| Memory Request | 64Mi | 2Gi | Cluster capacity |
| Replicas | 1 | 10 | Prevent resource exhaustion |

### Naming Conventions

| Resource Type | Pattern | Example |
|---------------|---------|---------|
| Deployment | `todo-{service}` | `todo-frontend` |
| Service | `todo-{service}-svc` | `todo-frontend-svc` |
| ConfigMap | `todo-{service}-config` | `todo-backend-config` |
| Secret | `todo-{service}-secrets` | `todo-backend-secrets` |
| HPA | `todo-{service}-hpa` | `todo-frontend-hpa` |

### Label Standards

All resources MUST include:

```yaml
labels:
  app.kubernetes.io/name: todo-chatbot
  app.kubernetes.io/component: {frontend|backend|infrastructure}
  app.kubernetes.io/version: {chart-version}
  app.kubernetes.io/managed-by: Helm
```
