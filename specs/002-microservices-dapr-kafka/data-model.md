# Data Model: Phase 5 Microservices Platform

**Feature**: `002-microservices-dapr-kafka`
**Date**: 2026-02-08

## Schema Isolation Strategy

Each microservice owns its data in a separate PostgreSQL schema within Neon DB.
No service may read or write another service's schema directly — all cross-service
data flows through Kafka events via Dapr Pub/Sub.

| Service | Schema | Tables |
|---------|--------|--------|
| Todo Service | `todo_service` | tasks |
| Audit Service | `audit_service` | audit_records |
| Notification Service | `notification_service` | notifications |
| Recurring Task Service | `recurring_task_service` | recurrence_schedules |
| WebSocket Service | (stateless) | None — uses Dapr State Store for connection tracking |

## Entities

### Task (Todo Service)

Represents a todo item. Owned exclusively by the Todo Service.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique task identifier |
| title | VARCHAR(255) | NOT NULL | Task title |
| description | TEXT | NULLABLE | Task details |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | pending, in_progress, complete |
| due_date | TIMESTAMPTZ | NULLABLE | When the task is due |
| reminder_time | TIMESTAMPTZ | NULLABLE | When to send reminder notification |
| is_recurring | BOOLEAN | NOT NULL, DEFAULT false | Whether task recurs |
| recurrence_schedule | VARCHAR(20) | NULLABLE | daily, weekly, monthly |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last update timestamp |

**State transitions**:
```
pending → in_progress → complete
pending → complete (skip in_progress)
any → deleted (soft or hard delete)
```

**Indexes**:
- `idx_tasks_status` on `status` (filtered queries)
- `idx_tasks_due_date` on `due_date` (reminder scheduling)
- `idx_tasks_is_recurring` on `is_recurring` (recurring task lookup)

### AuditRecord (Audit Service)

Immutable log entry of a task operation. Append-only, never updated or deleted.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique audit record ID |
| event_id | UUID | NOT NULL, UNIQUE | CloudEvents ID (dedup key) |
| event_type | VARCHAR(50) | NOT NULL | task-created, task-updated, etc. |
| task_id | UUID | NOT NULL | Reference to originating task |
| payload | JSONB | NOT NULL | Full event payload snapshot |
| source_service | VARCHAR(100) | NOT NULL | Service that produced the event |
| recorded_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | When audit record was stored |

**Indexes**:
- `idx_audit_task_id` on `task_id` (query by task)
- `idx_audit_event_type` on `event_type` (filter by operation)
- `idx_audit_recorded_at` on `recorded_at` (chronological queries)
- `idx_audit_event_id` on `event_id` UNIQUE (idempotency check)

### Notification (Notification Service)

Tracks notification delivery status.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique notification ID |
| task_id | UUID | NOT NULL | Task that triggered notification |
| notification_type | VARCHAR(20) | NOT NULL | reminder, update |
| channel | VARCHAR(20) | NOT NULL, DEFAULT 'in_app' | Delivery channel |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | pending, sent, failed |
| payload | JSONB | NOT NULL | Notification content |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | When notification was created |
| sent_at | TIMESTAMPTZ | NULLABLE | When notification was delivered |
| error_message | TEXT | NULLABLE | Failure reason if status=failed |

**State transitions**:
```
pending → sent
pending → failed → pending (retry)
```

**Indexes**:
- `idx_notifications_status` on `status` (pending queue)
- `idx_notifications_task_id` on `task_id` (query by task)

### RecurrenceSchedule (Recurring Task Service)

Tracks recurring task patterns and next occurrence dates.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique schedule ID |
| parent_task_id | UUID | NOT NULL | Original recurring task |
| frequency | VARCHAR(20) | NOT NULL | daily, weekly, monthly |
| next_due_date | TIMESTAMPTZ | NOT NULL | When next instance is due |
| is_active | BOOLEAN | NOT NULL, DEFAULT true | Whether schedule is active |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | When schedule was created |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last schedule update |

**State transitions**:
```
active (is_active=true) → inactive (is_active=false) on task deletion
active → recalculate next_due_date on task completion
```

**Indexes**:
- `idx_recurrence_parent_task` on `parent_task_id` (lookup by task)
- `idx_recurrence_active_next` on `(is_active, next_due_date)` (scheduling queries)

## Event Schemas (Kafka/CloudEvents)

All events are published via Dapr Pub/Sub and automatically wrapped in
CloudEvents v1.0 envelope by Dapr. The `data` field contains our custom payload.

### TaskEvent (Published to `task-events` and `task-updates`)

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "task-created",
  "task_id": "550e8400-e29b-41d4-a716-446655440001",
  "timestamp": "2026-02-08T10:00:00Z",
  "schema_version": "1.0",
  "payload": {
    "title": "Buy groceries",
    "description": "Milk, bread, eggs",
    "status": "pending",
    "due_date": "2026-02-09T18:00:00Z",
    "reminder_time": "2026-02-09T12:00:00Z",
    "is_recurring": false,
    "recurrence_schedule": null
  }
}
```

**Event types**: `task-created`, `task-updated`, `task-completed`, `task-deleted`

### ReminderEvent (Published to `reminders`)

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440002",
  "event_type": "reminder-fired",
  "task_id": "550e8400-e29b-41d4-a716-446655440001",
  "timestamp": "2026-02-09T12:00:00Z",
  "schema_version": "1.0",
  "payload": {
    "title": "Buy groceries",
    "reminder_time": "2026-02-09T12:00:00Z",
    "channel": "in_app"
  }
}
```

## Relationships

```
Task (Todo Service)
  │
  ├──publishes──→ TaskEvent ──→ task-events topic
  │                                ├──consumed by──→ AuditRecord (Audit Service)
  │                                └──consumed by──→ RecurrenceSchedule (Recurring Task)
  │
  ├──publishes──→ TaskEvent ──→ task-updates topic
  │                                └──consumed by──→ WebSocket Service (broadcast)
  │
  └──has──→ RecurrenceSchedule (Recurring Task Service)
               │
               └──publishes──→ ReminderEvent ──→ reminders topic
                                                    └──consumed by──→ Notification
```

## Migration Strategy

Each service manages its own schema migrations independently using Alembic
(SQLAlchemy's migration tool). Migrations run as init containers in Kubernetes
before the service starts.

```
services/<service>/alembic/
├── alembic.ini
├── env.py
└── versions/
    └── 001_initial.py
```
