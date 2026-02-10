# Tasks: Phase 5 Microservices Platform

**Input**: Design documents from `/specs/002-microservices-dapr-kafka/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Unit and integration tests are included as they are explicitly required in spec.md (FR: "Unit and integration tests for all services").

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Monorepo**: `services/<service-name>/app/` for application code
- **Shared**: `services/shared/shared/` for shared library
- **K8s**: `k8s/deployments/` and `k8s/dapr-components/` for infra
- **CI/CD**: `.github/workflows/` for pipeline

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, shared library, and infrastructure scaffolding

- [x] T001 Create monorepo directory structure per plan.md (`services/shared/`, `services/todo-service/`, `services/audit-service/`, `services/websocket-service/`, `services/notification-service/`, `services/recurring-task-service/`, `k8s/deployments/`, `k8s/dapr-components/`, `k8s/secrets/`)
- [x] T002 [P] Create shared library `services/shared/pyproject.toml` with package metadata and dependencies (pydantic v2, dapr, python-json-logger)
- [x] T003 [P] Create shared event schema definitions in `services/shared/shared/events.py` — Pydantic models for TaskEvent and ReminderEvent per data-model.md
- [x] T004 [P] Create shared Dapr client helpers in `services/shared/shared/dapr_helpers.py` — publish_event wrapper using DaprClient with CloudEvents metadata
- [x] T005 [P] Create shared structured JSON logger in `services/shared/shared/logging.py` — JSON formatter with task_id field per FR-012
- [x] T006 [P] Create shared base config in `services/shared/shared/config.py` — Pydantic Settings for DAPR_HTTP_PORT, DATABASE_URL, SERVICE_NAME
- [x] T007 [P] Create shared health check router in `services/shared/shared/health.py` — FastAPI router with `/health` and `/health/ready` endpoints per FR-013
- [x] T008 [P] Create Redpanda single-node deployment YAML in `k8s/deployments/redpanda.yaml` — Deployment + Service with `--memory=1G --smp=1` per research.md
- [x] T009 [P] Create Dapr Pub/Sub component in `k8s/dapr-components/kafka-pubsub.yaml` — pubsub.kafka pointing to redpanda:9092 per research.md
- [x] T010 [P] Create Dapr State Store component in `k8s/dapr-components/statestore.yaml` — state.postgresql v2 with secretKeyRef per research.md
- [x] T011 [P] Create Dapr Secrets component in `k8s/dapr-components/kubernetes-secrets.yaml` — secretstores.kubernetes v1 per research.md
- [x] T012 [P] Create K8s secrets script in `k8s/secrets/create-secrets.sh` — creates dapr-db-secret with Neon DB connectionString in todo-dev namespace

**Checkpoint**: Shared library installable, Dapr components defined, Redpanda manifest ready

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database sessions, migrations framework, and base FastAPI app pattern that MUST be complete before ANY user story

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T013 Create Todo Service base FastAPI app in `services/todo-service/app/main.py` — FastAPI + DaprApp setup, include shared health router, configure structured logging
- [x] T014 Create Todo Service config in `services/todo-service/app/config.py` — service-specific settings (PORT=8001, SERVICE_NAME=todo-service, DB schema=todo_service)
- [x] T015 Create Todo Service async DB session factory in `services/todo-service/app/db/session.py` — SQLAlchemy 2.0 async engine + sessionmaker using asyncpg per research.md
- [x] T016 Create Todo Service requirements.txt in `services/todo-service/requirements.txt` — fastapi, uvicorn, dapr, dapr-ext-fastapi, sqlalchemy[asyncio], asyncpg, pydantic, alembic, shared (local)
- [x] T017 Create Todo Service Dockerfile in `services/todo-service/Dockerfile` — multi-stage Python 3.11-slim, non-root user (UID 1001), healthcheck on /health port 8001, install shared lib
- [x] T018 [P] Create Audit Service base app in `services/audit-service/app/main.py` — FastAPI + DaprApp, shared health router, structured logging
- [x] T019 [P] Create Audit Service config, DB session, requirements.txt, Dockerfile (`services/audit-service/app/config.py`, `services/audit-service/app/db/session.py`, `services/audit-service/requirements.txt`, `services/audit-service/Dockerfile`) — PORT=8002, schema=audit_service
- [x] T020 [P] Create WebSocket Service base app in `services/websocket-service/app/main.py` — FastAPI + DaprApp, shared health router, structured logging
- [x] T021 [P] Create WebSocket Service config, requirements.txt, Dockerfile (`services/websocket-service/app/config.py`, `services/websocket-service/requirements.txt`, `services/websocket-service/Dockerfile`) — PORT=8003, no DB (stateless, uses Dapr State Store)
- [x] T022 [P] Create Notification Service base app in `services/notification-service/app/main.py` — FastAPI + DaprApp, shared health router, structured logging
- [x] T023 [P] Create Notification Service config, DB session, requirements.txt, Dockerfile (`services/notification-service/app/config.py`, `services/notification-service/app/db/session.py`, `services/notification-service/requirements.txt`, `services/notification-service/Dockerfile`) — PORT=8004, schema=notification_service
- [x] T024 [P] Create Recurring Task Service base app in `services/recurring-task-service/app/main.py` — FastAPI + DaprApp, shared health router, structured logging
- [x] T025 [P] Create Recurring Task Service config, DB session, requirements.txt, Dockerfile (`services/recurring-task-service/app/config.py`, `services/recurring-task-service/app/db/session.py`, `services/recurring-task-service/requirements.txt`, `services/recurring-task-service/Dockerfile`) — PORT=8005, schema=recurring_task_service, add APScheduler dependency
- [x] T026 Create Alembic migration framework for Todo Service in `services/todo-service/alembic/` — alembic.ini + async env.py targeting todo_service schema
- [x] T027 [P] Create Alembic migration framework for Audit Service in `services/audit-service/alembic/`
- [x] T028 [P] Create Alembic migration framework for Notification Service in `services/notification-service/alembic/`
- [x] T029 [P] Create Alembic migration framework for Recurring Task Service in `services/recurring-task-service/alembic/`

**Checkpoint**: All 5 services have base FastAPI apps with health endpoints, DB sessions (4 of 5), Dockerfiles, and Alembic (4 of 5). Foundation ready for user story implementation.

---

## Phase 3: User Story 1 — Task CRUD with Event Publishing (Priority: P1) MVP

**Goal**: Todo Service performs full CRUD and publishes events to `task-events` and `task-updates` topics via Dapr Pub/Sub

**Independent Test**: Deploy Todo Service + Dapr sidecar + Redpanda. CRUD via API → verify events on Kafka topics.

### Implementation for User Story 1

- [x] T030 [US1] Create Task SQLAlchemy model in `services/todo-service/app/models/task.py` — all fields from data-model.md Task entity (UUID PK, title, description, status, due_date, reminder_time, is_recurring, recurrence_schedule, created_at, updated_at)
- [x] T031 [US1] Create Alembic initial migration in `services/todo-service/alembic/versions/001_create_tasks_table.py` — tasks table with indexes (idx_tasks_status, idx_tasks_due_date, idx_tasks_is_recurring)
- [x] T032 [P] [US1] Create Task Pydantic schemas in `services/todo-service/app/schemas/task.py` — TaskCreate, TaskUpdate, TaskResponse, TaskListResponse per contracts/todo-service-api.yaml
- [x] T033 [US1] Create TaskService business logic in `services/todo-service/app/services/task_service.py` — create, get, list, update, delete, complete methods using async session; publish TaskEvent to `task-events` and `task-updates` via shared dapr_helpers after each mutation
- [x] T034 [US1] Create tasks router in `services/todo-service/app/routers/tasks.py` — REST endpoints per contracts/todo-service-api.yaml: GET /api/v1/tasks, POST /api/v1/tasks, GET /api/v1/tasks/{task_id}, PUT /api/v1/tasks/{task_id}, DELETE /api/v1/tasks/{task_id}, POST /api/v1/tasks/{task_id}/complete
- [x] T035 [US1] Wire tasks router into Todo Service main.py in `services/todo-service/app/main.py` — include router, add DB lifespan handler for engine creation/disposal
- [x] T036 [P] [US1] Create unit tests for TaskService in `services/todo-service/tests/test_task_service.py` — test create, update, delete, complete with mocked DB session and mocked Dapr client
- [x] T037 [P] [US1] Create API endpoint tests in `services/todo-service/tests/test_tasks_api.py` — test all 6 endpoints using httpx AsyncClient with TestClient

**Checkpoint**: Todo Service fully functional — CRUD operations persist to PostgreSQL and publish events to Kafka via Dapr. Independently testable as MVP.

---

## Phase 4: User Story 2 — Audit Trail (Priority: P2)

**Goal**: Audit Service subscribes to `task-events`, stores immutable audit records, and provides a query API

**Independent Test**: Deploy Audit + Todo Service. Create/update/delete tasks via Todo API → query Audit API → verify all operations recorded in chronological order.

### Implementation for User Story 2

- [x] T038 [US2] Create AuditRecord SQLAlchemy model in `services/audit-service/app/models/audit_record.py` — all fields from data-model.md (UUID PK, event_id UNIQUE, event_type, task_id, payload JSONB, source_service, recorded_at)
- [x] T039 [US2] Create Alembic initial migration in `services/audit-service/alembic/versions/001_create_audit_records_table.py` — audit_records table with indexes (idx_audit_task_id, idx_audit_event_type, idx_audit_recorded_at, idx_audit_event_id UNIQUE)
- [x] T040 [P] [US2] Create AuditRecord Pydantic schemas in `services/audit-service/app/schemas/audit_record.py` — AuditRecordResponse, AuditListResponse per contracts/audit-service-api.yaml
- [x] T041 [US2] Create AuditService business logic in `services/audit-service/app/services/audit_service.py` — store_event (idempotent via event_id UNIQUE), list_records (filter by task_id, event_type), get_record
- [x] T042 [US2] Create Dapr Pub/Sub event handler in `services/audit-service/app/events/handlers.py` — @dapr_app.subscribe to `task-events` topic on `kafka-pubsub`, parse TaskEvent, call AuditService.store_event with idempotency check
- [x] T043 [US2] Create audit query router in `services/audit-service/app/routers/audit.py` — GET /api/v1/audit (with task_id, event_type filters), GET /api/v1/audit/{record_id} per contracts/audit-service-api.yaml
- [x] T044 [US2] Wire event handlers and audit router into Audit Service main.py in `services/audit-service/app/main.py`
- [x] T045 [P] [US2] Create unit tests for AuditService in `services/audit-service/tests/test_audit_service.py` — test store_event, idempotency (duplicate event_id), list/filter queries

**Checkpoint**: Audit Service records all task events with zero data loss. Validates end-to-end event pipeline (Todo → Kafka → Audit).

---

## Phase 5: User Story 3 — Real-Time WebSocket Updates (Priority: P3)

**Goal**: WebSocket Service subscribes to `task-updates` and broadcasts to connected clients

**Independent Test**: Deploy WebSocket + Todo Service. Connect 2 WebSocket clients → create task via Todo API → both clients receive event within 2 seconds.

### Implementation for User Story 3

- [x] T046 [US3] Create WebSocket connection manager in `services/websocket-service/app/ws/manager.py` — ConnectionManager class: connect, disconnect, broadcast methods; track active connections; handle graceful disconnection
- [x] T047 [US3] Create Dapr Pub/Sub event handler in `services/websocket-service/app/events/handlers.py` — @dapr_app.subscribe to `task-updates` topic on `kafka-pubsub`, parse TaskEvent, call ConnectionManager.broadcast
- [x] T048 [US3] Create WebSocket endpoint in `services/websocket-service/app/main.py` — add /ws WebSocket route using ConnectionManager, add /api/v1/connections GET for active count, wire event handlers
- [x] T049 [P] [US3] Create unit tests for ConnectionManager in `services/websocket-service/tests/test_ws_manager.py` — test connect, disconnect, broadcast to multiple clients, broadcast with zero clients

**Checkpoint**: WebSocket Service broadcasts task updates to all connected clients in real time. Validates `task-updates` topic end-to-end.

---

## Phase 6: User Story 4 — Reminder Notifications (Priority: P4)

**Goal**: Notification Service subscribes to `reminders` topic and delivers in-app notifications

**Independent Test**: Publish a test reminder event to `reminders` topic → verify Notification Service creates notification record with status=sent.

### Implementation for User Story 4

- [x] T050 [US4] Create Notification SQLAlchemy model in `services/notification-service/app/models/notification.py` — all fields from data-model.md (UUID PK, task_id, notification_type, channel, status, payload JSONB, created_at, sent_at, error_message)
- [x] T051 [US4] Create Alembic initial migration in `services/notification-service/alembic/versions/001_create_notifications_table.py` — notifications table with indexes (idx_notifications_status, idx_notifications_task_id)
- [x] T052 [P] [US4] Create Notification Pydantic schemas in `services/notification-service/app/schemas/notification.py` — NotificationResponse, NotificationListResponse per contracts/notification-service-api.yaml
- [x] T053 [US4] Create NotificationService business logic in `services/notification-service/app/services/notification_service.py` — create_notification, deliver_notification (in-app channel: mark as sent), list_notifications, handle_failure (mark as failed with error_message)
- [x] T054 [US4] Create Dapr Pub/Sub event handler in `services/notification-service/app/events/handlers.py` — @dapr_app.subscribe to `reminders` topic on `kafka-pubsub`, parse ReminderEvent, call NotificationService.create_notification + deliver
- [x] T055 [US4] Create notifications query router in `services/notification-service/app/routers/notifications.py` — GET /api/v1/notifications (with status, task_id filters) per contracts/notification-service-api.yaml
- [x] T056 [US4] Wire event handlers and notifications router into Notification Service main.py in `services/notification-service/app/main.py`
- [x] T057 [P] [US4] Create unit tests for NotificationService in `services/notification-service/tests/test_notification_service.py` — test create, deliver (success/failure), idempotency

**Checkpoint**: Notification Service processes reminder events and records delivery status. Validates `reminders` topic end-to-end.

---

## Phase 7: User Story 5 — Recurring Task Auto-Generation (Priority: P5)

**Goal**: Recurring Task Service detects task completions and auto-generates next instances; schedules reminders via APScheduler

**Independent Test**: Deploy Recurring Task + Todo Service. Create a recurring daily task → complete it → verify new task instance created for next day.

### Implementation for User Story 5

- [x] T058 [US5] Create RecurrenceSchedule SQLAlchemy model in `services/recurring-task-service/app/models/recurrence.py` — all fields from data-model.md (UUID PK, parent_task_id, frequency, next_due_date, is_active, created_at, updated_at)
- [x] T059 [US5] Create Alembic initial migration in `services/recurring-task-service/alembic/versions/001_create_recurrence_schedules_table.py` — recurrence_schedules table with indexes (idx_recurrence_parent_task, idx_recurrence_active_next)
- [x] T060 [P] [US5] Create RecurrenceSchedule Pydantic schemas in `services/recurring-task-service/app/schemas/recurrence.py` — RecurrenceResponse, RecurrenceListResponse per contracts/recurring-task-service-api.yaml
- [x] T061 [US5] Create RecurrenceService business logic in `services/recurring-task-service/app/services/recurrence_service.py` — handle_task_created (create schedule if is_recurring), handle_task_completed (calculate next_due_date, publish new task via Dapr to Todo Service), handle_task_deleted (deactivate schedule), list_schedules
- [x] T062 [US5] Create APScheduler reminder jobs in `services/recurring-task-service/app/scheduler/jobs.py` — AsyncIOScheduler setup, schedule_reminder (one-time job at reminder_time), publish_reminder (publish ReminderEvent to `reminders` topic via Dapr), integrate with service lifespan (start/shutdown)
- [x] T063 [US5] Create Dapr Pub/Sub event handler in `services/recurring-task-service/app/events/handlers.py` — @dapr_app.subscribe to `task-events` topic on `kafka-pubsub`, route by event_type: task-created → handle_task_created, task-completed → handle_task_completed, task-deleted → handle_task_deleted
- [x] T064 [US5] Create schedules query router in `services/recurring-task-service/app/routers/schedules.py` — GET /api/v1/schedules (with is_active filter), GET /api/v1/schedules/{schedule_id} per contracts/recurring-task-service-api.yaml
- [x] T065 [US5] Wire event handlers, scheduler, and schedules router into Recurring Task Service main.py in `services/recurring-task-service/app/main.py` — APScheduler start in lifespan startup, shutdown in lifespan shutdown
- [x] T066 [P] [US5] Create unit tests for RecurrenceService in `services/recurring-task-service/tests/test_recurrence_service.py` — test handle_task_created (recurring), handle_task_completed (next_due_date calculation for daily/weekly/monthly), handle_task_deleted (deactivation)
- [x] T067 [P] [US5] Create unit tests for scheduler jobs in `services/recurring-task-service/tests/test_scheduler_jobs.py` — test schedule_reminder, publish_reminder with mocked Dapr client

**Checkpoint**: Recurring Task Service auto-generates tasks on completion and schedules reminders. Most complex service validated.

---

## Phase 8: Deployment & CI/CD

**Purpose**: Kubernetes deployment manifests and GitHub Actions pipeline

- [x] T068 Create Todo Service K8s deployment manifest in `k8s/deployments/todo-service.yaml` — Deployment (port 8001, non-root, Dapr annotations: app-id=todo-service, app-port=8001) + Service (ClusterIP) + resource limits (200m/256Mi request, 500m/512Mi limit)
- [x] T069 [P] Create Audit Service K8s deployment manifest in `k8s/deployments/audit-service.yaml` — same pattern, port 8002, app-id=audit-service
- [x] T070 [P] Create WebSocket Service K8s deployment manifest in `k8s/deployments/websocket-service.yaml` — same pattern, port 8003, app-id=websocket-service
- [x] T071 [P] Create Notification Service K8s deployment manifest in `k8s/deployments/notification-service.yaml` — same pattern, port 8004, app-id=notification-service
- [x] T072 [P] Create Recurring Task Service K8s deployment manifest in `k8s/deployments/recurring-task-service.yaml` — same pattern, port 8005, app-id=recurring-task-service
- [x] T073 Create Minikube deployment script in `scripts/deploy-phase5.sh` — prerequisite checks (minikube, dapr, kubectl), install Dapr on K8s, deploy Redpanda, create topics, apply Dapr components, build images (eval minikube docker-env), deploy services, verify health
- [x] T074 Create GitHub Actions CI/CD pipeline in `.github/workflows/ci-cd.yaml` — build all 5 Docker images, run pytest for all services, deploy to Minikube (CI), validate health endpoints

**Checkpoint**: All services deployable to Minikube via single script. CI/CD pipeline automated.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Integration testing, end-to-end validation, and documentation

- [X] T075 Create integration test for Todo→Audit event pipeline in `services/audit-service/tests/test_integration_audit.py` — start both services, create task, verify audit record appears
- [X] T076 [P] Create integration test for Todo→WebSocket broadcast in `services/websocket-service/tests/test_integration_ws.py` — start both services, connect WS client, create task, verify WS receives event
- [X] T077 Create end-to-end validation script in `scripts/validate-phase5.sh` — check all pods running, health endpoints pass, create task, verify audit, verify WS broadcast, verify no Phase 4 files modified (git diff)
- [X] T078 [P] Create env.example files for each service (`services/todo-service/.env.example`, etc.) — document required environment variables per service
- [X] T079 Update quickstart.md with final deployment commands in `specs/002-microservices-dapr-kafka/quickstart.md` — verify all steps match actual scripts and manifests

**Checkpoint**: All user stories validated end-to-end. Documentation matches implementation.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 (shared library must exist) — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Phase 2 — BLOCKS US2, US3 (they consume Todo events)
- **User Story 2 (Phase 4)**: Depends on Phase 3 (needs task-events to consume)
- **User Story 3 (Phase 5)**: Depends on Phase 3 (needs task-updates to consume)
- **User Story 4 (Phase 6)**: Depends on Phase 7 (needs reminders topic to consume)
- **User Story 5 (Phase 7)**: Depends on Phase 3 (needs task-events to consume)
- **Deployment (Phase 8)**: Depends on all user stories being complete
- **Polish (Phase 9)**: Depends on Phase 8

### User Story Dependencies

- **US1 (Todo Service)**: BLOCKS US2, US3, US5 — all consume its events. Must be first.
- **US2 (Audit Service)**: Can start after US1 — independent of US3/US4/US5
- **US3 (WebSocket Service)**: Can start after US1 — independent of US2/US4/US5
- **US4 (Notification Service)**: Depends on US5 (Recurring Task publishes to `reminders`)
- **US5 (Recurring Task Service)**: Can start after US1 — US4 depends on it

### Parallel Opportunities After US1

```
US1 complete →  US2 (Audit)      ──→ Phase 8
                US3 (WebSocket)  ──→ Phase 8
                US5 (Recurring)  ──→ US4 (Notification) ──→ Phase 8
