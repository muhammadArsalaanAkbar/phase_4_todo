# Research: Kubernetes Deployment

**Feature**: 001-k8s-deployment
**Date**: 2025-02-07
**Status**: Complete

## Research Tasks

This document captures technical decisions made during Phase 0 research.

---

## 1. Helm Chart Structure Best Practices

**Decision**: One chart per service boundary (frontend, backend, infrastructure)

**Rationale**:
- Follows Helm community best practices for microservices
- Enables independent versioning and deployment of each service
- Allows different teams to own different charts
- Simplifies rollback (can roll back single service)
- Constitution mandates Helm-managed deployments (Principle IV)

**Alternatives Considered**:
| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| Monorepo umbrella chart | Single deploy command | Tight coupling, all-or-nothing rollback | Violates independence principle |
| Kustomize overlays | Native K8s, no Helm dependency | No release management, no rollback | Constitution mandates Helm |
| Raw YAML + kubectl | Simplest | Error-prone, no parameterization | Constitution prohibits (Principle II) |

---

## 2. Base Image Selection

**Decision**: Use official distroless or alpine-based images with SHA pinning

**Frontend (Next.js)**:
- Base: `node:20-alpine` pinned to SHA
- Final: `gcr.io/distroless/nodejs20-debian12` for production
- Size target: <200MB

**Backend (FastAPI)**:
- Base: `python:3.11-slim` pinned to SHA
- Final: `python:3.11-slim` with non-root user
- Size target: <300MB

**Rationale**:
- Alpine/slim reduces attack surface and image size
- Distroless eliminates shell access (security hardening)
- SHA pinning ensures reproducible builds (Constitution Principle I)
- Non-root execution required by Constitution Principle (Security Standards)

**Alternatives Considered**:
| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| Ubuntu-based | Familiar, easy debugging | Large (500MB+), more vulnerabilities | Size and security concerns |
| Scratch images | Smallest possible | No debugging tools, complex builds | Too difficult for Phase IV |
| :latest tags | Always current | Non-reproducible, drift risk | Constitution prohibits |

---

## 3. Secrets Injection Pattern

**Decision**: Kubernetes Secrets with environment variable injection

**Pattern**:
1. Developer creates `.env.local` from `env.example` templates
2. `create-secrets.sh` script generates K8s Secret manifests
3. Secrets referenced by name in Helm values (never values themselves)
4. Pods inject secrets via `envFrom` or individual `env` references
5. Checksum annotation triggers pod restart on secret change

**Required Secrets**:
| Secret Name | Keys | Service |
|-------------|------|---------|
| `todo-backend-secrets` | `DATABASE_URL`, `OPENAI_API_KEY`, `JWT_SECRET` | Backend |
| `todo-frontend-secrets` | `NEXT_PUBLIC_API_URL` (if sensitive) | Frontend |

**Rationale**:
- Native Kubernetes pattern, no external dependencies
- Supports secret rotation without image rebuilds
- Constitution Principle III compliance
- Simple for local development (Phase IV scope)

**Alternatives Considered**:
| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| External Secrets Operator | Production-grade, vault integration | Overkill for local dev | Out of scope for Phase IV |
| Sealed Secrets | GitOps-friendly | Requires controller, complexity | Out of scope for Phase IV |
| ConfigMaps | Simpler | Not encrypted, visible in kubectl | Secrets must be encrypted |

---

## 4. Health Check Configuration

**Decision**: Three-probe pattern (liveness, readiness, startup)

**Frontend Probes**:
```yaml
livenessProbe:
  httpGet:
    path: /api/health
    port: 3000
  initialDelaySeconds: 10
  periodSeconds: 10
readinessProbe:
  httpGet:
    path: /api/health
    port: 3000
  initialDelaySeconds: 5
  periodSeconds: 5
startupProbe:
  httpGet:
    path: /api/health
    port: 3000
  failureThreshold: 30
  periodSeconds: 2
```

**Backend Probes**:
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10
readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
startupProbe:
  httpGet:
    path: /health
    port: 8000
  failureThreshold: 30
  periodSeconds: 2
```

**Rationale**:
- Startup probe prevents premature liveness failures during slow starts
- Readiness probe ensures traffic only routes to ready pods
- Liveness probe detects hung processes
- Constitution Principle VI and VIII compliance

---

## 5. Resource Allocation Strategy

**Decision**: Conservative defaults with per-environment overrides

**Default Resources (dev)**:
| Service | CPU Request | CPU Limit | Memory Request | Memory Limit |
|---------|-------------|-----------|----------------|--------------|
| Frontend | 100m | 500m | 128Mi | 512Mi |
| Backend | 200m | 1000m | 256Mi | 1Gi |

**Scaling (prod-like)**:
| Service | Min Replicas | Max Replicas | CPU Target |
|---------|--------------|--------------|------------|
| Frontend | 2 | 5 | 70% |
| Backend | 2 | 5 | 70% |

**Rationale**:
- Fits within Minikube 4-core/8GB constraints
- Leaves headroom for monitoring stack
- HPA enables automatic scaling under load
- Constitution Principle (Resource Definitions) compliance

---

## 6. Network Policy Design

**Decision**: Default-deny with explicit allow rules

**Policies**:
1. `deny-all`: Default deny all ingress/egress in namespace
2. `allow-frontend-ingress`: Ingress controller → Frontend pods
3. `allow-frontend-to-backend`: Frontend pods → Backend pods
4. `allow-backend-egress`: Backend pods → External (Neon PostgreSQL, OpenAI)
5. `allow-dns`: All pods → kube-dns

**Rationale**:
- Defense in depth (Constitution Security Standards)
- Limits blast radius of compromised pod
- Documents expected traffic flows
- Can be disabled in dev if needed (values override)

---

## 7. Observability Stack

**Decision**: Prometheus + Grafana + Loki (optional in Phase IV)

**Components**:
| Component | Purpose | Deployment |
|-----------|---------|------------|
| Prometheus | Metrics collection | Helm subchart dependency |
| Grafana | Dashboards | Helm subchart dependency |
| ServiceMonitor | Metric discovery | Part of todo-infrastructure |

**Metrics Exposed**:
- Frontend: Next.js default metrics + custom request duration
- Backend: FastAPI prometheus-fastapi-instrumentator

**Log Format** (JSON):
```json
{
  "timestamp": "2025-02-07T10:30:00Z",
  "level": "INFO",
  "service": "backend",
  "message": "Request processed",
  "trace_id": "abc123",
  "duration_ms": 45
}
```

**Rationale**:
- Industry standard stack
- Constitution Principle VI compliance
- Prometheus/Grafana Helm charts are well-maintained
- JSON logs enable future log aggregation

---

## 8. Deployment Script Design

**Decision**: Shell wrapper around Helm commands

**`deploy.sh` workflow**:
1. Validate prerequisites (minikube, helm, kubectl)
2. Set docker environment (`eval $(minikube docker-env)`)
3. Build images if source changed
4. Create namespace if not exists
5. Apply secrets (prompt if missing)
6. `helm upgrade --install --atomic` for each chart
7. Wait for pods ready
8. Print access URLs

**`rollback.sh` workflow**:
1. List available revisions
2. `helm rollback <release> <revision>`
3. Wait for pods ready

**Rationale**:
- Single command fulfills SC-001 (deploy in <5 minutes)
- Atomic flag ensures SC-010 (auto-rollback on failure)
- Script abstracts complexity while remaining transparent

---

## Summary

All technical decisions align with constitution principles. No NEEDS CLARIFICATION
items remain. Ready to proceed to Phase 1 design.
