# Research: Phase 5 Microservices Platform

**Feature**: `002-microservices-dapr-kafka`
**Date**: 2026-02-08
**Status**: Complete

## 1. Dapr Python SDK

**Decision**: Use `dapr==1.16.0` (stable) with `dapr-ext-fastapi` extension.

**Rationale**: Official Dapr Python SDK provides native integration with FastAPI
via the `DaprApp` extension class, which auto-registers Pub/Sub subscription
endpoints.

**Alternatives considered**:
- Raw HTTP to Dapr sidecar (localhost:3500) — more boilerplate, no type safety
- dapr-dev package — pre-release, unstable for production use

### Pub/Sub Pattern (FastAPI)

```python
# Publishing
from dapr.clients import DaprClient

with DaprClient() as client:
    client.publish_event(
        pubsub_name="kafka-pubsub",
        topic_name="task-events",
        data={"taskId": "uuid", "eventType": "task-created"},
        data_content_type="application/json",
        metadata={
            "cloudevent.type": "com.todoai.task.created",
            "cloudevent.source": "todo-service",
        },
    )

# Subscribing
from dapr.ext.fastapi import DaprApp

app = FastAPI()
dapr_app = DaprApp(app)

@dapr_app.subscribe(pubsub="kafka-pubsub", topic="task-events")
async def handle_task_event(event_data=Body()):
    # event_data contains CloudEvents 'data' field
    pass
```

### State Store Pattern

```python
from dapr.clients import DaprClient

async def save_state(key: str, value: dict):
    with DaprClient() as client:
        client.save_state(store_name="statestore", key=key, value=json.dumps(value))

async def get_state(key: str) -> dict:
    with DaprClient() as client:
        result = client.get_state(store_name="statestore", key=key)
        return json.loads(result.data) if result.data else None
```

### Secrets API Pattern

```python
from dapr.clients import DaprClient

with DaprClient() as client:
    secret = client.get_secret(store_name="kubernetes-secrets", key="db-credentials")
    db_url = secret.secret["connectionString"]
```

## 2. Dapr Jobs API Limitation

**Decision**: Use APScheduler (Python async scheduler) instead of Dapr Jobs API
for recurring tasks and scheduled reminders.

**Rationale**: Dapr Jobs API does NOT have Python SDK support as of February 2026.
Only Go and .NET SDKs support it. Using APScheduler provides equivalent
functionality within Python without depending on an unavailable SDK feature.

**Alternatives considered**:
- Dapr Jobs API via raw HTTP — fragile, no SDK support, poor error handling
- Kubernetes CronJobs — too coarse-grained (1-minute minimum), requires K8s
  YAML per schedule, cannot be dynamically created at runtime
- Celery — heavyweight, requires Redis/RabbitMQ, overkill for our use case

**APScheduler pattern**:
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

# Schedule a one-time reminder
scheduler.add_job(
    publish_reminder,
    trigger="date",
    run_date=reminder_time,
    args=[task_id],
    id=f"reminder-{task_id}",
)

# Schedule recurring task check
scheduler.add_job(
    check_recurring_tasks,
    trigger="interval",
    minutes=1,
    id="recurring-check",
)

scheduler.start()
```

## 3. Kafka Broker Selection

**Decision**: Redpanda (single-node, Docker container) for local development.

**Rationale**: System has ~3.7GB Docker Desktop memory allocation. Strimzi
Operator requires minimum 4GB for Minikube (Kafka JVM + ZooKeeper + Operator
pod). Redpanda runs as a single C++ binary with `--memory=1G --smp=1`,
consuming ~1GB total. It is 100% Kafka-compatible at the protocol level.

**Alternatives considered**:
- Strimzi Operator — production-grade but 4GB minimum, exceeds our budget
- Confluent Platform — enterprise, even heavier than Strimzi
- Apache Kafka standalone — still requires JVM + ZooKeeper, 2-3GB minimum

**Memory budget**:
| Component | Memory |
|-----------|--------|
| Minikube base | ~500MB |
| Redpanda | ~1GB |
| Dapr control plane | ~300MB |
| 5 microservices (FastAPI) | ~500MB total |
| PostgreSQL (external Neon) | 0MB |
| **Total** | **~2.3GB** (within 3.7GB budget) |

**Cloud deployment**: Redpanda Cloud (managed) or Confluent Cloud. Dapr
Pub/Sub component YAML is the only change — application code stays identical.

## 4. Database Strategy

**Decision**: SQLAlchemy 2.0 async with asyncpg driver.

**Rationale**: asyncpg is ~5x faster than psycopg3 async (C implementation,
asyncio-native). SQLAlchemy 2.0 provides full async support, modern API, and
is actively maintained. SQLModel is stuck on SQLAlchemy 1.4.41 — outdated.

**Alternatives considered**:
- SQLModel — Pydantic integration is nice but outdated SQLAlchemy version
- Raw asyncpg — maximum performance but too much boilerplate for 5 services
- psycopg3 async — good but slower than asyncpg

**Connection pattern**:
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    "postgresql+asyncpg://user:pass@host/db",
    pool_size=5,
    max_overflow=10,
)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
```