```

US2, US3, and US5 can run in parallel after US1 is complete.

### Within Each User Story

- Models before services
- Services before routers/event handlers
- Core implementation before tests
- Story complete before moving to next priority

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T012)
2. Complete Phase 2: Foundational (T013–T029)
3. Complete Phase 3: User Story 1 (T030–T037)
4. **STOP and VALIDATE**: Test Todo Service independently via API
5. Deploy to Minikube (T068 + T073 partial) for MVP demo

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (Todo) → Test independently → MVP!
3. Add US2 (Audit) + US3 (WebSocket) + US5 (Recurring) in parallel
4. Add US4 (Notification) after US5
5. Deployment + Polish

---

## Task Summary

| Phase | Tasks | Count |
|-------|-------|-------|
| Phase 1: Setup | T001–T012 | 12 |
| Phase 2: Foundational | T013–T029 | 17 |
| Phase 3: US1 — Todo CRUD + Events | T030–T037 | 8 |
| Phase 4: US2 — Audit Trail | T038–T045 | 8 |
| Phase 5: US3 — WebSocket Updates | T046–T049 | 4 |
| Phase 6: US4 — Notifications | T050–T057 | 8 |
| Phase 7: US5 — Recurring Tasks | T058–T067 | 10 |
| Phase 8: Deployment & CI/CD | T068–T074 | 7 |
| Phase 9: Polish & Validation | T075–T079 | 5 |
| **Total** | | **79** |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- All code MUST reference Task ID (e.g., `# Task: T030`) in comments per Constitution Principle I
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Phase 4 code MUST NOT be modified (Constitution Principle VI)
- APScheduler replaces Dapr Jobs API per research.md AD-2
