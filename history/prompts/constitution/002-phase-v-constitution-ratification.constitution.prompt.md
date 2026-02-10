---
id: 002
title: Phase V Constitution Ratification
stage: constitution
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: none
branch: master
user: architect
command: /sp.constitution
labels: ["phase-v", "microservices", "dapr", "kafka", "constitution"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - null
---

## Prompt

# speckit.constitution - Phase 5 Todo AI

## Purpose
This file defines **non-negotiable rules, standards, and constraints** for Phase 5 development.
All agents (Claude, Copilot, etc.) must follow this **before proposing architecture, writing tasks, or generating code**.

---

## Technology Stack Constraints
1. **Phase 4 code is reference only**. It must not be modified.
2. **Backend language**: Python (FastAPI / Async)
3. **Frontend**: Phase 4 UI reference only; no modification allowed
4. **Database**: PostgreSQL (Neon DB)
5. **Microservices**:
   - Todo Service
   - Notification Service
   - Recurring Task Service
   - Audit Service
   - WebSocket Service
6. **Event-driven messaging**: Kafka (Redpanda Cloud or Strimzi self-hosted)
7. **Distributed runtime**: Dapr (Pub/Sub, State, Jobs, Secrets)
8. **Local deployment**: Minikube
9. **Cloud deployment**: AKS / GKE
10. **Containerization**: Docker

---

## Coding & Architecture Principles
1. **No agent may write code without a Task ID**.
2. **All new code must reference Phase 5 Task IDs in comments**.
3. **Microservices must communicate only via Dapr sidecars**; no direct API calls.
4. **Tightly coupled code is prohibited**. Use Dapr abstraction for Kafka, state, jobs, secrets.
5. **Atomic, testable tasks only**. Each task must have precondition, output, and artifacts.
6. **No feature improvisation**. If a requirement is missing, agents must ask for clarification.

---

## Kafka / Event Rules
1. Kafka topics:
   - `task-events` → Todo CRUD events
   - `reminders` → Scheduled reminder notifications
   - `task-updates` → Real-time sync via WebSocket
2. Microservices can only **publish/subscribe via Dapr**.
3. Event schema must follow the **standardized format** defined in Phase 5 plan.

---

## Dapr Rules
1. **Pub/Sub** for event-driven messaging
2. **State** for conversation/task cache
3. **Jobs API** for recurring tasks and scheduled reminders
4. **Secrets API** for storing API keys and DB credentials
5. Microservices **must not access Kafka/Postgres directly**.

---

## Deployment & CI/CD
1. Minikube must host all services locally first.
2. Cloud deployment (AKS / GKE) must mirror Minikube setup.
3. GitHub Actions must:
   - Build Docker images
   - Run unit & integration tests
   - Deploy to Minikube / Cloud cluster

---

## Security & Standards
1. Secrets must **never be hardcoded**; use Dapr or Kubernetes Secrets.
2. All inter-service communication must support **TLS or mTLS** where possible.
3. All logs must include **Task ID** reference for traceability.

---

## Failure Modes / Restrictions
- Agents **cannot modify Phase 4 code**.
- Agents **cannot generate code without task reference**.
- Agents **cannot bypass Dapr for communication or events**.
- Any missing specification → request clarification instead of improvising.

---

## Summary
- **Phase 5 is spec-driven**. No freestyle coding.
- **Dapr + Kafka + Microservices** are the backbone.
- **Phase 4 code is only reference**, no direct edits.
- **All agents must follow this constitution** strictly before generating plan, tasks, or implementation code.

## Response snapshot

Ratified Phase V Constitution v2.0.0 (MAJOR bump from v1.0.0). Replaced all 8 Phase IV K8s-focused principles with 9 Phase V microservices/Dapr/Kafka principles:

1. **Spec-Driven Development** - No code without Task ID, no feature improvisation
2. **Dapr-Mediated Communication** - All inter-service communication via Dapr sidecars
3. **Event-Driven Architecture** - Kafka topics (task-events, reminders, task-updates) via Dapr Pub/Sub
4. **Microservices Isolation** - 5 independently deployable services with domain ownership
5. **Secrets Governance** - Dapr Secrets API / K8s Secrets, never hardcoded
6. **Phase 4 Immutability** - Phase 4 code is reference only, no modifications
7. **Container-First Deployment** - Docker + Minikube + AKS/GKE
8. **Fail-Fast Validation** - GitHub Actions CI/CD pipeline enforcement
9. **Observability & Traceability** - JSON logs with Task ID references

Added sections: Technology Stack Constraints, Kafka/Event Rules, Dapr Rules, Deployment & CI/CD, Failure Modes/Restrictions. All templates validated as compatible.

## Outcome

- ✅ Impact: Established Phase V governance foundation for microservices architecture
- 🧪 Tests: N/A - Governance document, no code
- 📁 Files: .specify/memory/constitution.md (updated v1.0.0 → v2.0.0)
- 🔁 Next prompts: /sp.specify for first Phase V feature spec, /sp.plan for implementation planning
- 🧠 Reflection: MAJOR version bump justified — complete architectural paradigm shift from monolith K8s to distributed microservices with Dapr+Kafka. All user-specified constraints captured. Templates are generic enough to require no updates.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual review PASS - all sections present, no unresolved placeholders, all user constraints captured
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider ADR for Dapr adoption decision when /sp.plan is run
