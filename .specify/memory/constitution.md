<!--
================================================================================
SYNC IMPACT REPORT
================================================================================
Version Change: 1.0.0 → 2.0.0 (MAJOR - complete Phase V redefinition)

Modified Principles:
  - I. Container-First Architecture → I. Spec-Driven Development (redefined)
  - II. No Manual YAML → II. Dapr-Mediated Communication (redefined)
  - III. Secrets Governance → III. Event-Driven Architecture (redefined)
  - IV. Helm-Managed Deployments → IV. Microservices Isolation (redefined)
  - V. AI-Assisted DevOps → V. Secrets Governance (redefined)
  - VI. Observability by Default → VI. Phase 4 Immutability (new)
  - VII. Immutable Infrastructure → VII. Container-First Deployment (redefined)
  - VIII. Fail-Fast Validation → VIII. Fail-Fast Validation (redefined)
  - (new) → IX. Observability & Traceability (new)

Added Sections:
  - Technology Stack Constraints
  - Kafka / Event Rules
  - Dapr Rules
  - Deployment & CI/CD
  - Failure Modes / Restrictions

Removed Sections:
  - Infrastructure Rules (replaced by Technology Stack Constraints)
  - Environment Variable Governance (subsumed by Dapr Secrets)
  - Containerization Standards (simplified into Container-First Deployment)
  - Kubernetes Standards (subsumed by Deployment & CI/CD)
  - Helm Governance (no longer exclusive mechanism; Dapr replaces)
  - AI DevOps Policy (removed; AI agents governed by Spec-Driven principle)
  - Scalability Standards (deferred to feature specs)
  - Non-Goals (replaced by Failure Modes / Restrictions)

Templates Requiring Updates:
  ✅ plan-template.md - Constitution Check section compatible (generic gates)
  ✅ spec-template.md - Requirements section compatible (generic structure)
  ✅ tasks-template.md - Phase structure compatible (generic phases)

Follow-up TODOs: None
================================================================================
-->

# AI-Native Todo Chatbot Constitution — Phase V

## Vision

Phase V transforms the AI-Native Todo Chatbot from a monolithic Kubernetes
workload into a **distributed, event-driven microservices platform**. This phase
introduces Dapr as the distributed runtime, Kafka as the event backbone, and
decomposes the application into five purpose-built microservices. Phase 4 code
serves as reference only — all new implementation is Python/FastAPI.

**North Star**: Every microservice MUST communicate exclusively through Dapr
sidecars. No service may directly call another service's API or directly access
Kafka or PostgreSQL. All development MUST be spec-driven with traceable Task IDs.

## Core Principles

### I. Spec-Driven Development

No agent or developer MAY write code without an assigned Task ID. All code
MUST be traceable to a specification artifact.

- Every code file MUST reference its Phase 5 Task ID in comments
- No feature improvisation is permitted; missing requirements MUST trigger
  a clarification request, not assumptions
- Tasks MUST be atomic and testable with explicit preconditions, outputs,
  and artifacts
- The workflow is: Spec → Plan → Tasks → Implement → Validate

**Rationale**: Spec-driven development eliminates scope creep, ensures
traceability, and enables any agent or developer to pick up work with full
context. Ungoverned code is untraceable code.

### II. Dapr-Mediated Communication

All inter-service communication MUST flow through Dapr sidecars. Direct
service-to-service API calls are prohibited.

- **Pub/Sub**: Event-driven messaging between microservices
- **State**: Conversation and task cache management
- **Jobs API**: Recurring tasks and scheduled reminders
- **Secrets API**: API keys, database credentials, and sensitive configuration
- Microservices MUST NOT access Kafka or PostgreSQL directly; all access
  MUST go through Dapr building blocks

**Rationale**: Dapr provides a portable, vendor-neutral abstraction layer.
Services remain decoupled from infrastructure, enabling migration between
Kafka providers (Redpanda, Confluent, Strimzi) or databases without code
changes.

### III. Event-Driven Architecture

All cross-service data flow MUST use Kafka topics via Dapr Pub/Sub. Synchronous
request-response patterns between services are prohibited except for health
checks.

- Kafka topics:
  - `task-events` → Todo CRUD events
  - `reminders` → Scheduled reminder notifications
  - `task-updates` → Real-time sync via WebSocket
- Event schemas MUST follow the standardized format defined in the Phase 5
  feature plan
- Microservices MUST publish and subscribe exclusively via Dapr Pub/Sub
- Events MUST be idempotent; consumers MUST handle duplicate delivery

