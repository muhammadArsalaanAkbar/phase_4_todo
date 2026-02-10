---
id: 001
title: Phase 5 Microservices Spec Creation
stage: spec
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: 002-microservices-dapr-kafka
branch: 002-microservices-dapr-kafka
user: architect
command: /sp.specify
labels: ["phase-v", "microservices", "dapr", "kafka", "spec", "todo-service", "audit", "websocket", "notification", "recurring-task"]
links:
  spec: specs/002-microservices-dapr-kafka/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-microservices-dapr-kafka/spec.md
  - specs/002-microservices-dapr-kafka/checklists/requirements.md
  - history/prompts/002-microservices-dapr-kafka/001-phase5-microservices-spec-creation.spec.prompt.md
tests:
  - null
---

## Prompt

# speckit.specify - Phase 5 Todo AI

## Project Context
- Phase 5 extends the existing Phase 4 Todo AI project.
- Phase 4 code is **reference only** and **must not be modified**.
- Phase 5 introduces:
  - Microservices: Todo, Notification, Recurring Task, Audit, WebSocket
  - Event-driven architecture using Kafka / Redpanda Cloud
  - Dapr integration: Pub/Sub, State, Jobs API, Secrets
  - Local deployment (Minikube) and Cloud deployment (AKS / GKE)
  - CI/CD pipelines

## User Stories / Journeys

### 1. Todo Service
- **As a user**, I want to create, update, delete, and complete tasks.
- **Phase 5 Enhancement**: Reuse Phase 4 CRUD backend logic. Publish task events to Kafka via Dapr Pub/Sub.

### 2. Notification Service
- **As a user**, I want to receive notifications for task reminders.
- **Phase 5 Enhancement**: Subscribe to `reminders` topic. Send push/email notifications via Dapr Pub/Sub.

### 3. Recurring Task Service
- **As a user**, I want recurring tasks to auto-generate after completion.
- **Phase 5 Enhancement**: Subscribe to `task-events` topic. Auto-create next task occurrence via Dapr Jobs API.

### 4. Audit Service
- **As an admin**, I want a complete history of task operations.
- **Phase 5 Enhancement**: Subscribe to `task-events`. Store operations in PostgreSQL (Neon DB).

### 5. WebSocket Service
- **As a user**, I want real-time updates across all connected clients.
- **Phase 5 Enhancement**: Subscribe to `task-updates` topic. Broadcast changes via WebSocket service.

## Requirements

### Functional
1. Phase 4 CRUD logic must be imported, never modified.
2. Event-driven architecture using Kafka / Redpanda Cloud.
3. Dapr integration: Pub/Sub, State, Jobs API, Secrets.
4. Microservices must be independent and deployable.
5. Local deployment using Minikube; Cloud deployment on AKS / GKE.

### Technical
1. PostgreSQL (Neon DB) for persistent storage.
2. Unit and integration tests for all services.
3. CI/CD pipeline using GitHub Actions.
4. All services containerized via Docker.

### Deployment
1. Minikube YAMLs under `k8s/deployments/`.
2. Dapr components under `k8s/dapr-components/`.
3. Phase 4 frontend is reference only.

## Domain Rules
1. No direct modification of Phase 4 code.
2. All new code must reference Task IDs in comments.
3. Microservices communicate only via Dapr sidecars.
4. Kafka topics: task-events, reminders, task-updates.

## Acceptance Criteria
- Todo Service performs CRUD and publishes events.
- Notification Service triggers notifications at correct time.
- Recurring Task Service auto-generates tasks correctly.
- Audit Service stores complete history.
- WebSocket Service broadcasts real-time updates.
- Minikube deployment runs all services without errors.
- CI/CD pipeline successfully builds, tests, and deploys.

## Phase 4 References
- Backend CRUD logic: `backend/todo_logic.py`
- DB schema: `backend/schema.sql`
- Frontend components: `frontend/`

## Response snapshot

Created Phase 5 feature spec on branch `002-microservices-dapr-kafka` with 5 prioritized user stories:

- **P1**: Task CRUD with Event Publishing (Todo Service) — core domain, all services depend on it
- **P2**: Audit Trail (Audit Service) — simplest event consumer, validates pipeline
- **P3**: Real-Time Updates (WebSocket Service) — high UX value, validates `task-updates` topic
- **P4**: Reminder Notifications (Notification Service) — validates `reminders` topic
- **P5**: Recurring Task Auto-Generation (Recurring Task Service) — most complex, Dapr Jobs API

Key decisions:
- 15 functional requirements, all testable
- 5 key entities defined (Task, TaskEvent, AuditRecord, RecurrenceSchedule, Notification)
- 10 measurable success criteria with specific thresholds
- 5 edge cases covering Dapr/Kafka failure modes and idempotency
- Critical assumption documented: Phase 4 has no backend source code — "reuse" means reimplementation
- Auth out of scope for MVP
- In-app notification only for MVP (email/push deferred)

Quality checklist: ALL items pass. Zero NEEDS CLARIFICATION markers.

## Outcome

- ✅ Impact: Feature spec ready for /sp.plan (architecture planning)
- 🧪 Tests: N/A — specification document, no code
- 📁 Files: spec.md (created), checklists/requirements.md (created)
- 🔁 Next prompts: /sp.plan for architecture, then /sp.tasks for task generation
- 🧠 Reflection: User's Phase 4 references (backend/todo_logic.py, backend/schema.sql) do not exist as source code. Phase 4 only has Docker/Helm/K8s infrastructure. This was documented as an assumption rather than flagged as NEEDS CLARIFICATION because the implication is clear: reimplement in Python/FastAPI.

## Evaluation notes (flywheel)

- Failure modes observed: PowerShell script partially failed on prompts directory creation (worked around manually)
- Graders run and results (PASS/FAIL): Quality checklist PASS (all 16 items checked)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider splitting into multiple feature specs (one per service) if the plan phase reveals too much complexity
