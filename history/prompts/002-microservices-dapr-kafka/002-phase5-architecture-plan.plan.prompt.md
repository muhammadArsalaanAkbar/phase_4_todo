---
id: 002
title: Phase 5 Architecture Plan
stage: plan
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: 002-microservices-dapr-kafka
branch: 002-microservices-dapr-kafka
user: architect
command: /sp.plan
labels: ["phase-v", "architecture", "dapr", "kafka", "redpanda", "fastapi", "microservices"]
links:
  spec: specs/002-microservices-dapr-kafka/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-microservices-dapr-kafka/plan.md
  - specs/002-microservices-dapr-kafka/research.md
  - specs/002-microservices-dapr-kafka/data-model.md
  - specs/002-microservices-dapr-kafka/quickstart.md
  - specs/002-microservices-dapr-kafka/contracts/todo-service-api.yaml
  - specs/002-microservices-dapr-kafka/contracts/audit-service-api.yaml
  - specs/002-microservices-dapr-kafka/contracts/websocket-service-api.yaml
  - specs/002-microservices-dapr-kafka/contracts/notification-service-api.yaml
  - specs/002-microservices-dapr-kafka/contracts/recurring-task-service-api.yaml
tests:
  - null
---

## Prompt

# speckit.plan - Phase 5 Todo AI

## Purpose
This file defines the **architecture, components, interfaces, and high-level sequencing** for Phase 5 Todo AI. Claude and agents must follow this to generate tasks and implement services.

## High-Level Architecture
### Microservices
1. Todo Service - CRUD + event publishing via Dapr Pub/Sub
2. Notification Service - Subscribe reminders, send notifications
3. Recurring Task Service - Subscribe task-events, Dapr Jobs API
4. Audit Service - Subscribe task-events, store in PostgreSQL
5. WebSocket Service - Subscribe task-updates, broadcast real-time

## Event-Driven Architecture (Kafka + Dapr)
- task-events: Todo Service → Recurring Task, Audit
- reminders: Todo Service → Notification Service
- task-updates: Todo Service → WebSocket Service

## Dapr Components
- kafka-pubsub (pubsub.kafka), statestore (state.postgresql), dapr-jobs, kubernetes-secrets

## Deployment: Minikube (local) + AKS/GKE (cloud)
## Sequencing: Todo first → then Audit/WebSocket/Notification/Recurring

## Response snapshot

Created comprehensive Phase 5 architecture plan with 9 artifacts:

**Research findings (research.md)**:
- Dapr Python SDK 1.16.0 with FastAPI extension for Pub/Sub
- Dapr Jobs API NOT available in Python SDK — using APScheduler instead
- Redpanda over Strimzi (1GB vs 4GB RAM; critical for 3.7GB Docker budget)
- SQLAlchemy 2.0 async + asyncpg (~5x faster than psycopg3)
- CloudEvents v1.0 auto-wrapped by Dapr with custom type/source fields

**Architecture decisions (plan.md)**:
- AD-1: Redpanda over Strimzi (memory constraint)
- AD-2: APScheduler over Dapr Jobs API (no Python SDK)
- AD-3: SQLAlchemy 2.0 over SQLModel (outdated dependency)
- AD-4: Per-service PostgreSQL schema (not separate DBs)
- AD-5: K8s YAML over Helm charts (Dapr annotations replace Helm templating)

**Data model (data-model.md)**: 4 DB schemas (todo_service, audit_service, notification_service, recurring_task_service) with 5 entities and event schemas.

**API contracts**: OpenAPI 3.1 specs for all 5 services with port assignments (8001-8005).

**Constitution Check**: All 9 principles PASS. One deviation documented: APScheduler instead of Dapr Jobs API (justified — no Python SDK available).

**Quickstart (quickstart.md)**: 8-step local deployment guide for Minikube.

## Outcome

- ✅ Impact: Complete architecture plan ready for /sp.tasks generation
- 🧪 Tests: N/A — planning artifact, no code
- 📁 Files: plan.md, research.md, data-model.md, quickstart.md, 5 API contract YAMLs
- 🔁 Next prompts: /sp.tasks to generate implementation tasks, /sp.adr for architectural decisions
- 🧠 Reflection: Key discovery — Dapr Jobs API unavailable in Python SDK. APScheduler is a clean workaround that preserves Dapr-mediated communication for all external calls. Memory constraint (3.7GB) makes Redpanda the only viable Kafka option.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution Check PASS (9/9), all NEEDS CLARIFICATION resolved in research
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider grouping AD-1/AD-2/AD-3 into a single "Phase 5 Technology Stack" ADR
