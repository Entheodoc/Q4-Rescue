# Q4-Rescue

Q4-Rescue is the backend foundation for a medication adherence operations platform.

The project is centered on a Case-based rescue workflow: one referral creates one operational case for one member, and that case may contain multiple measures, medications, barriers, tasks, and communication events. The current backend supports a normalized rescue graph rather than the earlier flat single-measure case model.

## Purpose

In practical terms, this system is intended to help:

- identify members who need adherence rescue
- represent rescue work in a durable domain model
- track case lifecycle and status changes
- prevent duplicate active cases for the same member
- support future automation, event handling, and outreach workflows

The current code is a backend service, not yet a full product.

## Current State

What exists today:

- a FastAPI app in [app/main.py](/Applications/Q4-Rescue/app/main.py)
- a SQLite database in [q4_rescue.sqlite3](/Applications/Q4-Rescue/q4_rescue.sqlite3)
- a database schema in [app/persistence/schema.sql](/Applications/Q4-Rescue/app/persistence/schema.sql)
- a Case-centered domain model in [app/domain](/Applications/Q4-Rescue/app/domain)
- repository classes for persistence in [app/persistence/repositories](/Applications/Q4-Rescue/app/persistence/repositories)
- API endpoints for case creation, retrieval, listing, status updates, and archiving in [app/api/routes/case.py](/Applications/Q4-Rescue/app/api/routes/case.py)
- idempotency support for safe repeated create requests
- end-to-end persistence for nested `Member`, `Referral`, `Measure`, `Medication`, `MedicationProvider`, and `MedicationPharmacy` data during case creation

What does not exist yet:

- a completed eligibility ingestion flow
- a task-management API or operator work queue
- domain events wired into downstream automation
- projections or read models for operational reporting
- a frontend or dashboard
- voice agent integration
- broad business-rule and workflow test coverage

## Domain-Driven Design Direction

This project follows a domain-driven design shape.

The current implementation uses `Case` as the aggregate root and stores a normalized rescue graph:

- `Member`
- `Referral`
- `Case`
- `Measure`
- `Medication`
- `Provider`
- `Pharmacy`
- `MedicationProvider`
- `MedicationPharmacy`

Instead of treating the system as only database CRUD, the code models business rules directly in domain objects. For example:

- required member, referral, measure, and medication data is validated at creation time
- PDC and target thresholds are constrained at the measure level
- lifecycle transitions are controlled through methods like `start()`, `hold()`, `close()`, and `archive()`
- duplicate active cases for the same member are prevented at both the repository and database-index levels

That is the clearest sign that the project is being structured around domain behavior rather than only API endpoints.

## Domain Vocabulary

The current agreed vocabulary is:

- `Member`
  The persistent canonical person record across time.
- `Referral`
  One referral received. This starts the process, and the same member may have multiple referrals over time.
- `Case`
  The main member-level operational record that represents the overall rescue effort for that member.
- `Measure`
  One measure-level problem or opportunity inside a case.
- `Medication`
  One medication-level record inside a measure.
- `Barrier`
  One case-level obstacle preventing rescue resolution.
- `Provider`
  A shared provider actor that may appear across many medications and cases.
- `Pharmacy`
  A shared pharmacy actor that may appear across many medications and cases.
- `MedicationProvider`
  The provider-specific relationship object for one medication.
- `MedicationPharmacy`
  The pharmacy-specific relationship object for one medication, including fill and refill state.
- `Task`
  A task created to do something.
- `ContactAttempt`
  One logged communication attempt and its result. This can be for a member, pharmacy, or provider.
- `TaskContactAttempt`
  The linking object between one task and one communication event when a single event advances one or more tasks.

In plain English, the intended flow is:

1. A `Referral` arrives.
2. The system creates one `Case` from that `Referral`.
3. The `Case` contains one or more `Measure` records.
4. Each `Measure` contains one or more `Medication` records.
5. Each `Medication` may link to Providers and Pharmacies through relationship objects.
6. The system creates `Task` records to act on the case.
7. Each completed or attempted contact is logged as a `ContactAttempt`.
8. `TaskContactAttempt` links those communication events back to the work they advanced.

