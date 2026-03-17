# Case

## Metadata

Document ID: DOM-CASE-001
Status: Active
Version: 0.1.2
Last Updated: 2026-03-15
Owner: José Palomino
Layer: Domain
Parent Document: PRD-MASTER-001

---

## Purpose

The **Case** is the aggregate root and main operational rescue record for one Member.

It is created from exactly one Referral and serves as the consistency boundary for the work required to resolve that member's rescue episode.

Case is the center of operational state. It tracks what work exists, what barriers are present, and what measures are currently being addressed.

---

## Entity Definition

**Aggregate Root:** Case

A Case represents one active or historical rescue effort for one Member.

Case is the aggregate root because it governs:

- case lifecycle state
- contained Measures
- case-level Barriers
- case-scoped Tasks

ContactAttempt is intentionally not owned directly by Case. Communication events are modeled separately and linked back to case work through TaskContactAttempt.

---

## Relationships

- one Case belongs to one Member
- one Case is linked to exactly one Referral
- one Case has many Measures
- one Case has many Barriers
- one Case has many Tasks

Case connects to ContactAttempts indirectly:

- one Case has many Tasks
- one Task can link to many ContactAttempts through TaskContactAttempt

This allows one provider or pharmacy call to advance work for multiple Cases without forcing ContactAttempt to belong to only one Case.

---

## Core Attributes

### Identity

- `CaseID` (UUID)
- `MemberID`
- `ReferralID`

### Lifecycle

- `Status` - Initial working values: `open`, `in_progress`, `on_hold`, `closed`, `archived`
- `OpenedAt`
- `ClosedAt` (nullable)
- `ArchivedAt` (nullable)
- `ClosedReason` (nullable)

### Work Context

- `CaseSummary` (nullable)
- `Priority` (nullable)

### Audit

- `CreatedAt`
- `UpdatedAt`

---

## Domain Responsibilities

Case is responsible for:

- representing the member's operational rescue episode
- enforcing case lifecycle rules
- governing Measures, Barriers, and Tasks within its boundary
- maintaining the active work context for the member

Case is not responsible for:

- preserving the original intake snapshot
- directly owning every communication event
- serving as a shared communication log across multiple members

---

## Aggregate Boundary

The current working aggregate boundary is:

- Case
- Measure
- Barrier
- Task

ContactAttempt remains outside the Case aggregate because:

- one ContactAttempt can relate to multiple Tasks
- those Tasks may belong to different Cases
- one real-world call or fax should stay modeled as one event

---

## Invariants

The following invariants should hold:

- every Case must belong to exactly one Member
- every Case must have exactly one Referral
- every Referral must create exactly one Case
- a Member should have at most one active Case at a time in this workflow
- archived Cases are terminal
- Tasks, Measures, and Barriers within a Case must all reference that same Case
- a ContactAttempt may advance Case work, but must do so through Task linkage rather than direct Case ownership

---

## Notes for v1

The initial Case model is intentionally simple.

It should be strong enough to support:

- intake
- work management
- barrier tracking
- task execution
- clean linkage to communication events

Detailed routing, SLA, assignment, and automation rules can be layered on later without changing the Case's core role.

---

## Version History

Version 0.1.2 - 2026-03-15 - Normalized metadata formatting for the active documentation set.
Version 0.1.1 - 2026-03-14 - Added formal version history tracking to align the document with governance requirements.
Version 0.1.0 - 2026-03-11 - Initial Case domain specification established.
