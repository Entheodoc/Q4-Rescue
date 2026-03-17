# Master Index

## Metadata
Document ID: PRD-MASTER-001
Status: Active
Version: 2.4.0
Last Updated: 2026-03-15
Owner: José Palomino
Layer: Product
System Version Alignment: 1.0.0

---

## System Purpose

This repository defines the authoritative specification for the Q4-Rescue medication-adherence platform and the backend that is actively being built toward that model.

The active platform vocabulary is centered on:

- Member
- Referral
- Case
- Measure
- Medication
- Barrier
- Task
- ContactAttempt
- Provider
- Pharmacy
- MedicationProvider
- MedicationPharmacy
- TaskContactAttempt

In the active model, a Referral starts intake work, a Case becomes the operational rescue record for one Member, and downstream work is organized through Measures, Medications, Barriers, Tasks, and ContactAttempts, with shared Providers and Pharmacies connected through relationship objects.

This repository serves as the single source of truth for platform architecture, workflow intent, rules, and governance.

Legacy note:

The repository still contains archived documentation that uses the older `MeasureCase` name. Those references describe the starter system, not the active Case-centered model.

---

## Current Implementation Snapshot

The governed document set describes the target platform shape, but the running backend currently implements only part of that model.

Implemented today in code:

- Postgres-backed FastAPI service for case create, list, detail, status update, and archive
- service-layer orchestration, permission-gated Bearer auth, and audit logging
- normalized persistence for Member, Referral, Case, Measure, Medication, Provider, Pharmacy, MedicationProvider, MedicationPharmacy, Barrier, Task, ContactAttempt, and audit/idempotency records
- vendor-neutral observability foundation with structured logs, Prometheus metrics, request correlation, and OpenTelemetry tracing

Not implemented yet in code:

- automated intake and eligibility ingestion
- task, barrier, and contact-attempt APIs
- governed domain event emission for automation
- projections, dashboards, and queue-oriented views
- voice-agent workflows

Documents that describe target-state capabilities must label that status clearly when the code has not reached them yet.

---

## Lifecycle Model Overview

### 1. Eligibility-Driven Creation

A Referral is received for a Member and intake determines whether rescue work should be opened.

If rescue work is needed, one Case is created from that Referral.

Current implementation note:
The backend currently accepts authorized case-create payloads and enforces structural validation plus duplicate-active-case prevention, but it does not yet automate eligibility evaluation or referral ingestion.

---

### 2. Episode-Based Lifecycle

Each Case represents one distinct rescue episode for one Member.

If work is completed or terminated:

- The Case transitions to `closed`
- The Case may later transition to `archived`
- Archived cases become historical and immutable

---

### 3. Re-Eligibility

If a Member is referred again later:

- A new Referral is created
- A new Case is created
- The prior archived case remains unchanged
- Historical continuity is preserved through the shared Member

Archived cases are never reactivated.

---

### 4. Lifecycle Integrity Principles

- State transitions must follow defined rules
- Archived cases are immutable
- Automation reacts to governed domain events once implemented
- Workflow orchestration does not modify lifecycle rules
- Dashboards reflect both current and historical episode states once projections exist
- Runtime telemetry must remain distinct from audit records and domain events

---

## Architectural Model

### Core Design Principles

1. Member is the persistent person identity across time
2. Each Referral creates exactly one Case
3. Case is the aggregate root for rescue operations
4. Case governs Measures, Barriers, and Tasks within its boundary
5. ContactAttempt is communication-scoped and may relate to multiple Tasks
6. Domain defines state and invariants
7. Rules govern valid state transitions and intake gates
8. Automation reacts to domain events rather than ad hoc route logic
9. Dashboards project domain state rather than define it
10. Logs, metrics, traces, audit records, and domain events are separate system artifacts
11. Documents are versioned and governed

---

## High-Level Architecture

### 01_Product

Defines product strategy, implementation status framing, and roadmap.

---

### 02_Domain

Defines core entities and aggregate roots.

Working entity specifications:

- case.md
- barrier.md
- member.md
- referral.md
- measure.md
- medication.md
- provider.md
- pharmacy.md
- medication_provider.md
- medication_pharmacy.md
- task.md
- contact_attempt.md
- task_contact_attempt.md

Archived legacy specifications:

- ../99_Archive/measure_case.md

---

### 03_Workflows

Defines orchestration logic built on top of domain entities.

- intake_workflow.md
- rescue_workflow_overview.md
- ../Medication Adherence Workflow_v_212.md

Workflows orchestrate domain behavior but do not define business rules.

`rescue_workflow_overview.md` is a draft visual reference for design conversations, while `intake_workflow.md` remains the governed workflow contract and now explicitly distinguishes target-state flow from the currently implemented backend slice.

Supplemental note:
`../Medication Adherence Workflow_v_212.md` is retained as detailed operational source material. It uses business-language terms such as "prescriber" and "PCP"; in the active domain model those map to `Provider` and a possible future member-to-provider relationship rather than separate entities.

---

### 04_Rules

Defines deterministic system rules and constraints.

- state_transition_rules.md
- eligibility_rules.md
- adherence_rules.md
- escalation_rules.md

These documents define the lifecycle contract, case-opening gate, adherence interpretation baseline, and escalation handling model.

---

### 05_Data_Model

Defines structural persistence and entity relationships.

- entity_relationships.md

The live persistence shape is implemented in `app/persistence/schema.sql` and Alembic migrations, with governed structural intent described in this layer.

---

### 06_Automation

Defines event-driven logic and integrations.

- domain_events.md

This layer documents planned domain event contracts separately from audit logging and runtime telemetry. A governed domain event stream is not yet implemented in the backend.

---

### 07_Dashboard

Defines projection and visualization layer.

Current status:
This layer is reserved in the documentation model but does not yet have standalone governed dashboard documents in this repository.

Dashboards are expected to reflect current and historical rescue operations state once the projection layer is designed and implemented.

---

### 08_Governance

Defines documentation standards and repository-wide engineering conventions.

- governance.md
- service_rules.md
- observability.md

Working spreadsheets in `documentation/*.xlsx` are supporting source artifacts, not part of the governed Markdown documentation set, and should be de-identified before they are stored in the repository.

---

### 99_Archive

Stores deprecated or historical specifications.

---

## Version History

Version 2.4.0 - 2026-03-15 - Added explicit implementation-status framing, incorporated the observability governance document, and clarified runtime telemetry boundaries across the architecture.
Version 2.3.1 - 2026-03-15 - Clarified that the rescue workflow overview is a draft visual reference and normalized active documentation metadata references.
Version 2.3.0 - 2026-03-14 - Added governed Rules, Data Model, and Automation documents and aligned the master index to the expanded documentation set.
Version 2.2.0 - 2026-03-14 - Aligned the master index with the current documentation tree, added the service rules governance document, and added formal version history tracking.
Version 2.1.0 - 2026-03-11 - Established the Case-centered documentation baseline carried forward into the current repository structure.