The active implementation now uses this vocabulary for the core create/read/status case flow, even though some areas such as tasks, barriers, and contact attempts are not fully exposed in API workflows yet.

## Case Lifecycle

The implemented case statuses are:

- `open`
- `in_progress`
- `on_hold`
- `closed`
- `archived`

The current transition rules are:

- `open -> in_progress`
- `open -> on_hold`
- `on_hold -> in_progress`
- `on_hold -> open`
- `in_progress -> on_hold`
- `in_progress -> closed`
- `closed -> archived`

The system also prevents creating another active case for the same member unless the prior case has reached a terminal state.

## Current Architecture

The project is organized roughly as follows:

- [app/domain](/Applications/Q4-Rescue/app/domain)
  Domain entities, errors, and eventually domain events.
- [app/application](/Applications/Q4-Rescue/app/application)
  Intended for use cases and command handlers. Mostly stubbed right now.
- [app/persistence](/Applications/Q4-Rescue/app/persistence)
  SQLite connection setup, schema, and repositories.
- [app/api](/Applications/Q4-Rescue/app/api)
  FastAPI routes and request schemas.
- [app/automation](/Applications/Q4-Rescue/app/automation)
  Intended for event dispatch and downstream automation handlers. Currently empty.
- [app/projection](/Applications/Q4-Rescue/app/projection)
  Intended for read models or reporting views. Currently empty.
- [app/rules](/Applications/Q4-Rescue/app/rules)
  Intended for business rules such as eligibility logic. Currently empty.

## Repository Guide

This section explains the project structure in beginner-friendly terms.

### `api/`

This is the entry door into the backend.

Its job is to receive requests from outside the system and pass them inward.

It answers questions like:

- what endpoints exist?
- what input shape is allowed?
- what response should go back?

In this project:

- [app/api/routes/case.py](/Applications/Q4-Rescue/app/api/routes/case.py)
- [app/api/schemas/case.py](/Applications/Q4-Rescue/app/api/schemas/case.py)

Short version:
`api/` is how the outside world talks to the app.

### `application/`

This is the coordinator layer.

Its job is to organize workflows and use cases.

It answers questions like:

- when input comes in, what should happen next?
- which domain objects should be created or updated?
- what steps should happen in order?

This folder is mostly empty right now, but it is the natural place for things like:

- ingest an incoming row
- create a rescue case
- create work items
- trigger automation

Short version:
`application/` is the workflow layer.

### `domain/`

This is the business meaning of the system.

Its job is to define the main business objects and the rules they must follow.

It answers questions like:

- what is a case?
- what states are allowed?
- what makes data valid?
- what business behavior is allowed?

In this project:

- [app/domain/case.py](/Applications/Q4-Rescue/app/domain/case.py)
- [app/domain/errors.py](/Applications/Q4-Rescue/app/domain/errors.py)

Current domain files include:

- [app/domain/case.py](/Applications/Q4-Rescue/app/domain/case.py)
- [app/domain/member.py](/Applications/Q4-Rescue/app/domain/member.py)
- [app/domain/referral.py](/Applications/Q4-Rescue/app/domain/referral.py)
- [app/domain/measure.py](/Applications/Q4-Rescue/app/domain/measure.py)
- [app/domain/medication.py](/Applications/Q4-Rescue/app/domain/medication.py)
- [app/domain/provider.py](/Applications/Q4-Rescue/app/domain/provider.py)
- [app/domain/pharmacy.py](/Applications/Q4-Rescue/app/domain/pharmacy.py)
- [app/domain/medication_provider.py](/Applications/Q4-Rescue/app/domain/medication_provider.py)
- [app/domain/medication_pharmacy.py](/Applications/Q4-Rescue/app/domain/medication_pharmacy.py)

Short version:
`domain/` contains the real business concepts and rules.

### `persistence/`

This is the storage layer.

Its job is to save and load information.

It answers questions like:

- where is data stored?
- how is it written?
- how is it retrieved?

