# Master Index

## Metadata
Document ID: PRD-MASTER-001
Status: Active
Version: 1.0.0
Last Updated: 2026-03-01
Owner: José Palomino
Layer: Product
System Version Alignment: 1.0.0

---

## System Purpose

This repository defines the authoritative specification for the Medication Adherence SaaS Platform.

The platform is built around a MeasureCase-centered, episode-based domain model.

Each MeasureCase represents a single eligibility episode for a specific Member and Measure combination.

MeasureCases are created only when eligibility criteria are met and are permanently archived when eligibility ends.

The system supports event-driven automation, voice-agent integrations, deterministic state transitions, and scalable dashboard projections.

This repository serves as the single source of truth for platform architecture.

---

## Lifecycle Model Overview

### 1. Eligibility-Driven Creation

A MeasureCase is created only when a Member meets eligibility criteria for a specific Measure.

No MeasureCase exists without eligibility.

---

### 2. Episode-Based Lifecycle

Each MeasureCase represents one distinct eligibility episode.

If eligibility ends:

- The MeasureCase transitions to `Closed_Ineligible`
- The MeasureCase then transitions to `Archived`
- Archived cases become historical and immutable

---

### 3. Re-Eligibility

If a Member becomes eligible again for the same Measure:

- A new MeasureCase is created
- A new CaseID is generated
- The prior archived case remains unchanged
- Episode continuity may be linked via reference IDs

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

1. MeasureCase is the aggregate root
2. Each Member may have multiple MeasureCases (one per eligible measure)
3. Each MeasureCase represents one eligibility episode
4. Domain defines state and invariants
5. Rules govern valid state transitions
6. Automation reacts to domain events
7. Dashboards project domain state
8. Documents are versioned and governed

---

## High-Level Architecture

### 01_Product

Defines product strategy, positioning, and roadmap.

---

### 02_Domain

Defines core entities and aggregate roots.

Aggregate Root:
- measure_case.md

Supporting Entities:
- member.md
- measure.md
- contact_attempt.md
- intervention.md
- escalation.md

---

### 03_Workflows

Defines orchestration logic built on top of domain entities.

- workflow_overview.md
- intake_workflow.md
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

Dashboards reflect current and historical MeasureCase states.

---

### 08_Governance

Defines documentation schema and versioning standards.

- governance.md

---

### 99_Archive

Stores deprecated or historical specifications.