**Rationale**: Event-driven architecture enables loose coupling, temporal
decoupling, and natural audit trails. Kafka provides durable, ordered event
streams that serve as the system's source of truth for state transitions.

### IV. Microservices Isolation

The system MUST be decomposed into five independently deployable microservices.
Each service owns its domain and MUST NOT share databases or internal state
with other services.

- **Todo Service**: CRUD operations for tasks and task lifecycle management
- **Notification Service**: Email, push, and in-app notification delivery
- **Recurring Task Service**: Scheduled task generation via Dapr Jobs API
- **Audit Service**: Event logging and compliance trail
- **WebSocket Service**: Real-time client updates via `task-updates` topic

Each service MUST:
- Have its own Dockerfile and container image
- Be independently deployable without affecting other services
- Communicate only through Dapr sidecars (Principle II)
- Own its data; no shared database tables across services

**Rationale**: Service isolation enables independent scaling, deployment, and
failure containment. A bug in the Notification Service MUST NOT cascade to
Todo Service availability.

### V. Secrets Governance

Secrets MUST NEVER be hardcoded in source code, container images, configuration
files, or any artifact tracked in version control.

- All secrets MUST be managed via Dapr Secrets API or Kubernetes Secrets
- `.env` files are permitted for local development ONLY and MUST be gitignored
- API keys (OpenAI, etc.), database credentials, and JWT secrets are
  explicitly covered
- Secret rotation MUST be possible without rebuilding images or redeploying
  services

**Rationale**: Hardcoded secrets are a critical security vulnerability. Dapr
Secrets API provides a unified, provider-agnostic interface for secret
management across local (file) and cloud (Azure Key Vault, AWS Secrets Manager)
environments.

### VI. Phase 4 Immutability

Phase 4 code is reference only. No agent or developer MAY modify Phase 4
source code, configuration, or deployment artifacts.

- Phase 4 frontend serves as UI reference; Phase 5 does not modify it
- Phase 4 backend serves as API reference; Phase 5 reimplements in Python
- Phase 4 Helm charts, Dockerfiles, and K8s manifests MUST NOT be altered
- Phase 5 code MUST live in its own directory structure, separate from
  Phase 4 artifacts

**Rationale**: Phase 4 represents a stable, validated baseline. Modifying it
risks breaking proven infrastructure and conflates two distinct architectural
paradigms (monolith vs. microservices).

### VII. Container-First Deployment

Every microservice MUST run inside a container. Local deployment uses Minikube;
cloud deployment targets AKS or GKE.

- All services MUST have production-ready Dockerfiles
- Local development MUST use Minikube with the same container images
- Cloud deployment (AKS/GKE) MUST mirror the Minikube configuration
- Images MUST be tagged with SemVer; `:latest` is prohibited outside local
  development

**Rationale**: Container-first ensures environment parity between local and
cloud. Minikube-first development catches deployment issues early, before
they reach shared environments.

### VIII. Fail-Fast Validation

Misconfigurations MUST be caught at build time or deploy time, never at runtime.
GitHub Actions enforces the CI/CD pipeline.

- GitHub Actions MUST build Docker images for all services
- GitHub Actions MUST run unit and integration tests before deployment
- GitHub Actions MUST deploy to Minikube (CI) and cloud cluster (CD)
- Container images MUST pass vulnerability scanning before deployment
- Startup probes MUST fail fast if critical dependencies (Dapr, Kafka,
  PostgreSQL) are unavailable

**Rationale**: Every error caught before production is an incident prevented.
Automated CI/CD eliminates human error in the build-test-deploy cycle.

### IX. Observability & Traceability

Every deployed component MUST emit structured logs that include Task ID
references for end-to-end traceability.

- Logs MUST be JSON-formatted and written to stdout/stderr
- All log entries MUST include a `task_id` field linking to the originating
  Phase 5 Task ID
- All inter-service communication MUST support TLS or mTLS where possible
- Health checks (liveness, readiness) MUST be defined for all containers

**Rationale**: Traceability from spec to runtime is the core promise of
spec-driven development. Without Task ID correlation in logs, debugging
distributed microservices becomes guesswork.

## Technology Stack Constraints

