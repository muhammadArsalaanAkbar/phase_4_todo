<!--
================================================================================
SYNC IMPACT REPORT
================================================================================
Version Change: 0.0.0 → 1.0.0 (MAJOR - initial constitution ratification)

Added Principles:
  - I. Container-First Architecture
  - II. No Manual YAML
  - III. Secrets Governance
  - IV. Helm-Managed Deployments
  - V. AI-Assisted DevOps
  - VI. Observability by Default
  - VII. Immutable Infrastructure
  - VIII. Fail-Fast Validation

Added Sections:
  - Infrastructure Rules
  - Environment Variable Governance
  - Containerization Standards
  - Kubernetes Standards
  - Helm Governance
  - AI DevOps Policy
  - Security Standards
  - Scalability Standards
  - Observability & Debugging Policy
  - Non-Goals
  - Acceptance Definition

Templates Requiring Updates:
  ✅ plan-template.md - Constitution Check section compatible
  ✅ spec-template.md - Requirements section compatible
  ✅ tasks-template.md - Phase structure compatible

Follow-up TODOs: None
================================================================================
-->

# AI-Native Todo Chatbot Constitution — Phase IV

## Vision

Phase IV transforms the AI-Native Todo Chatbot from a cloud-hosted application into a
**production-grade, locally-deployable Kubernetes workload**. This phase establishes
the infrastructure patterns, DevOps practices, and operational standards that enable
the system to run reliably on Minikube today and scale to managed Kubernetes clusters
(EKS, GKE, AKS) in the future.

**North Star**: Any developer MUST be able to spin up the complete system locally with
a single command (`helm install`) and have full observability within 5 minutes.

## Core Principles

### I. Container-First Architecture

Every service, utility, and dependency MUST run inside a container. Host-level
dependencies are forbidden except for container runtime prerequisites.

- All application components (Next.js frontend, FastAPI backend) MUST have Dockerfiles
- Build artifacts MUST be container images, not raw binaries or source deployments
- Local development MUST use the same container images that production uses
- Base images MUST be pinned to specific SHA digests, not floating tags

**Rationale**: Container-first ensures environment parity, eliminates "works on my
machine" failures, and provides the foundation for Kubernetes orchestration.

### II. No Manual YAML

Kubernetes manifests MUST NOT be hand-written. All Kubernetes resources MUST be
generated through Helm charts, Kustomize overlays, or AI-assisted tooling.

- Direct `kubectl apply -f` of hand-written YAML is prohibited in production workflows
- Helm templates MUST be the canonical source for all Kubernetes objects
- `kubectl-ai` and `kagent` MAY be used for exploration and prototyping
- Generated manifests MUST be committed to version control for auditability

**Rationale**: Manual YAML is error-prone, inconsistent, and unscalable. Template-based
generation enforces standards and enables parameterized deployments.

### III. Secrets Governance

Secrets MUST NEVER be hardcoded in source code, container images, Helm values, or
any file tracked in version control.

- All secrets MUST be injected via Kubernetes Secrets or external secret managers
- `.env` files are permitted for local development ONLY and MUST be gitignored
- Secrets MUST be referenced by name in Helm values, never by value
- Secret rotation MUST be possible without rebuilding images or redeploying charts
- OpenAI API keys, database credentials, and JWT secrets are explicitly covered

**Rationale**: Hardcoded secrets are a critical security vulnerability. External
injection enables rotation, auditing, and least-privilege access patterns.

### IV. Helm-Managed Deployments

Helm MUST be the exclusive deployment mechanism for all Kubernetes resources.

- One Helm chart per logical service boundary (frontend, backend, infrastructure)
- Charts MUST support multiple environments via values files (dev, staging, prod)
- Chart versions MUST follow SemVer and be tagged in version control
- `helm upgrade --atomic` MUST be the standard deployment command
- Rollback capability (`helm rollback`) MUST be tested and documented

**Rationale**: Helm provides release management, rollback capability, and
parameterization that raw manifests cannot. Atomic upgrades prevent partial failures.

### V. AI-Assisted DevOps

AI tooling (`kubectl-ai`, `kagent`) MUST be leveraged to accelerate Kubernetes
operations while maintaining human oversight.

- AI-generated manifests MUST be reviewed before applying to any environment
- `kubectl-ai` MAY be used for debugging, resource inspection, and one-off queries
- `kagent` MAY be used for automated remediation with explicit approval workflows
- AI suggestions MUST be validated against security policies before execution
- Human approval is REQUIRED for any destructive operation (delete, scale-to-zero)

**Rationale**: AI accelerates DevOps velocity but is not infallible. Human-in-the-loop
ensures accountability and prevents automated misconfiguration.

### VI. Observability by Default

Every deployed component MUST emit structured logs, expose metrics, and propagate
distributed traces without additional configuration.

