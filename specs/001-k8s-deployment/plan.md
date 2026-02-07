# Implementation Plan: Kubernetes Deployment

**Branch**: `001-k8s-deployment` | **Date**: 2025-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-k8s-deployment/spec.md`

## Summary

Deploy the AI Todo Chatbot (Next.js frontend + FastAPI backend) to a local Kubernetes
cluster using Helm charts. The implementation provides single-command deployment,
secure secrets management, atomic updates with rollback, and full observability
through Prometheus/Grafana. This directly fulfills the Phase IV constitution's
North Star goal.

## Technical Context

**Language/Version**: TypeScript 5.x (frontend), Python 3.11 (backend)
**Primary Dependencies**: Helm 3.x, Minikube 1.32+, Docker/containerd
**Storage**: Neon PostgreSQL (external, accessed via connection string)
**Testing**: helm lint, helm template, kubectl wait, integration scripts
**Target Platform**: Minikube on Linux/macOS/Windows (local Kubernetes)
**Project Type**: Infrastructure (Helm charts + Dockerfiles for web application)
**Performance Goals**: Full deployment in <5 minutes, pod health in <60 seconds
**Constraints**: 4 CPU cores, 8GB RAM minimum cluster allocation
**Scale/Scope**: 2 services (frontend, backend), 3 Helm charts, 3 environments

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Plan Compliance | Status |
|-----------|-------------|-----------------|--------|
| I. Container-First | All services in containers with pinned base images | Dockerfiles for frontend/backend with SHA-pinned bases | PASS |
| II. No Manual YAML | All K8s resources via Helm | 3 Helm charts (frontend, backend, infrastructure) | PASS |
| III. Secrets Governance | No hardcoded secrets | K8s Secrets with env.example templates | PASS |
| IV. Helm-Managed | Helm exclusive deployment | `helm upgrade --atomic` as standard command | PASS |
| V. AI-Assisted DevOps | kubectl-ai/kagent available | Optional tooling documented in quickstart | PASS |
| VI. Observability | Logs, metrics, traces | JSON logs, Prometheus metrics, OTEL traces | PASS |
| VII. Immutable Infrastructure | No in-place changes | Checksum annotations for ConfigMap/Secret rotation | PASS |
| VIII. Fail-Fast | Validate at build/deploy time | helm lint in CI, startup probes, schema validation | PASS |

**Gate Result**: PASS - All 8 principles satisfied. Proceeding to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/001-k8s-deployment/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (Helm value schemas)
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
# Infrastructure artifacts
charts/
├── todo-frontend/
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── values-dev.yaml
│   ├── values-staging.yaml
│   ├── values-prod.yaml
│   └── templates/
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── ingress.yaml
│       ├── configmap.yaml
│       ├── hpa.yaml
│       ├── networkpolicy.yaml
│       └── _helpers.tpl
├── todo-backend/
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── values-dev.yaml
│   ├── values-staging.yaml
│   ├── values-prod.yaml
│   └── templates/
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── configmap.yaml
│       ├── hpa.yaml
│       ├── networkpolicy.yaml
│       ├── serviceaccount.yaml
│       └── _helpers.tpl
└── todo-infrastructure/
    ├── Chart.yaml
    ├── values.yaml
    └── templates/
        ├── namespace.yaml
        ├── resourcequota.yaml
        ├── secrets-template.yaml
        └── monitoring/
            ├── prometheus-config.yaml
            ├── grafana-config.yaml
            └── servicemonitor.yaml

# Container definitions
docker/
├── frontend/
│   ├── Dockerfile
│   └── .dockerignore
└── backend/
    ├── Dockerfile
    └── .dockerignore

# Deployment scripts
scripts/
├── deploy.sh              # Single-command deployment
├── rollback.sh            # Manual rollback helper
├── create-secrets.sh      # Secret creation from env.example
└── validate.sh            # Pre-deployment validation

# Environment templates
env.example.frontend       # Frontend env vars documentation
env.example.backend        # Backend env vars documentation
```

**Structure Decision**: Infrastructure-focused layout. Helm charts are the primary
artifacts. Docker files and scripts support the deployment workflow. No changes to
existing frontend/backend source code structure.

## Complexity Tracking

> No constitution violations requiring justification.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |
