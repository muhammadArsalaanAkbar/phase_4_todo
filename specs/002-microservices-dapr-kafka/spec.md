# Feature Specification: Phase 5 Microservices Platform

**Feature Branch**: `002-microservices-dapr-kafka`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Phase 5 Todo AI — Microservices with Dapr, Kafka, and event-driven architecture"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Task CRUD with Event Publishing (Priority: P1)

As a user, I want to create, update, delete, and complete tasks through the
Todo Service, with every operation automatically publishing events so that
other services (audit, notifications, real-time sync) can react without the
Todo Service knowing about them.

**Why this priority**: The Todo Service is the core domain service. All other
services depend on the events it produces. Without a functioning Todo Service
publishing to Kafka via Dapr Pub/Sub, no downstream service has data to consume.

**Independent Test**: Deploy only the Todo Service with Dapr sidecar and Kafka.
Perform CRUD operations via the API and verify events appear on the
`task-events` and `task-updates` Kafka topics.

**Acceptance Scenarios**:

1. **Given** the Todo Service is running with a Dapr sidecar, **When** a user
   creates a new task via the API, **Then** the task is persisted in PostgreSQL
   and a `task-created` event is published to the `task-events` topic.
2. **Given** a task exists, **When** a user updates the task title or
   description, **Then** the task is updated in PostgreSQL and a
   `task-updated` event is published to the `task-events` topic.
3. **Given** a task exists, **When** a user marks the task as complete,
   **Then** the task status changes to complete, a `task-completed` event is
   published to `task-events`, and a `task-updates` event is published for
   real-time sync.
4. **Given** a task exists, **When** a user deletes the task, **Then** the
   task is removed from PostgreSQL and a `task-deleted` event is published to
   the `task-events` topic.

---

### User Story 2 - Audit Trail for Task Operations (Priority: P2)

As an admin, I want a complete, immutable history of every task operation so
that I can review who did what and when for compliance and debugging purposes.

**Why this priority**: Audit is a passive consumer of events. Once the Todo
Service publishes events (P1), the Audit Service simply subscribes and stores
them. It validates the event-driven pipeline end-to-end without requiring
complex business logic.

**Independent Test**: Deploy the Audit Service alongside the Todo Service.
Perform several CRUD operations, then query the Audit Service API to verify
all operations are recorded with timestamps and operation types.

**Acceptance Scenarios**:

1. **Given** the Audit Service is subscribed to `task-events`, **When** a
   `task-created` event is published, **Then** the Audit Service stores the
   event with timestamp, operation type, task ID, and payload.
2. **Given** multiple task operations have occurred, **When** an admin queries
   the audit log for a specific task, **Then** all operations for that task
   are returned in chronological order.
3. **Given** the Audit Service is temporarily unavailable, **When** it
   reconnects, **Then** it processes all missed events from Kafka without
   data loss (Kafka retention guarantees delivery).

---

### User Story 3 - Real-Time Task Updates via WebSocket (Priority: P3)

As a user with multiple devices or browser tabs open, I want to see task
changes reflected in real time across all connected clients without manually
refreshing.

**Why this priority**: Real-time sync is a high-value user experience feature
that validates the `task-updates` topic and WebSocket integration. It depends
on the Todo Service (P1) publishing updates.

**Independent Test**: Deploy the WebSocket Service alongside the Todo Service.
Connect two WebSocket clients. Create a task via the API and verify both
clients receive the update within 2 seconds.

**Acceptance Scenarios**:

1. **Given** a user has two browser tabs connected via WebSocket, **When** a
   task is created in one tab, **Then** the new task appears in the other tab
   within 2 seconds.
2. **Given** a WebSocket client is connected, **When** a task is updated or
   deleted, **Then** the client receives the change event and can update its
   local state.
3. **Given** a WebSocket client disconnects and reconnects, **When** the
   reconnection completes, **Then** the client receives any events missed
   during the disconnection window.

---

### User Story 4 - Task Reminder Notifications (Priority: P4)

As a user, I want to receive notifications when a task reminder is due so
that I never miss an important deadline.

**Why this priority**: Notifications require the `reminders` Kafka topic and
introduce the Notification Service as a consumer. This validates the second
Kafka topic and the push/email notification delivery mechanism.

**Independent Test**: Deploy the Notification Service alongside the Todo
Service and Recurring Task Service. Create a task with a reminder time.
Verify the notification is delivered when the reminder fires.

**Acceptance Scenarios**:

1. **Given** a task has a reminder set for a specific time, **When** that time
   arrives, **Then** the Recurring Task Service publishes a reminder event to
   the `reminders` topic.
2. **Given** a reminder event is published, **When** the Notification Service
   receives it, **Then** it delivers a notification to the user via the
   configured channel (in-app notification as default).
3. **Given** multiple reminders fire at the same time, **When** the
   Notification Service processes them, **Then** all notifications are
   delivered without loss or duplication.

---

### User Story 5 - Recurring Task Auto-Generation (Priority: P5)

As a user, I want to define recurring tasks (daily, weekly, monthly) that
automatically generate a new task instance when the current one is completed,
so I do not need to manually recreate repetitive tasks.

**Why this priority**: Recurring tasks introduce the Dapr Jobs API for
scheduling and the most complex business logic. It depends on `task-events`
(P1) to detect completion and requires a scheduling mechanism.

**Independent Test**: Deploy the Recurring Task Service alongside the Todo
Service. Create a recurring task with a daily schedule. Complete the task
and verify a new instance is automatically created for the next day.

**Acceptance Scenarios**:

1. **Given** a task is marked as recurring with a daily schedule, **When** the
   user completes the task, **Then** the Recurring Task Service detects the
   `task-completed` event and creates a new task instance for the next day.