- Logs MUST be JSON-formatted and written to stdout/stderr
- Prometheus metrics MUST be exposed on a standard `/metrics` endpoint
- OpenTelemetry tracing MUST be instrumented for all HTTP/gRPC boundaries
- Health checks (liveness, readiness, startup) MUST be defined for all containers
- Dashboards and alerts MUST be deployed alongside the application

**Rationale**: You cannot manage what you cannot measure. Observability is not
optional—it is a deployment prerequisite.

### VII. Immutable Infrastructure

Deployed containers MUST be treated as immutable. Configuration changes MUST trigger
new deployments, not in-place modifications.

- `kubectl exec` for configuration changes is prohibited
- ConfigMaps and Secrets trigger pod restarts when changed (via checksums)
- Image tags MUST be immutable (no `:latest` in production)
- Debugging containers MAY be attached ephemerally but MUST NOT persist changes

**Rationale**: Immutability ensures reproducibility and eliminates configuration drift
that makes debugging impossible.

### VIII. Fail-Fast Validation

Misconfigurations MUST be caught at build time or deploy time, never at runtime.

- Helm charts MUST pass `helm lint` and `helm template` validation in CI
- Container images MUST pass vulnerability scanning before deployment
- Kubernetes manifests MUST pass policy validation (OPA/Gatekeeper or equivalent)
- Startup probes MUST fail fast if critical dependencies are unavailable
- Schema validation MUST be enforced for all ConfigMap and Secret structures

**Rationale**: Every error caught before production is an incident prevented. Fail-fast
reduces mean time to detection (MTTD) to zero for preventable issues.

## Infrastructure Rules

### Cluster Requirements

| Component | Specification |
|-----------|---------------|
| Runtime | Minikube 1.32+ or Docker Desktop Kubernetes |
| Kubernetes | v1.28+ |
| Container Runtime | containerd or Docker |
| CPU | Minimum 4 cores allocated to cluster |
| Memory | Minimum 8GB allocated to cluster |
| Storage | 20GB available for images and PVCs |

### Namespace Strategy

- `todo-dev`: Development deployments (default)
- `todo-staging`: Pre-production validation
- `todo-prod`: Production workloads (local simulation)
- `todo-system`: Infrastructure components (ingress, monitoring)

### Resource Quotas

All namespaces MUST have ResourceQuotas defined to prevent runaway resource consumption.

## Environment Variable Governance

### Classification

| Tier | Examples | Handling |
|------|----------|----------|
| **Public** | `NODE_ENV`, `LOG_LEVEL` | ConfigMap, committed to repo |
| **Sensitive** | `DATABASE_URL`, `OPENAI_API_KEY` | Kubernetes Secret, never committed |
| **Runtime** | `POD_NAME`, `POD_IP` | Downward API injection |

### Naming Convention

- Prefix with service name: `BACKEND_DATABASE_URL`, `FRONTEND_API_URL`
- Use SCREAMING_SNAKE_CASE exclusively
- Document all variables in a `env.example` file per service

### Injection Hierarchy

1. Kubernetes Secrets (highest precedence)
2. Kubernetes ConfigMaps
3. Container image defaults (lowest precedence, discouraged)

## Containerization Standards

### Dockerfile Requirements

- MUST use multi-stage builds to minimize image size
- MUST run as non-root user (UID 1000+)
- MUST define explicit `HEALTHCHECK` instruction
- MUST pin base image to SHA digest
- MUST NOT include development dependencies in final stage
- MUST use `.dockerignore` to exclude unnecessary files

### Image Tagging

- Development: `<service>:dev-<short-sha>`
- Release: `<service>:v<semver>` (e.g., `backend:v1.2.3`)
- Never use `:latest` outside of local development

### Image Registry

- Local development: Minikube's built-in registry or `eval $(minikube docker-env)`
- Production path: Container registry (GitHub Container Registry, ECR, GCR)

## Kubernetes Standards

### Resource Definitions

All Deployments MUST define:

- `resources.requests` (guaranteed allocation)
- `resources.limits` (maximum allowed)
- `livenessProbe` (is the process alive?)
- `readinessProbe` (can it serve traffic?)
- `startupProbe` (for slow-starting containers)

### Pod Disruption Budgets

Services with replicas > 1 MUST define PodDisruptionBudgets to ensure availability
during node maintenance.

### Network Policies

Network segmentation MUST be enforced:

- Frontend pods: ingress from ingress controller only
- Backend pods: ingress from frontend pods only
- Database pods: ingress from backend pods only

## Helm Governance

### Chart Structure

```
charts/
├── todo-frontend/
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── values-dev.yaml
│   ├── values-staging.yaml
│   └── templates/
├── todo-backend/
│   └── ...
└── todo-infrastructure/
    └── ...
```

### Versioning

- Chart version: Incremented on any template change
- App version: Matches the container image version being deployed
- Breaking changes: MAJOR version bump, documented in CHANGELOG

