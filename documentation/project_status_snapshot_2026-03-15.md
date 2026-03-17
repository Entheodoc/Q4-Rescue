# Q4-Rescue Project Status Snapshot

Prepared: March 15, 2026
Repository: `Q4-Rescue`
Branch: `main`
HEAD: `54739d5`

Note:
This is a dated project snapshot captured before the March 15, 2026 documentation alignment pass. It is a status artifact, not a governed architecture document.

## Executive Summary

Q4-Rescue is no longer just a scaffold. It is a working backend foundation for a medication adherence rescue platform, with the strongest implemented slice centered on case management.

Today, the project can:

- boot a FastAPI service
- validate runtime configuration
- apply Alembic migrations at startup
- persist a normalized rescue graph in Postgres
- create, list, retrieve, update, and archive cases
- enforce authentication and permission checks
- record audit events
- support idempotent case creation
- run a passing automated test suite for the implemented case-management workflow

At the same time, the project is not yet product-ready. Major areas such as intake and eligibility, operator tasking, automation dispatch, projections and dashboards, and any frontend experience remain incomplete or only documented.

## Current Delivery Status

Overall maturity: backend foundation with one solid vertical slice

Delivery state:

- Working backend service for case operations
- Domain model and persistence are more mature than the README language suggests
- Several broader platform layers are still placeholders
- Repository is in active transition with a large uncommitted change set

Working tree summary at the time of review:

- 29 modified tracked files
- 17 untracked files

This means the project is actively moving forward, but the current state should be treated as an in-flight build rather than a clean release candidate.

## What Is Implemented

### 1. Application Runtime

The application starts through FastAPI and runs database initialization during startup. Runtime settings enforce a Postgres connection string and require token configuration when authentication is enabled.

Key files:

- `app/main.py`
- `app/settings.py`
- `app/persistence/db.py`
- `app/persistence/migrations.py`

### 2. Case Management API

The current public API supports the core case lifecycle:

- create case
- list cases
- retrieve case detail
- update case status
- archive case

Request handling includes:

- bearer-token authentication
- permission checks
- generated or propagated request IDs
- service-layer orchestration instead of route-level persistence logic

Key files:

- `app/api/routes/case.py`
- `app/api/security.py`
- `app/api/deps.py`
- `app/application/services/case_service.py`

### 3. Domain Model and Rules

The codebase now reflects a genuine case-centered domain model instead of a flat CRUD-only shape.

Implemented domain ideas include:

- `Case` as the aggregate root
- lifecycle transitions across `open`, `in_progress`, `on_hold`, `closed`, and `archived`
- duplicate active-case prevention for the same member
- measure uniqueness validation within a case
- medication-level provider and pharmacy relationship validation

Key files:

- `app/domain/case.py`
- `app/api/schemas/case.py`
- `app/persistence/repositories/case_repo.py`

### 4. Persistence Layer

The persistence model is broad and already includes tables for:

- members
- referrals
- cases
- measures
- medications
- providers
- pharmacies
- medication-provider relationships
- medication-pharmacy relationships
- barriers
- tasks
- contact attempts
- task-contact-attempt links
- audit events
- idempotency keys

This is important because the storage model is ahead of the exposed API. The backend can already represent more of the rescue domain than it currently exposes through routes.

Key file:

- `app/persistence/schema.sql`

### 5. Testing and CI

Automated test coverage exists for the currently implemented slice, including:

- create/list/detail/status/archive behavior
- duplicate active-case prevention
- auth and authorization behavior
- audit event creation
- member reuse across referrals
- provider and pharmacy reuse
- idempotent creates
- settings validation
- migration bootstrapping

GitHub Actions is configured to run tests with Postgres in CI.

Key files:

- `tests/test_case_api.py`
- `tests/test_case_domain.py`
- `tests/test_migrations.py`
- `tests/test_settings.py`
- `.github/workflows/ci.yml`

## What Is Partially Implemented or In Flight

The repository shows an architectural transition that is real, not cosmetic:

- routes now delegate to a service layer
- audit logging has been introduced
- token-based authorization has been added
- migrations and Postgres-only runtime rules are now first-class
- documentation has expanded into governed rules, data model, and automation folders

This is good progress, but the work is not fully rounded out. Several files and folders that represent the next platform layers still exist as placeholders.

Examples of empty or placeholder modules:

- `app/api/routes/eligibility.py`
- `app/application/commands/ingest_eligibility_row.py`
- `app/automation/dispatcher.py`
- `app/automation/handlers/case_created.py`
- `app/projection/models.py`
- `app/projection/updater.py`
- `app/rules/eligibility.py`
- `app/domain/events.py`

## What Is Missing

The following major product capabilities are still missing or not wired into the running application:

- completed eligibility and intake ingestion flow
- task-management API
- operator work queue
- barrier management workflows
- contact-attempt workflows
- domain-event stream for downstream automation
- reporting projections and dashboard read models
- frontend or operational dashboard
- voice-agent integration

In practical terms, the current system can manage case records, but it cannot yet support a full operations team workflow end to end.

## Documentation Status

Documentation has improved significantly and now includes a governed master index plus rule, data-model, and automation documents.

At the time of this review, there was still some drift between the docs and the code:

- the README understates current implementation depth in several areas
- the master index describes broader target-state architecture than the running code currently delivers
- some folders are documented as planned layers and still contain only placeholder files

This is a normal mid-build pattern, but it means documentation should not be treated as exact runtime truth without checking the code.

## Verification Results

Verification performed during this review:

- inspected repository structure and git state
- reviewed core runtime, API, service, schema, test, and documentation files
- ran the project test suite in the local virtual environment

Test command:

`.venv/bin/python -m unittest discover -s tests -p 'test*.py' -q`

Result:

- 19 tests passed

Important environment note:

- the system Python did not have project dependencies installed
- the repository virtual environment did have the required dependencies
- the `docker` command was not available in this session, so live local container status could not be confirmed from the terminal environment used for this review

## Main Risks

### 1. Large Uncommitted Change Set

There is a substantial amount of work sitting uncommitted on `main`. That increases risk around reviewability, rollback, and release confidence.

### 2. Feature Surface vs. Exposed API

The schema can represent tasks, barriers, and contact attempts, but the app currently exposes only case routes. This creates a gap between domain ambition and usable product functionality.

### 3. Documentation Drift

Some docs still describe future-state capabilities as if they are architectural facts, while the running system has only partially implemented them.

### 4. Operational Readiness

There is no frontend, no queue-driven operator workflow, and no reporting layer yet. That keeps the project squarely in backend-foundation territory.

## Recommended Next Steps

Priority order for moving this project forward:

1. Commit and stabilize the current architecture shift on a reviewable branch.
2. Decide the next product slice: eligibility intake or operator tasking.
3. Expose the next missing workflow through APIs rather than expanding only the schema and docs.
4. Add targeted tests for whichever next slice is chosen.
5. Align the README with the actual code so stakeholders get a truthful snapshot quickly.
6. Add release hygiene around environment setup, migration flow, and local developer bootstrapping.

## Bottom Line

Q4-Rescue is in a healthy early-platform stage. The case-management backend is real, tested, and structurally sound enough to build on. The project has clear momentum and a better technical core than a first glance at the README might suggest.

The limiting factor is not whether the project exists. It does. The limiting factor is that only one major vertical slice is truly implemented today. Everything beyond that slice is either planned, partially scaffolded, or documented ahead of delivery.
