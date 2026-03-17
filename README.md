# Q4-Rescue

Q4-Rescue is a FastAPI and Postgres backend for medication-adherence rescue operations.

The current implementation delivers one real vertical slice: case management. It can create, list, read, update, and archive rescue cases backed by a normalized domain model. The broader platform shape described in [`documentation/`](documentation/) is still ahead of the running code in areas such as intake automation, task orchestration, projections, and dashboards.

The governed documentation set starts at [`documentation/00_master_index.md`](documentation/00_master_index.md). This README is the practical runtime guide for the code that exists today.

## Current Status

Implemented today:

- FastAPI app startup, runtime settings validation, and automatic Alembic migration on boot in [`app/main.py`](app/main.py) and [`app/persistence/db.py`](app/persistence/db.py)
- Postgres persistence with schema, migrations, and repositories in [`app/persistence/`](app/persistence/)
- Case-centered domain model with lifecycle rules in [`app/domain/`](app/domain/)
- Case API for create, list, detail, status update, and archive in [`app/api/routes/case.py`](app/api/routes/case.py)
- Bearer-token auth with permission checks in [`app/api/security.py`](app/api/security.py)
- Service-layer orchestration and audit logging in [`app/application/services/case_service.py`](app/application/services/case_service.py)
- Idempotent case creation via [`app/persistence/repositories/idempotency_repo.py`](app/persistence/repositories/idempotency_repo.py)
- Vendor-neutral observability foundation in [`app/observability/`](app/observability/)
- Postgres-backed tests in [`tests/`](tests/)

Not implemented yet:

- eligibility ingestion and automated intake
- task, barrier, and contact-attempt APIs
- governed domain event emission and automation dispatch
- projection models, work queues, and dashboards
- frontend and voice-agent workflows

## Domain Snapshot

The active model is centered on `Case` as the aggregate root.

- `Member` is the persistent person identity across time.
- `Referral` is the intake record that starts a rescue episode.
- `Case` is the operational rescue record for one member.
- `Measure` and `Medication` capture the adherence work inside the case.
- `Provider` and `Pharmacy` are shared actors connected through `MedicationProvider` and `MedicationPharmacy`.
- `Barrier`, `Task`, and `ContactAttempt` already exist in the data model, but are not yet exposed through dedicated workflows.

Implemented case statuses:

- `open`
- `in_progress`
- `on_hold`
- `closed`
- `archived`

The system prevents duplicate active cases for the same member.

## Repository Map

- [`app/api/`](app/api/) - FastAPI routes, request schemas, auth, and dependencies
- [`app/application/services/`](app/application/services/) - application workflows and audit-aware service methods
- [`app/domain/`](app/domain/) - domain entities, value rules, and lifecycle behavior
- [`app/observability/`](app/observability/) - JSON logging, request correlation, Prometheus metrics, and OpenTelemetry tracing
- [`app/persistence/`](app/persistence/) - database connection wrappers, schema, migrations, and repositories
- [`app/automation/`](app/automation/) - planned automation dispatch layer, not implemented yet
- [`app/projection/`](app/projection/) - planned read models and reporting layer, not implemented yet
- [`app/rules/`](app/rules/) - planned business-rule engines beyond the current domain validation
- [`documentation/`](documentation/) - governed product, workflow, rules, and governance docs

## Local Development

### Prerequisites

- Python 3.11+
- Docker
- a local Postgres client if you want to create the test database manually

### Environment

Copy values from [`.env.example`](.env.example) into your shell or local `.env`.

Important variables:

- `Q4_RESCUE_DATABASE_URL` - main app database
- `Q4_RESCUE_TEST_DATABASE_URL` - disposable database for tests
- `Q4_RESCUE_AUTH_ENABLED` and `Q4_RESCUE_AUTH_TOKENS` - local auth behavior
- `Q4_RESCUE_METRICS_ENABLED` - enables `/metrics`
- `Q4_RESCUE_OTEL_ENABLED` - enables tracing instrumentation
- `Q4_RESCUE_OTEL_EXPORTER_OTLP_ENDPOINT` - optional OTLP trace export target

### Start Postgres

```bash
docker compose up -d postgres
```

The provided Compose file creates the `q4_rescue` database. Create `q4_rescue_test` once for the test suite if it does not already exist.

### Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[test]
```

### Run Migrations

```bash
alembic upgrade head
```

The app also runs migrations during startup, so a correctly configured database will be upgraded automatically.

### Run the API

```bash
uvicorn app.main:app --reload
```

### Run Tests

```bash
python -m unittest discover -s tests -p 'test*.py' -q
```

## API Surface

Current routes:

- `POST /cases/` - create a case with nested member, referral, measure, medication, provider, and pharmacy data
- `GET /cases` - list case summaries
- `GET /cases/{case_id}` - fetch one normalized case graph
- `PUT /cases/{case_id}/status` - move a case through its lifecycle
- `DELETE /cases/{case_id}` - archive a case
- `GET /health` - basic health check
- `GET /metrics` - Prometheus metrics when metrics are enabled

Authentication uses Bearer tokens with explicit permissions. The current case routes rely on:

- `cases:read`
- `cases:detail`
- `cases:write`

## Observability

The backend now ships with a vendor-neutral observability foundation:

- structured JSON logs to stdout
- `X-Request-ID` correlation on requests and responses
- `X-Trace-ID` response headers when tracing is active
- Prometheus metrics for HTTP, service, DB, and core case events
- OpenTelemetry spans across HTTP middleware, service methods, and DB queries

Current observability entry points:

- [`app/observability/http.py`](app/observability/http.py)
- [`app/observability/logging.py`](app/observability/logging.py)
- [`app/observability/metrics.py`](app/observability/metrics.py)
- [`app/observability/tracing.py`](app/observability/tracing.py)

Governed observability rules live in [`documentation/08_Governance/observability.md`](documentation/08_Governance/observability.md).

## Testing

The implemented slice is covered by tests for:

- case create, list, detail, status update, and archive
- duplicate active-case prevention
- auth and permission failures
- audit logging
- member, provider, and pharmacy reuse behavior
- idempotency
- settings and migrations
- metrics exposure

Key files:

- [`tests/test_case_api.py`](tests/test_case_api.py)
- [`tests/test_migrations.py`](tests/test_migrations.py)
- [`tests/test_settings.py`](tests/test_settings.py)

## Governed Documentation

If you are changing system behavior, start with the governed docs:

- [`documentation/00_master_index.md`](documentation/00_master_index.md) - top-level architecture and documentation index
- [`documentation/03_Workflows/intake_workflow.md`](documentation/03_Workflows/intake_workflow.md) - governed intake workflow target state
- [`documentation/04_Rules/`](documentation/04_Rules/) - deterministic rule documents
- [`documentation/08_Governance/service_rules.md`](documentation/08_Governance/service_rules.md) - service-layer contribution rules
- [`documentation/08_Governance/observability.md`](documentation/08_Governance/observability.md) - logs, metrics, tracing, and telemetry constraints

## Recommended Next Steps

The next highest-value milestones are:

1. implement intake and eligibility ingestion
2. expose tasks, barriers, and contact attempts as first-class workflows
3. emit governed domain events for downstream automation
4. build projections and queue-oriented operational views
5. wire the observability foundation into a local Collector and dashboards