### Dependencies

- Subchart dependencies MUST be pinned to specific versions
- `helm dependency update` MUST be run in CI before packaging

## AI DevOps Policy

### Approved Tools

| Tool | Purpose | Approval Level |
|------|---------|----------------|
| `kubectl-ai` | Natural language K8s queries | Self-service |
| `kagent` | Automated cluster operations | Requires review |
| `helm` | Standard deployments | Self-service |

### Guardrails

- AI-generated `delete` commands require explicit confirmation
- AI cannot modify RBAC, NetworkPolicies, or Secrets directly
- All AI operations MUST be logged with prompt and response
- AI suggestions that violate this constitution MUST be rejected

## Security Standards

### RBAC

- Principle of least privilege: Services get only required permissions
- No cluster-admin bindings in application namespaces
- ServiceAccounts MUST be explicitly created (no default SA usage)

### Pod Security

- Pods MUST run as non-root
- Pods MUST have read-only root filesystem where possible
- Privileged containers are prohibited
- Host networking/PID/IPC namespaces are prohibited

### Secret Management

- Secrets MUST be encrypted at rest (Kubernetes EncryptionConfiguration)
- Secret access MUST be audited via Kubernetes audit logs
- External secret operators (e.g., External Secrets Operator) are preferred
  for production

## Scalability Standards

### Horizontal Pod Autoscaling

- HPA MUST be configured for stateless services
- Scale triggers: CPU > 70%, Memory > 80%, or custom metrics
- Minimum replicas: 2 for production-like environments
- Maximum replicas: Defined per service based on resource quotas

### Vertical Scaling

- VPA (Vertical Pod Autoscaler) MAY be used in recommendation mode
- VPA auto-apply is prohibited without extensive testing

### Database Scaling

- Neon PostgreSQL is managed externally; connection pooling is REQUIRED
- Backend MUST use connection pools with explicit limits

## Observability & Debugging Policy

### Logging

- Format: JSON with fields `timestamp`, `level`, `service`, `message`, `trace_id`
- Aggregation: Logs forwarded to stdout, collected by cluster logging stack
- Retention: 7 days for dev, 30 days for staging/prod simulation

### Metrics

- Exposition: Prometheus format on `:9090/metrics` or service-specific port
- Collection: Prometheus scrape via ServiceMonitor CRDs
- Dashboards: Grafana dashboards deployed via Helm

### Tracing

- Protocol: OpenTelemetry (OTLP)
- Sampling: 100% in dev, 10% in prod simulation
- Visualization: Jaeger or Tempo

### Debugging Workflow

1. Check pod status: `kubectl get pods -n <namespace>`
2. Check logs: `kubectl logs -f <pod> -n <namespace>`
3. Check events: `kubectl describe pod <pod> -n <namespace>`
4. Attach debug container: `kubectl debug -it <pod> --image=busybox`
5. NEVER modify running containers directly

## Non-Goals

The following are explicitly OUT OF SCOPE for Phase IV:

- Multi-cluster federation
- Service mesh (Istio/Linkerd) — evaluate in Phase V
- GitOps (ArgoCD/Flux) — evaluate in Phase V
- Cloud-managed Kubernetes (EKS/GKE/AKS) — Phase IV is local only
- Production traffic handling — this is a development/learning environment
- High availability beyond local simulation
- Disaster recovery procedures

## Acceptance Definition

Phase IV is considered complete when:

- [ ] All services (frontend, backend) have production-ready Dockerfiles
- [ ] Helm charts exist for all services with dev/staging/prod values
- [ ] `helm install` brings up the complete system in under 5 minutes
- [ ] All secrets are injected via Kubernetes Secrets (none hardcoded)
- [ ] Health checks pass for all pods within 60 seconds of deployment
- [ ] Prometheus metrics are exposed and scrapeable
- [ ] Logs are structured JSON and visible via `kubectl logs`
- [ ] `helm upgrade --atomic` successfully updates running deployments
- [ ] `helm rollback` successfully reverts to previous release
- [ ] Resource requests/limits are defined for all containers
- [ ] No manual YAML exists outside of Helm templates
- [ ] AI tooling (kubectl-ai) can query cluster state successfully

## Governance

### Amendment Process

1. Propose change via PR with rationale
2. Review by at least one other team member
3. Update version according to SemVer rules
4. Document change in Sync Impact Report
5. Propagate changes to dependent templates

### Compliance Verification

- All PRs MUST include a Constitution Check in the plan
- Violations MUST be justified in the Complexity Tracking table
- Unjustified violations block merge

### Version Policy

- MAJOR: Principle removal or fundamental redefinition
- MINOR: New principle or section added
- PATCH: Clarification or typo fix

**Version**: 1.0.0 | **Ratified**: 2025-02-07 | **Last Amended**: 2025-02-07