2. **Given** a recurring task with a weekly schedule, **When** the current
   instance is completed, **Then** the next instance is created 7 days from
   the original due date (not from the completion date).
3. **Given** a recurring task exists, **When** the user deletes it (not just
   completes), **Then** the recurrence schedule is cancelled and no future
   instances are generated.

---

### Edge Cases

- What happens when a Dapr sidecar is unavailable? The service MUST return a
  clear error indicating the dependency is down, not silently drop events.
- What happens when Kafka is unreachable? Events MUST be retried with
  exponential backoff; the service MUST NOT lose events or return success
  to the user if the event was not published.
- What happens when a duplicate event is received by a consumer? Consumers
  MUST be idempotent — processing the same event twice MUST NOT create
  duplicate records.
- What happens when a service receives an event with an unknown schema
  version? The service MUST log the event, skip processing, and emit a
  warning metric.
- What happens when the WebSocket Service has 0 connected clients? Events
  MUST still be consumed from Kafka (to maintain consumer offset) but no
  broadcast is attempted.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST decompose into five independently deployable
  microservices: Todo, Notification, Recurring Task, Audit, and WebSocket.
- **FR-002**: Todo Service MUST perform full CRUD operations (create, read,
  update, delete, complete) on tasks and persist them in PostgreSQL.
- **FR-003**: Todo Service MUST publish events to `task-events` topic for
  every state change (create, update, delete, complete).
- **FR-004**: Todo Service MUST publish events to `task-updates` topic for
  real-time client synchronization on every state change.
- **FR-005**: Audit Service MUST subscribe to `task-events` and store every
  event as an immutable audit record in PostgreSQL.
- **FR-006**: WebSocket Service MUST subscribe to `task-updates` and broadcast
  events to all connected WebSocket clients.
- **FR-007**: Notification Service MUST subscribe to `reminders` and deliver
  notifications via in-app channel (default).
- **FR-008**: Recurring Task Service MUST subscribe to `task-events`, detect
  `task-completed` events for recurring tasks, and create the next task
  instance using the defined schedule (daily, weekly, monthly).
- **FR-009**: Recurring Task Service MUST use Dapr Jobs API for scheduling
  reminder publications to the `reminders` topic.
- **FR-010**: All inter-service communication MUST flow through Dapr sidecars;
  no direct HTTP calls between services.
- **FR-011**: All services MUST use Dapr Secrets API for database credentials
  and API keys.
- **FR-012**: All services MUST emit structured JSON logs with Task ID
  references for traceability.
- **FR-013**: All services MUST expose health check endpoints (liveness and
  readiness).
- **FR-014**: All events MUST follow a standardized schema with fields:
  event_id, event_type, timestamp, task_id, payload, and schema_version.
- **FR-015**: All event consumers MUST be idempotent — duplicate event
  delivery MUST NOT produce duplicate side effects.

### Key Entities

- **Task**: Represents a todo item owned by a user. Key attributes: id, title,
  description, status (pending/in_progress/complete), due_date,
  reminder_time, is_recurring, recurrence_schedule, created_at, updated_at.
- **TaskEvent**: Represents a state change event published to Kafka. Key
  attributes: event_id, event_type (created/updated/deleted/completed),
  timestamp, task_id, payload (task snapshot), schema_version.
- **AuditRecord**: Represents an immutable log entry of a task operation. Key
  attributes: id, event_id, event_type, task_id, payload, recorded_at.
- **RecurrenceSchedule**: Represents the recurring pattern for a task. Key
  attributes: frequency (daily/weekly/monthly), next_due_date,
  parent_task_id, is_active.
- **Notification**: Represents a notification to be delivered to a user. Key
  attributes: id, task_id, notification_type (reminder/update), channel
  (in_app), status (pending/sent/failed), created_at, sent_at.

### Assumptions

- Phase 4 has no backend source code to import directly; "reuse Phase 4 CRUD
  logic" means reimplementing equivalent functionality in Python/FastAPI,
  using Phase 4 Dockerfiles, Helm charts, and env configs as structural
  reference.
- In-app notification is the default and only notification channel for MVP.
  Email and push notification channels are deferred to future iterations.
- Authentication/authorization is out of scope for Phase 5 MVP. All API
  endpoints are unauthenticated. User identity is assumed from request
  context.
- Each microservice gets its own PostgreSQL schema/database within Neon DB
  to enforce data isolation (Principle IV of the constitution).
- Kafka topic partitioning strategy defaults to single partition per topic
  for local development; production partitioning is deferred to cloud
  deployment planning.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 5 microservices deploy successfully on Minikube and pass
  health checks within 60 seconds of deployment.
- **SC-002**: A task CRUD operation in the Todo Service results in the
  corresponding event appearing on the Kafka topic within 1 second.
- **SC-003**: The Audit Service records 100% of task events with zero data
  loss over a 1-hour test window.
- **SC-004**: Connected WebSocket clients receive task update events within
  2 seconds of the originating operation.
- **SC-005**: Recurring tasks auto-generate the next instance within 5 seconds
  of the previous instance being completed.
- **SC-006**: Reminder notifications are delivered within 10 seconds of the
  scheduled reminder time.
- **SC-007**: No service directly accesses Kafka or PostgreSQL — all access
  is verified through Dapr sidecar logs.
- **SC-008**: GitHub Actions CI/CD pipeline builds, tests, and deploys all
  5 services without manual intervention.
- **SC-009**: All structured logs include Task ID references, verifiable by
  querying logs for any task operation.
- **SC-010**: Zero Phase 4 files are modified (verified by diffing against
  Phase 4 baseline).
