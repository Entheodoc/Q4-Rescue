# Task

## Metadata

Document ID: DOM-TASK-001
Status: Active
Version: 0.1.2
Last Updated: 2026-03-15
Owner: José Palomino
Layer: Domain
Parent Document: PRD-MASTER-001

---

## Purpose

A **Task** is a unit of work created to move a Case forward.

Task is where the domain turns a known problem into actionable work.

Tasks stay case-scoped, even when one real-world communication event advances tasks from several different Cases.

---

## Entity Definition

**Entity:** Task

A Task represents one actionable piece of work inside a Case.

Examples may include:

- call member
- text member
- fax provider
- call pharmacy
- request refill
- verify fill status

Task should be granular enough to assign and track, but broad enough to represent real operational work instead of tiny technical steps.

---

## Relationships

- one Task belongs to one Case
- one Task may relate to one or more Measures
- one Task may relate to one or more Medications
- one Task may be created because of one Barrier
- one Task can link to many ContactAttempts through TaskContactAttempt

Tasks must remain case-specific.

If one provider call advances work for several members, that should still be modeled as:

- separate Tasks, one per Case
- one shared ContactAttempt
- many TaskContactAttempt links

---

## Core Attributes

### Identity

- `TaskID` (UUID)
- `CaseID`

### Classification

- `TaskType`
- `Status` - Initial working values: `open`, `in_progress`, `blocked`, `completed`, `cancelled`
- `Priority` (nullable)

### Scope

- `RelatedMeasureIDs` (nullable collection)
- `RelatedMedicationIDs` (nullable collection)
- `BarrierID` (nullable)

### Execution

- `Title`
- `Description` (nullable)
- `DueAt` (nullable)
- `CompletedAt` (nullable)
- `CancelledAt` (nullable)
- `Outcome` (nullable)

### Ownership

- `AssignedTo` (nullable)
- `AssignedQueue` (nullable)

### Audit

- `CreatedAt`
- `UpdatedAt`

---

## Domain Responsibilities

Task is responsible for:

- representing actionable case work
- tracking task lifecycle state
- tying work back to the Case
- capturing what part of the Case the work relates to
- linking work to the ContactAttempts that actually occurred

Task is not responsible for:

- representing the communication event itself
- replacing the underlying Barrier
- owning member identity or referral provenance

---

## Invariants

The following invariants should hold:

- every Task must belong to exactly one Case
- any related Measure or Medication must also belong to that same Case
- one Task may have many ContactAttempts over time
- one ContactAttempt may satisfy multiple Tasks
- task completion is independent from whether the underlying Barrier is fully resolved
- cancelling a Task does not automatically close the Case

---

## Notes for v1

The Task model should stay flexible enough to support:

- member outreach
- provider outreach
- pharmacy outreach
- non-call work such as verification or review

This flexibility is why Task should not be forced to belong to exactly one Medication.

---

## Version History

Version 0.1.2 - 2026-03-15 - Normalized metadata formatting for the active documentation set.
Version 0.1.1 - 2026-03-14 - Added formal version history tracking to align the document with governance requirements.
Version 0.1.0 - 2026-03-11 - Initial Task domain specification established.
