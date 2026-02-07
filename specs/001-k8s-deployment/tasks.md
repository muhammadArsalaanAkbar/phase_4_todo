# Tasks: Kubernetes Deployment

**Input**: Design documents from `/specs/001-k8s-deployment/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: No automated tests requested. Validation via `helm lint` and manual verification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Infrastructure**: `charts/`, `docker/`, `scripts/`
- **Environment**: `env.example.*` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create directory structure and initialize Helm chart scaffolding

- [ ] T001 Create charts directory structure per plan.md in charts/
- [ ] T002 [P] Create docker directory structure in docker/frontend/ and docker/backend/
- [ ] T003 [P] Create scripts directory structure in scripts/
- [ ] T004 [P] Create env.example.frontend at repository root
- [ ] T005 [P] Create env.example.backend at repository root

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core Helm charts and Dockerfiles that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

### Infrastructure Chart (shared by all stories)

- [ ] T006 Create Chart.yaml for todo-infrastructure in charts/todo-infrastructure/Chart.yaml
- [ ] T007 Create values.yaml for todo-infrastructure in charts/todo-infrastructure/values.yaml
- [ ] T008 [P] Create namespace template in charts/todo-infrastructure/templates/namespace.yaml
- [ ] T009 [P] Create resourcequota template in charts/todo-infrastructure/templates/resourcequota.yaml

### Frontend Helm Chart Structure

- [ ] T010 Create Chart.yaml for todo-frontend in charts/todo-frontend/Chart.yaml
- [ ] T011 Create base values.yaml for todo-frontend in charts/todo-frontend/values.yaml
- [ ] T012 [P] Create values-dev.yaml for todo-frontend in charts/todo-frontend/values-dev.yaml
- [ ] T013 [P] Create values-staging.yaml for todo-frontend in charts/todo-frontend/values-staging.yaml
- [ ] T014 [P] Create values-prod.yaml for todo-frontend in charts/todo-frontend/values-prod.yaml
- [ ] T015 Create _helpers.tpl for todo-frontend in charts/todo-frontend/templates/_helpers.tpl

### Backend Helm Chart Structure

- [ ] T016 Create Chart.yaml for todo-backend in charts/todo-backend/Chart.yaml
- [ ] T017 Create base values.yaml for todo-backend in charts/todo-backend/values.yaml
- [ ] T018 [P] Create values-dev.yaml for todo-backend in charts/todo-backend/values-dev.yaml
- [ ] T019 [P] Create values-staging.yaml for todo-backend in charts/todo-backend/values-staging.yaml
- [ ] T020 [P] Create values-prod.yaml for todo-backend in charts/todo-backend/values-prod.yaml
- [ ] T021 Create _helpers.tpl for todo-backend in charts/todo-backend/templates/_helpers.tpl

### Dockerfiles (required for container-first)

- [ ] T022 Create multi-stage Dockerfile for frontend in docker/frontend/Dockerfile
- [ ] T023 [P] Create .dockerignore for frontend in docker/frontend/.dockerignore
- [ ] T024 Create multi-stage Dockerfile for backend in docker/backend/Dockerfile
- [ ] T025 [P] Create .dockerignore for backend in docker/backend/.dockerignore

**Checkpoint**: Foundation ready - Helm chart structure and Dockerfiles exist. User story implementation can now begin.

---

## Phase 3: User Story 1 - One-Command Local Deployment (Priority: P1)

**Goal**: Deploy complete system with single command, pods healthy in <5 minutes

**Independent Test**: Run `./scripts/deploy.sh` on fresh Minikube, verify all pods reach Running status

### Core Deployment Templates

- [ ] T026 [US1] Create deployment template for frontend in charts/todo-frontend/templates/deployment.yaml
- [ ] T027 [US1] Create service template for frontend in charts/todo-frontend/templates/service.yaml
- [ ] T028 [US1] Create configmap template for frontend in charts/todo-frontend/templates/configmap.yaml
- [ ] T029 [US1] Create ingress template for frontend in charts/todo-frontend/templates/ingress.yaml
- [ ] T030 [US1] Create deployment template for backend in charts/todo-backend/templates/deployment.yaml
- [ ] T031 [US1] Create service template for backend in charts/todo-backend/templates/service.yaml
- [ ] T032 [US1] Create configmap template for backend in charts/todo-backend/templates/configmap.yaml
- [ ] T033 [US1] Create serviceaccount template for backend in charts/todo-backend/templates/serviceaccount.yaml

### Deployment Script

- [ ] T034 [US1] Create deploy.sh script with prereq validation in scripts/deploy.sh
- [ ] T035 [US1] Create validate.sh script for pre-deployment checks in scripts/validate.sh

### Validation

- [ ] T036 [US1] Run helm lint on all charts to verify syntax
- [ ] T037 [US1] Run helm template to verify generated manifests

**Checkpoint**: User Story 1 complete. `./scripts/deploy.sh` deploys frontend and backend to Minikube.

---

## Phase 4: User Story 2 - Secure Secrets Management (Priority: P2)

**Goal**: Secrets injected securely, never visible in code/logs/specs

**Independent Test**: Deploy with secrets, run `kubectl describe pod` and verify no plain-text secrets

### Secrets Infrastructure

- [ ] T038 [US2] Create secrets template stub in charts/todo-infrastructure/templates/secrets-template.yaml
- [ ] T039 [US2] Update backend deployment to reference secrets via envFrom in charts/todo-backend/templates/deployment.yaml
- [ ] T040 [US2] Add checksum annotation for secret rotation in charts/todo-backend/templates/deployment.yaml

### Secrets Script

- [ ] T041 [US2] Create create-secrets.sh script in scripts/create-secrets.sh
- [ ] T042 [US2] Update deploy.sh to prompt for secrets if missing in scripts/deploy.sh

### Documentation

- [ ] T043 [P] [US2] Document required secrets in env.example.backend
- [ ] T044 [P] [US2] Document optional secrets in env.example.frontend

**Checkpoint**: User Story 2 complete. Secrets are securely managed and injectable.

---

## Phase 5: User Story 3 - Deployment Updates and Rollback (Priority: P3)

**Goal**: Atomic upgrades with auto-rollback on failure, manual rollback in <2 minutes

**Independent Test**: Deploy v1, upgrade to v2, rollback to v1, verify state at each step

### Atomic Deployment Configuration

- [ ] T045 [US3] Configure --atomic flag in deploy.sh for auto-rollback in scripts/deploy.sh
- [ ] T046 [US3] Add --wait flag with timeout in deploy.sh for deployment verification in scripts/deploy.sh

### Rollback Script

- [ ] T047 [US3] Create rollback.sh script with revision listing in scripts/rollback.sh
- [ ] T048 [US3] Add rollback confirmation prompt in scripts/rollback.sh

### Health Checks for Rollback Detection

- [ ] T049 [US3] Configure startupProbe in frontend deployment in charts/todo-frontend/templates/deployment.yaml
- [ ] T050 [US3] Configure startupProbe in backend deployment in charts/todo-backend/templates/deployment.yaml

**Checkpoint**: User Story 3 complete. Deployments are atomic with working rollback.

---

## Phase 6: User Story 4 - Observability Dashboard (Priority: P4)

**Goal**: Logs, metrics, traces visible for debugging

**Independent Test**: Make API request, verify log entry and metric increment visible

### Monitoring Infrastructure

- [ ] T051 [US4] Create prometheus-config.yaml in charts/todo-infrastructure/templates/monitoring/prometheus-config.yaml
- [ ] T052 [US4] Create grafana-config.yaml in charts/todo-infrastructure/templates/monitoring/grafana-config.yaml
- [ ] T053 [US4] Create servicemonitor.yaml for metric discovery in charts/todo-infrastructure/templates/monitoring/servicemonitor.yaml

### HPA for Scaling (depends on metrics)

- [ ] T054 [P] [US4] Create hpa template for frontend in charts/todo-frontend/templates/hpa.yaml
- [ ] T055 [P] [US4] Create hpa template for backend in charts/todo-backend/templates/hpa.yaml

### Network Policies (observability of traffic)

- [ ] T056 [P] [US4] Create networkpolicy template for frontend in charts/todo-frontend/templates/networkpolicy.yaml
- [ ] T057 [P] [US4] Create networkpolicy template for backend in charts/todo-backend/templates/networkpolicy.yaml

**Checkpoint**: User Story 4 complete. Prometheus/Grafana deployed with service discovery.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Finalization and validation across all user stories

- [ ] T058 Run helm lint on all three charts (frontend, backend, infrastructure)
- [ ] T059 Run full deploy.sh on fresh Minikube and time execution (<5 min target)
- [ ] T060 Verify all pods pass health checks within 60 seconds
- [ ] T061 Verify secrets are not visible in kubectl describe output
- [ ] T062 Test rollback.sh with version upgrade scenario
- [ ] T063 Verify Prometheus can scrape metrics from both services
- [ ] T064 Run quickstart.md validation steps end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 - BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2 - Core deployment
- **US2 (Phase 4)**: Depends on Phase 2 - Can run parallel with US1
- **US3 (Phase 5)**: Depends on US1 - Needs working deploy.sh
- **US4 (Phase 6)**: Depends on Phase 2 - Can run parallel with US1/US2
- **Polish (Phase 7)**: Depends on all user stories complete

### User Story Dependencies

```
Phase 2 (Foundational)
    │
    ├──→ US1 (One-Command Deploy) ──→ US3 (Updates/Rollback)
    │                                      │
    ├──→ US2 (Secrets) ────────────────────┤
    │                                      │
    └──→ US4 (Observability) ──────────────┴──→ Phase 7 (Polish)