**Schema isolation**: Each service gets its own PostgreSQL schema within Neon DB
(e.g., `todo_service`, `audit_service`). This enforces data isolation per
Constitution Principle IV without requiring separate database instances.

## 5. Event Schema (CloudEvents)

**Decision**: Use Dapr's automatic CloudEvents v1.0 wrapping with custom
`type` and `source` fields per event category.

**Rationale**: Dapr automatically wraps all Pub/Sub messages in CloudEvents
envelope. We customize the `type` field for routing and the `data` field
for payload.

**Dapr auto-generated fields**:
- `specversion`: "1.0"
- `id`: UUID (unique event ID)
- `source`: app ID (Dapr-generated)
- `type`: "com.dapr.event.sent" (default, we override)
- `time`: RFC3339 timestamp
- `topic`, `pubsubname`, `traceid`, `traceparent`

**Custom event `type` values**:
- `com.todoai.task.created`
- `com.todoai.task.updated`
- `com.todoai.task.completed`
- `com.todoai.task.deleted`
- `com.todoai.reminder.scheduled`
- `com.todoai.reminder.fired`

**Custom `data` payload schema**:
```json
{
  "event_id": "uuid",
  "event_type": "task-created",
  "task_id": "uuid",
  "timestamp": "2026-02-08T10:00:00Z",
  "schema_version": "1.0",
  "payload": {
    "title": "string",
    "description": "string",
    "status": "pending|in_progress|complete",
    "due_date": "date|null",
    "is_recurring": false,
    "recurrence_schedule": "daily|weekly|monthly|null"
  }
}
```

## 6. Dapr Component Definitions

### kafka-pubsub (pubsub.kafka)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "redpanda.todo-dev.svc.cluster.local:9092"
  - name: consumerGroup
    value: "todo-services"
  - name: authType
    value: "none"
  - name: disableTls
    value: "true"
```

### statestore (state.postgresql)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v2
  metadata:
  - name: connectionString
    secretKeyRef:
      name: dapr-db-secret
      key: connectionString
```

### kubernetes-secrets (secretstores.kubernetes)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
```

## 7. Port Assignments

Phase 4 uses ports 8000 (backend) and 3000 (frontend). Phase 5 services
MUST use different ports to avoid conflicts when running alongside Phase 4.

| Service | Application Port | Dapr HTTP Port | Dapr gRPC Port |
|---------|-----------------|----------------|----------------|
| Todo Service | 8001 | 3501 | 50001 |
| Audit Service | 8002 | 3502 | 50002 |
| WebSocket Service | 8003 | 3503 | 50003 |
| Notification Service | 8004 | 3504 | 50004 |
| Recurring Task Service | 8005 | 3505 | 50005 |

## 8. Microservice Project Structure

**Decision**: Monorepo with shared library pattern.

```
services/
├── shared/                    # Shared library (event schemas, Dapr helpers)
│   ├── pyproject.toml
│   └── shared/
│       ├── events.py          # Event schema definitions
│       ├── dapr_client.py     # Dapr client wrapper
│       └── logging.py         # Structured JSON logger
├── todo-service/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routers/
│   │   ├── services/
│   │   └── events/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── audit-service/
│   └── [same structure]
├── websocket-service/
│   └── [same structure]
├── notification-service/
│   └── [same structure]
└── recurring-task-service/
    └── [same structure]
```

**Rationale**: Shared library avoids duplicating event schemas, Dapr client
wrappers, and logging config across 5 services. Each service still has its
own Dockerfile and is independently deployable.
