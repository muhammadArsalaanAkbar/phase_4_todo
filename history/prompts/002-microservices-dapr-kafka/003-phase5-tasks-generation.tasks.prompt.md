---
id: 003
title: Phase 5 Tasks Generation
stage: tasks
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: 002-microservices-dapr-kafka
branch: 002-microservices-dapr-kafka
user: architect
command: /sp.tasks
labels: ["phase-v", "tasks", "microservices", "dapr", "kafka", "implementation-plan"]
links:
  spec: specs/002-microservices-dapr-kafka/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-microservices-dapr-kafka/tasks.md
tests:
  - null
---

## Prompt

# speckit.tasks - Phase 5 Todo AI

Use this speckit.tasks to implement Phase 5 microservices in order. Reference Task IDs in all code comments. Follow speckit.plan architecture strictly. Do not modify Phase 4 code.

## Draft Tasks Provided

T-001: Set up FastAPI project structure for todo-service
T-002: Implement Pydantic models matching Phase 4 schema
T-003: Build CRUD endpoints reusing Phase 4 todo_logic
T-004: Add Dapr pub/sub publishing on task events
T-005: Unit tests for todo-service

N-001: Set up FastAPI project for notification-service
N-002: Subscribe to reminders topic via Dapr
N-003: Implement in-app notification delivery
N-004: Unit tests for notification-service

R-001: Set up FastAPI project for recurring-task-service
R-002: Implement recurrence detection using Dapr Jobs API
R-003: Subscribe to task-events for completed tasks
R-004: Unit tests for recurring-task-service

A-001: Set up FastAPI project for audit-service
A-002: Subscribe to task-events topic
A-003: Store audit records in PostgreSQL
A-004: Implement audit query API
A-005: Unit tests for audit-service

W-001: Set up FastAPI for websocket-service
W-002: Subscribe to task-updates topic
W-003: Implement WebSocket broadcast
W-004: Unit tests for websocket-service

D-001: Write Dockerfiles for all services
D-002: Create K8s deployment manifests with Dapr annotations
D-003: Create GitHub Actions CI/CD pipeline

## Response snapshot

Generated comprehensive tasks.md with 79 tasks across 9 phases, correcting and expanding the user's draft of ~22 tasks. Key corrections applied:

**Issues identified in draft tasks:**
1. Wrong file paths — draft used `phase5/` instead of `services/` per plan.md
2. Reference to non-existent `backend/todo_logic.py` — Phase 4 has no backend source code
3. R-002 references Dapr Jobs API — research.md confirms no Python SDK, using APScheduler
4. Too few tasks — 22 draft tasks insufficient for 5 services + shared library + infra
5. Missing Setup (Phase 1) and Foundational (Phase 2) phases
6. Not using required checklist format from tasks template

**Generated 79 tasks across 9 phases:**
- Phase 1: Setup (T001-T012, 12 tasks) — monorepo structure, shared library, K8s infra
- Phase 2: Foundational (T013-T029, 17 tasks) — DB sessions, migrations, base FastAPI apps
- Phase 3: US1 Todo CRUD+Events (T030-T037, 8 tasks) — CRUD API, event publishing
- Phase 4: US2 Audit Trail (T038-T045, 8 tasks) — subscribe task-events, audit records
- Phase 5: US3 WebSocket (T046-T049, 4 tasks) — subscribe task-updates, broadcast
- Phase 6: US4 Notifications (T050-T057, 8 tasks) — subscribe reminders, delivery
- Phase 7: US5 Recurring Tasks (T058-T067, 10 tasks) — APScheduler, recurrence detection
- Phase 8: Deployment & CI/CD (T068-T074, 7 tasks) — Dockerfiles, K8s manifests, GitHub Actions
- Phase 9: Polish & Validation (T075-T079, 5 tasks) — integration tests, end-to-end validation

**Validation results (all PASS):**
- User story coverage: 5/5 user stories covered
- FR coverage: 15/15 functional requirements mapped
- File paths: All match plan.md project structure
- Task sequencing: 79 IDs sequential and unique (T001-T079)
- Parallel markers: All [P] markers valid (no conflicting dependencies)
- Dependencies: Phase ordering correct, blocking prerequisites enforced

## Outcome

- ✅ Impact: 79 actionable implementation tasks ready for Phase 5 development
- 🧪 Tests: N/A — planning artifact, no code. Validation agent confirmed all checks PASS.
- 📁 Files: tasks.md
- 🔁 Next prompts: /sp.implement to begin Phase 1 task execution, /sp.adr phase5-technology-stack for ADR
- 🧠 Reflection: User's draft needed significant correction — wrong paths, non-existent file references, and Dapr Jobs API assumption contradicted by research. Expanding from 22 to 79 tasks with proper phasing ensures granular implementation. The shared library (Phase 1-2) is the critical foundation that gates all service work.

## Evaluation notes (flywheel)

- Failure modes observed: User draft referenced non-existent Phase 4 backend code and unavailable Dapr Jobs API — both caught by cross-referencing plan.md and research.md
- Graders run and results (PASS/FAIL): Validation agent PASS — user story coverage 5/5, FR coverage 15/15, file paths valid, sequencing correct, parallel markers valid, dependencies correct
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider auto-generating GitHub Issues from tasks.md using /sp.taskstoissues for better project tracking