```

### Parallel Opportunities

**Phase 1** (all parallel):
- T002, T003, T004, T005

**Phase 2** (grouped parallel):
- T008, T009 (infrastructure templates)
- T012, T013, T014 (frontend values)
- T018, T019, T020 (backend values)
- T023, T025 (dockerignore files)

**Phase 3-6** (per story parallel):
- US2: T043, T044 (env docs)
- US4: T054, T055 (HPA) and T056, T057 (network policies)

---

## Parallel Execution Examples

### Phase 2 Parallelization

```bash
# Parallel batch 1: All environment-specific values files
Task: "Create values-dev.yaml for todo-frontend"
Task: "Create values-staging.yaml for todo-frontend"
Task: "Create values-prod.yaml for todo-frontend"
Task: "Create values-dev.yaml for todo-backend"
Task: "Create values-staging.yaml for todo-backend"
Task: "Create values-prod.yaml for todo-backend"

# Parallel batch 2: Both dockerignore files
Task: "Create .dockerignore for frontend"
Task: "Create .dockerignore for backend"
```

### User Story 4 Parallelization

```bash
# HPA templates (independent files)
Task: "Create hpa template for frontend"
Task: "Create hpa template for backend"

# Network policies (independent files)
Task: "Create networkpolicy template for frontend"
Task: "Create networkpolicy template for backend"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (5 tasks)
2. Complete Phase 2: Foundational (20 tasks)
3. Complete Phase 3: User Story 1 (12 tasks)
4. **STOP and VALIDATE**: Run deploy.sh, verify pods running
5. MVP achieved - basic deployment works

### Incremental Delivery

1. Setup + Foundational → Charts exist, Dockerfiles ready
2. Add US1 → Single-command deployment works
3. Add US2 → Secrets properly managed
4. Add US3 → Safe updates and rollback
5. Add US4 → Full observability
6. Polish → Production-ready quality

### Task Counts

| Phase | Tasks | Parallel Tasks |
|-------|-------|----------------|
| Phase 1: Setup | 5 | 4 |
| Phase 2: Foundational | 20 | 12 |
| Phase 3: US1 | 12 | 0 |
| Phase 4: US2 | 7 | 2 |
| Phase 5: US3 | 6 | 0 |
| Phase 6: US4 | 7 | 4 |
| Phase 7: Polish | 7 | 0 |
| **Total** | **64** | **22** |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All Helm templates use Helm best practices (_helpers.tpl for shared logic)
- Constitution compliance verified at each phase checkpoint
