# TaskContactAttempt

## Metadata

Document ID: DOM-TASKCONTACTATTEMPT-001
Status: Active
Version: 0.1.0
Last Updated: 2026-03-11
Owner: Jose Palomino
Layer: Domain
Parent Document: PRD-MASTER-001

---

## Purpose

**TaskContactAttempt** is the linking object between Task and ContactAttempt.

It exists because:

- one Task may require multiple ContactAttempts
- one ContactAttempt may advance multiple Tasks

This is a real domain relationship, not just a technical join.

---

## Entity Definition

**Entity:** TaskContactAttempt

TaskContactAttempt records that a specific communication event affected a specific Task.

It allows the system to answer questions such as:

- which outreach attempts were made for this Task
- which Tasks were advanced by this provider call
- what effect did this call or fax have on each linked Task

---

## Relationships

- one TaskContactAttempt belongs to one Task
- one TaskContactAttempt belongs to one ContactAttempt

Together, these links create the many-to-many relationship between Task and ContactAttempt.

---

## Core Attributes

### Identity

- `TaskContactAttemptID` (UUID)
- `TaskID`
- `ContactAttemptID`

### Effect

- `EffectOnTask` (nullable)
- `Notes` (nullable)

### Audit

- `CreatedAt`

---

## Domain Responsibilities

TaskContactAttempt is responsible for:

- connecting communication events to case work
- preserving the many-to-many relationship cleanly
- allowing task-level interpretation of a shared ContactAttempt

TaskContactAttempt is not responsible for:

- owning the full communication payload
- replacing Task state
- replacing ContactAttempt outcome

---

## Invariants

The following invariants should hold:

- every TaskContactAttempt must link exactly one Task and one ContactAttempt
- the same Task and ContactAttempt pair should not be duplicated unless the domain later requires versioned effects
- TaskContactAttempt may carry task-specific interpretation of a shared ContactAttempt without redefining the ContactAttempt itself

---

## Notes for v1

This relationship object is necessary because the workflow explicitly allows one provider or pharmacy interaction to advance several Tasks across several Cases.