In this project:

- [app/persistence/db.py](/Applications/Q4-Rescue/app/persistence/db.py)
- [app/persistence/schema.sql](/Applications/Q4-Rescue/app/persistence/schema.sql)
- [app/persistence/repositories/case_repo.py](/Applications/Q4-Rescue/app/persistence/repositories/case_repo.py)
- [app/persistence/repositories/idempotency_repo.py](/Applications/Q4-Rescue/app/persistence/repositories/idempotency_repo.py)

Short version:
`persistence/` is the database and storage logic.

### `automation/`

This is the automatic-action layer.

Its job is to react when something important happens and trigger follow-up work.

Examples:

- queue a voice call
- retry outreach
- assign human follow-up
- send a notification

This folder is mostly empty right now, but that is its intended role.

Short version:
`automation/` is what the system does automatically.

### `projection/`

This is the reporting and view layer.

Its job is to shape data into forms that are easier to read, filter, and operate on.

Examples:

- dashboard views
- work queues
- summary tables
- reporting outputs

This folder is mostly empty right now.

Short version:
`projection/` is where read-friendly views of the data would live.

### `rules/`

This is the decision-logic layer.

Its job is to hold specific business rules that help determine what should happen.

Examples:

- does this member qualify for rescue?
- which measure gaps should be created?
- which outreach path should be used?

This folder is also mostly empty right now.

Short version:
`rules/` contains decision logic.

### `shared/`

This is reusable support code.

Its job is to hold small helpers used by multiple parts of the app.

Examples:

- ID helpers
- time helpers
- utility functions

Short version:
`shared/` contains common reusable support code.

### `settings.py`

This file contains configuration.

Its job is to store app settings such as:

- database path
- environment options
- later, possibly service URLs or API keys

In this project:

- [app/settings.py](/Applications/Q4-Rescue/app/settings.py)

Short version:
`settings.py` is app configuration.

### `main.py`

This is the starting point of the backend.

Its job is to:

- create the FastAPI app
- initialize the database
- register routes

In this project:

- [app/main.py](/Applications/Q4-Rescue/app/main.py)

Short version:
`main.py` is where the backend starts.

### `__pycache__/`

This is a Python-generated cache folder.

You usually do not edit it and do not need it to understand the project.

Short version:
`__pycache__/` is auto-generated Python cache.

## Quick Cheat Sheet

- `api/` = receive requests
- `application/` = coordinate workflow
- `domain/` = business meaning and rules
- `persistence/` = save and load data
- `automation/` = automatic follow-up actions
- `projection/` = reporting and work views
- `rules/` = decision logic
- `shared/` = reusable helpers
- `main.py` = start the app
- `settings.py` = configuration

## Implemented API

The current API supports:

- `POST /cases/`
  Create a new rescue case with nested member, referral, measure, medication, provider, pharmacy, and refill detail.
- `GET /cases`
  List all cases.
- `GET /cases/{case_id}`
  Retrieve a single normalized case graph by ID.
- `PUT /cases/{case_id}/status`
  Move a case through its lifecycle and optionally set `closed_reason`.
- `DELETE /cases/{case_id}`
  Archive a case.
- `GET /health`
  Basic health check.

## Important Existing Files

- [app/main.py](/Applications/Q4-Rescue/app/main.py)
  FastAPI entrypoint and startup DB initialization.
- [app/domain/case.py](/Applications/Q4-Rescue/app/domain/case.py)
  Core domain entity and transition logic.
- [app/domain/member.py](/Applications/Q4-Rescue/app/domain/member.py)
  Canonical member entity.
- [app/domain/referral.py](/Applications/Q4-Rescue/app/domain/referral.py)
  Intake snapshot and referral entity.
- [app/domain/measure.py](/Applications/Q4-Rescue/app/domain/measure.py)
  Measure-level rescue entity and PDC carrier.
- [app/domain/medication.py](/Applications/Q4-Rescue/app/domain/medication.py)
  Measure-scoped medication entity.
- [app/domain/errors.py](/Applications/Q4-Rescue/app/domain/errors.py)
  Domain-level exception types.
