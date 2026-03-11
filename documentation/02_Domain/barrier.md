# Barrier

## Metadata

Document ID: DOM-BARRIER-001
Status: Active
Version: 0.1.0
Last Updated: 2026-03-11
Owner: Jose Palomino
Layer: Domain
Parent Document: PRD-MASTER-001

---

## Purpose

A **Barrier** is an obstacle preventing a Case from being resolved successfully.

Barriers explain why rescue work is needed or why progress is blocked.

In the current domain direction, Barrier is modeled at the Case level by default because many real barriers apply across multiple medications or measures for the same member.

---

## Entity Definition

**Entity:** Barrier

A Barrier is a case-scoped business object that captures one meaningful obstacle to resolution.

Examples may include:

- refill needed
- cannot reach member
- language mismatch
- provider authorization needed
- pharmacy issue
- cost or affordability issue

Barrier exists so the domain can separate:

- what problem exists
- what work should be created to address it

---

## Relationships

- one Barrier belongs to one Case
- one Barrier may trigger zero or many Tasks

Barrier may later gain optional links to a specific Measure or Medication if operational workflows prove that level of precision is necessary, but that is not the default v1 design.

---

## Core Attributes

### Identity

- `BarrierID` (UUID)
- `CaseID`

### Classification

- `BarrierType`
- `BarrierStatus` - Initial working values: `open`, `resolved`, `dismissed`
- `Severity` (nullable)

### Description

- `Title`
- `Description` (nullable)

### Timing

- `IdentifiedAt`
- `ResolvedAt` (nullable)

### Audit

- `CreatedAt`
- `UpdatedAt`

---

## Domain Responsibilities

Barrier is responsible for:

- recording that a specific obstacle exists
- describing the nature of that obstacle
- showing whether the obstacle still blocks progress
- providing a reason for downstream Task creation

Barrier is not responsible for:

- carrying all execution history
- representing the work itself
- acting as a substitute for Task or ContactAttempt

---

## Invariants

The following invariants should hold:

- every Barrier must belong to exactly one Case
- a Barrier cannot exist without a Case
- resolved Barriers must have a resolution timestamp or equivalent closure marker
- dismissing a Barrier is not the same as resolving it
- Tasks created because of a Barrier must remain traceable back to that Barrier when such linkage exists

---

## Notes for v1

Starting Barriers at the Case level keeps the model simpler and better aligned with the current workflow understanding.

If later workflows show that barriers need to be tracked at Measure or Medication level, the model can be extended without changing Barrier's core purpose.
