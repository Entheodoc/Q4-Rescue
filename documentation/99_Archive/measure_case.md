# MeasureCase Aggregate Root (Archived)

## Metadata

Document ID: DOM-MEASURECASE-001  
Status: Archived  
Version: 2.0.0  
Last Updated: 2026-03-11  
Owner: José Palomino  
Layer: Domain  
Parent Document: PRD-MASTER-001  

---

## Archive Note

This document is archived.

It describes the legacy `MeasureCase`-centered starter architecture that existed before the rescue operations model adopted `Case` as the aggregate root.

It is preserved for historical reference only and is no longer the active domain specification.

---

## Purpose

The **MeasureCase** is the aggregate root of the Medication Adherence Platform domain.

It represents a single eligibility episode for a specific:

- Member  
- Measure  

A MeasureCase exists only when eligibility criteria are satisfied.

Each MeasureCase:

- Encapsulates all domain state related to one eligibility episode
- Governs consistency boundaries for related entities
- Enforces lifecycle integrity
- Emits domain events reflecting state changes

Archived MeasureCases are immutable and never reactivated.

This document defines:

- Domain state
- Lifecycle states
- Invariants
- Aggregate relationships
- Constraints

It does **not** define workflow orchestration, automation logic, UI behavior, or state transition rules.

---

## Entity Definition

**Aggregate Root:** MeasureCase  

A MeasureCase is uniquely identified and version-controlled.

Each instance represents:

> One Member + One Measure + One Eligibility Episode

It is the authoritative consistency boundary for:

- ContactAttempts
- Interventions
- Escalations
- Episode-level adherence state

No external entity may modify internal state outside defined rule-governed transitions.

---

## Core Attributes

### Identity

- `CaseID` (UUID) – Globally unique identifier
- `MemberID` – Reference to Member
- `MeasureID` – Reference to Measure
- `EpisodeNumber` – Sequential number per Member + Measure
- `PreviousCaseID` (nullable) – Reference to prior archived episode

---

### Eligibility

- `EligibilityStartDate`
- `EligibilityEndDate` (nullable while active)
- `EligibilitySource` (e.g., CMS feed, internal logic)

---

### Lifecycle

- `CurrentState`
- `ArchivedAt` (nullable)
- `ClosedReason` (nullable)

---

### Adherence Context

- `BaselinePDC`
- `CurrentPDC`
- `AdherenceStatus`
- `RiskLevel`
- `GoalThreshold` (e.g., 80%)

---

### Episode Metrics

- `TotalContactAttempts`
- `TotalSuccessfulContacts`
- `TotalInterventions`
- `LastActivityDate`

---

### Audit

- `CreatedAt`
- `CreatedBy`
- `UpdatedAt`
- `Version` (optimistic concurrency control)

---

## Lifecycle States

Lifecycle states are defined in the Domain layer.

Valid states:

1. `Eligible_Active`
2. `Engaged`
3. `Monitoring`
4. `Closed_Successful`
5. `Closed_Unsuccessful`
6. `Closed_Ineligible`
7. `Archived`

State transitions are governed by RULE documents.

Domain defines only the state model.

---

## State Invariants

The following invariants must always hold:

---

### Episode Integrity

- A MeasureCase must reference exactly one Member and one Measure.
- EpisodeNumber must be unique per Member + Measure combination.
- EpisodeNumber must be monotonically increasing per Member + Measure.
- EpisodeNumber values must never be reused.
- EligibilityStartDate must be defined at creation.
- EligibilityEndDate must not precede EligibilityStartDate.

---

### Active Case Uniqueness

- At most one MeasureCase in a non-terminal state may exist for a Member + Measure combination.
- Closed and Archived cases may coexist historically.
- No two active or non-terminal cases may overlap for the same Member + Measure.

---

### Creation Invariants

- A MeasureCase can only be created if eligibility criteria are satisfied.
- No MeasureCase may exist without eligibility.

---

### Archival Invariants

- Archived state is terminal.
- Archived cases are immutable.
- ArchivedAt must be populated when CurrentState = Archived.
- Archived cases must never transition to any other state.

---

### Closure Invariants

- Closed states must precede Archived.
- ClosedReason must be populated for any Closed_* state.

---

### Re-Eligibility Invariants

- Re-eligibility must create a new MeasureCase.
- A previously Archived case must never be reactivated.
- PreviousCaseID may reference prior archived episode for continuity.
- Re-eligibility must generate a new CaseID and increment EpisodeNumber.

---

### Consistency Boundary

All subordinate entities must reference exactly one MeasureCase.

No subordinate entity may exist outside a MeasureCase boundary.

---

### Aggregate Growth Boundaries

To preserve SaaS scalability and bounded aggregate integrity:

- The MeasureCase aggregate must remain bounded in size.
- Subordinate entity collections (ContactAttempts, Interventions, Escalations, Snapshots) must not grow unbounded.
- Historical or high-frequency operational data may be projected to external historical storage.
- The aggregate must maintain sufficient state for consistency but must not function as an infinite event log.

---

## Emitted Domain Events

The Domain may declare events but does not define automation behavior.

Possible emitted events:

- `MeasureCaseCreated`
- `MeasureCaseStateChanged`
- `MeasureCaseClosed`
- `MeasureCaseArchived`
- `EligibilityEnded`
- `ReEligibilityDetected`
- `AdherenceThresholdCrossed`
- `RiskLevelChanged`

Event definitions and handling logic are defined in:

`06_Automation/domain_events.md`

Domain does not define trigger logic.

---

## Aggregate Relationships

The MeasureCase aggregate root contains or governs:

### Child Entities (within boundary)

- ContactAttempt
- Intervention
- Escalation
- EpisodeAdherenceSnapshot

These entities:

- Cannot exist independently
- Must reference CaseID
- Cannot outlive the MeasureCase lifecycle

---

### External References (outside boundary)

- Member
- Measure
- Prescriber (via reference)
- Pharmacy (via reference)

These are separate aggregates or reference entities.

---

## Constraints

### Uniqueness

- CaseID must be globally unique.
- EpisodeNumber must be unique per Member + Measure.
- Only one non-terminal MeasureCase may exist per Member + Measure.

---

### Immutability

- Archived MeasureCases are read-only.
- Historical Episode data must not be modified.

---

### Concurrency

- Version field must enforce optimistic concurrency.
- State transitions must validate version before commit.

---

### Deterministic State Model

- State transitions must be rule-driven.
- No workflow may directly alter lifecycle without rule validation.

---

### SaaS Scalability Constraints

- CaseID must be globally unique.
- Domain must be multi-tenant safe (TenantID may be introduced in future versions).
- Aggregate size must remain bounded.
- Historical events should be append-only.
- The aggregate must remain safe for horizontal scaling.

---

## Dependencies

This document depends on:

- PRD-MASTER-001  
- GOV-GOVERNANCE-001  

Future dependencies:

- RULE-ELIGIBILITY-001
- RULE-STATE-TRANSITIONS-001
- AUTO-DOMAIN-EVENTS-001
- DATA-DICTIONARY-001

---

## Version History

Version 1.1.0 – 2026-03-01 – Strengthened invariants, promoted active-case uniqueness to invariant, added bounded aggregate discipline.
Version 1.0.0 – 2026-03-01 – Initial MeasureCase aggregate root specification established.