| Component | Specification |
|-----------|---------------|
| Backend Language | Python (FastAPI / Async) |
| Frontend | Phase 4 UI (reference only, no modification) |
| Database | PostgreSQL (Neon DB) |
| Event Messaging | Kafka (Redpanda Cloud or Strimzi self-hosted) |
| Distributed Runtime | Dapr (Pub/Sub, State, Jobs, Secrets) |
| Local Deployment | Minikube |
| Cloud Deployment | AKS / GKE |
| Containerization | Docker |
| CI/CD | GitHub Actions |

### Microservices

| Service | Responsibility |
|---------|---------------|
| Todo Service | Task CRUD and lifecycle management |
| Notification Service | Email, push, in-app notifications |
| Recurring Task Service | Scheduled task generation (Dapr Jobs) |
| Audit Service | Event logging and compliance trail |
| WebSocket Service | Real-time client sync via `task-updates` |

## Kafka / Event Rules

### Topic Definitions

| Topic | Purpose | Producers | Consumers |
|-------|---------|-----------|-----------|
| `task-events` | Todo CRUD events | Todo Service | Audit, Notification |
| `reminders` | Scheduled reminders | Recurring Task Service | Notification |
| `task-updates` | Real-time sync | Todo Service | WebSocket Service |

### Event Governance

- All events MUST be published/subscribed via Dapr Pub/Sub components
- Event schemas MUST follow the standardized format in the Phase 5 plan
- Events MUST be idempotent; consumers MUST handle duplicate delivery
- New topics require explicit specification before implementation

## Dapr Rules

### Building Block Usage

| Building Block | Purpose | Services |
|----------------|---------|----------|
| Pub/Sub | Event-driven messaging | All services |
| State | Conversation/task cache | Todo, WebSocket |
| Jobs API | Recurring tasks, reminders | Recurring Task Service |
| Secrets API | API keys, DB credentials | All services |

### Constraints

- Microservices MUST NOT bypass Dapr to access Kafka directly
- Microservices MUST NOT bypass Dapr to access PostgreSQL directly
- Dapr component definitions MUST be version-controlled
- Local Dapr configuration MUST mirror cloud configuration

## Deployment & CI/CD

### Environment Strategy

| Environment | Platform | Purpose |
|-------------|----------|---------|
| Local Dev | Minikube | Development and testing |
| CI | Minikube (GitHub Actions) | Automated validation |
| Cloud | AKS / GKE | Production deployment |

### CI/CD Pipeline Requirements

- GitHub Actions MUST build Docker images for all 5 microservices
- GitHub Actions MUST run unit and integration tests
- GitHub Actions MUST deploy to Minikube for CI validation
- Cloud deployment MUST mirror the Minikube setup exactly
- Pipeline failures MUST block deployment

## Security Standards

### Secrets

- Secrets MUST NEVER be hardcoded; use Dapr Secrets API or K8s Secrets
- All inter-service communication MUST support TLS or mTLS where possible
- `.env` files MUST be gitignored; `env.example` files document required vars

### Pod Security

- Pods MUST run as non-root
- Privileged containers are prohibited
- ServiceAccounts MUST be explicitly created (no default SA usage)

## Failure Modes / Restrictions

The following are **hard restrictions** that agents and developers MUST NOT
violate under any circumstances:

- Agents **MUST NOT** modify Phase 4 code (Principle VI)
- Agents **MUST NOT** generate code without a Task ID reference (Principle I)
- Agents **MUST NOT** bypass Dapr for inter-service communication or event
  publishing (Principle II)
- Agents **MUST NOT** access Kafka or PostgreSQL directly; all access MUST go
  through Dapr (Principle II)
- Any missing specification MUST trigger a clarification request; agents
  MUST NOT improvise features (Principle I)

## Acceptance Definition

Phase V is considered complete when:

- [ ] All 5 microservices have production-ready Dockerfiles
- [ ] All services communicate exclusively via Dapr sidecars
- [ ] Kafka topics (task-events, reminders, task-updates) are operational
- [ ] Dapr Pub/Sub, State, Jobs, and Secrets building blocks are configured
- [ ] All secrets are managed via Dapr Secrets API (none hardcoded)
- [ ] Health checks pass for all pods within 60 seconds of deployment
- [ ] Logs are structured JSON with Task ID references
- [ ] GitHub Actions CI/CD pipeline builds, tests, and deploys all services
- [ ] Minikube hosts all services locally
- [ ] Cloud deployment (AKS/GKE) mirrors Minikube configuration
- [ ] No Phase 4 code has been modified
- [ ] All code references traceable Phase 5 Task IDs

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

**Version**: 2.0.0 | **Ratified**: 2025-02-07 | **Last Amended**: 2026-02-08
