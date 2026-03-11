# Master Index

## Metadata
Document ID: PRD-MASTER-001
Status: Active
Version: 2.1.0
Last Updated: 2026-03-11
Owner: José Palomino
Layer: Product
System Version Alignment: 1.0.0

---

## System Purpose

This repository defines the authoritative specification for the Medication Adherence SaaS Platform.

The platform is built around a rescue operations domain model centered on:

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

The system supports event-driven automation, voice-agent integrations, deterministic state transitions, and scalable dashboard projections.

This repository serves as the single source of truth for platform architecture.

Legacy note:

The repository still contains archived documentation that uses the older `MeasureCase` name. Those references describe the starter system, not the current target domain model.

---

## Lifecycle Model Overview

### 1. Eligibility-Driven Creation

A Referral is received for a Member and intake determines whether rescue work should be opened.

If rescue work is needed, one Case is created from that Referral.

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
- Automation reacts to domain events
- Workflow orchestration does not modify lifecycle rules
- Dashboards reflect both current and historical episode states

---

## Architectural Model

### Core Design Principles

1. Member is the persistent person identity across time
2. Each Referral creates exactly one Case
3. Case is the aggregate root for rescue operations
4. Case governs Measures, Barriers, and Tasks within its boundary
5. ContactAttempt is communication-scoped and may relate to multiple Tasks
6. Domain defines state and invariants
7. Rules govern valid state transitions
8. Automation reacts to domain events
9. Dashboards project domain state
10. Documents are versioned and governed

---

## High-Level Architecture

### 01_Product

Defines product strategy, positioning, and roadmap.

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

- workflow_overview.md
- intake_workflow.md
- rescue_workflow_overview.md
- contact_workflow.md
- assessment_workflow.md
- intervention_workflow.md
- follow_up_workflow.md
- closure_workflow.md

Workflows orchestrate domain behavior but do not define business rules.

---

### 04_Rules

Defines deterministic system rules and constraints.

- state_transition_rules.md
- eligibility_rules.md
- escalation_rules.md
- adherence_rules.md

Rules govern domain behavior and lifecycle transitions.

---

### 05_Data_Model

Defines structural persistence and entity relationships.

- data_dictionary.md
- entity_relationships.md

---

### 06_Automation

Defines event-driven logic and integrations.

- domain_events.md
- trigger_logic.md
- voice_agent_integration.md

Automation reacts to domain events and may emit new events.

---

### 07_Dashboard

Defines projection and visualization layer.

- kpi_definitions.md
- dashboard_specifications.md

Dashboards reflect current and historical rescue operations state.

---

### 08_Governance

Defines documentation schema and versioning standards.

- governance.md

---

### 99_Archive

Stores deprecated or historical specifications.