- [app/persistence/schema.sql](/Applications/Q4-Rescue/app/persistence/schema.sql)
  SQLite schema for the normalized rescue model and idempotency keys.
- [app/persistence/db.py](/Applications/Q4-Rescue/app/persistence/db.py)
  Database connection, schema initialization, and legacy MeasureCase migration.
- [app/persistence/repositories/case_repo.py](/Applications/Q4-Rescue/app/persistence/repositories/case_repo.py)
  Persistence logic for normalized case graphs.
- [app/persistence/repositories/idempotency_repo.py](/Applications/Q4-Rescue/app/persistence/repositories/idempotency_repo.py)
  Persistence logic for idempotent create requests.
- [app/api/routes/case.py](/Applications/Q4-Rescue/app/api/routes/case.py)
  Current case-management API.

## What Was Likely Planned Next

Based on the folder structure and stub files, the next intended milestone was probably:

1. ingest adherence or eligibility data into the system
2. evaluate business rules to determine when a case should be created
3. create or update rescue cases automatically
4. emit domain events when a case is created or changes state
5. trigger downstream automations such as assignment, outreach, reminders, or voice workflows
6. build projections or work queues for human operators

That direction aligns with medication adherence operations and with the unfinished modules currently in the repo.

## Missing Pieces

The following areas are present only as placeholders or partial scaffolding:

- [app/application/commands/ingest_eligibility_row.py](/Applications/Q4-Rescue/app/application/commands/ingest_eligibility_row.py)
- [app/api/routes/eligibility.py](/Applications/Q4-Rescue/app/api/routes/eligibility.py)
- [app/api/schemas/eligibility.py](/Applications/Q4-Rescue/app/api/schemas/eligibility.py)
- [app/rules/eligibility.py](/Applications/Q4-Rescue/app/rules/eligibility.py)
- [app/domain/events.py](/Applications/Q4-Rescue/app/domain/events.py)
- [app/automation/dispatcher.py](/Applications/Q4-Rescue/app/automation/dispatcher.py)
- [app/automation/handlers/case_created.py](/Applications/Q4-Rescue/app/automation/handlers/case_created.py)
- [app/projection/models.py](/Applications/Q4-Rescue/app/projection/models.py)
- [app/projection/updater.py](/Applications/Q4-Rescue/app/projection/updater.py)
- [app/persistence/repositories/work_item_repo.py](/Applications/Q4-Rescue/app/persistence/repositories/work_item_repo.py)
- [tests](/Applications/Q4-Rescue/tests)

## Recommended Next Steps

The highest-value next steps are:

1. Define the real business workflow in writing.
   Clarify what inputs create a case, which measures matter, what thresholds matter, and what outcomes count as resolved.

2. Implement eligibility ingestion.
   Build the path from an incoming referral or source record into application logic that creates or updates a `Case` graph, including its `Measure` and `Medication` records.

3. Add domain events.
   When a case is created or transitions state, emit explicit events so automation logic is not buried inside the API layer.

4. Add work items and queue views.
   Cases alone are not enough for operations. The system needs a way to represent actionable tasks for agents, staff, or automations.

5. Add tests around domain and ingestion rules.
   The most important logic in this project is business logic, so that should be covered first.

6. Decide how voice agents fit.
   A voice agent should likely sit on top of a stable case/work-item model rather than being introduced before the core workflow is defined.

## Development Notes

- The project uses SQLite for local persistence.
- There are sample rows already stored in the local database.
- The continuation prompt file exists at [PROMPT_NEXT_CHAT.md](/Applications/Q4-Rescue/PROMPT_NEXT_CHAT.md), but it is currently just a placeholder.

## Summary

Q4-Rescue is currently a partially built backend for medication adherence rescue operations.

It already has:

- a domain model
- a case lifecycle
- persistence
- a working API

It does not yet have:

- automated intake
- orchestration
- agent workflows
- operator tooling
- tests

The next real milestone is to turn the current case-management backend into an actual workflow engine for medication adherence rescue.
