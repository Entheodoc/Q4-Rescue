# Measure

## Metadata

Document ID: DOM-MEASURE-001
Status: Active
Version: 0.1.0
Last Updated: 2026-03-11
Owner: Jose Palomino
Layer: Domain
Parent Document: PRD-MASTER-001

---

## Purpose

The **Measure** is a case-owned operational record of one specific adherence performance opportunity for a member.

It is not the abstract catalog definition of an industry measure.

In practical terms:

- "statin adherence" as a reusable concept is not this object
- "this member's statin adherence opportunity in this case" is this object

Measure is the bridge between the broad operational Case and the more specific Medication records.

---

## Entity Definition

**Entity:** Measure

A Measure exists to:

- separate one adherence opportunity from another inside the same Case
- group the Medications that qualify for that opportunity
- carry measure-specific performance and rescue status
- give Tasks a level above individual Medications when needed

---

## Relationships

- one Case has many Measures
- one Measure belongs to one Case
- one Measure has many Medications
- one Medication belongs to one Measure

---

## Core Attributes

### Identity

- `MeasureID` (UUID)
- `CaseID`

### Classification

- `MeasureCode`
- `MeasureName`
- `MeasurementYear` or `PerformanceYear`

### Performance

- `PDC`
- `TargetThreshold`

### Operational State

- `Status`
- `ActionableStatus`
- `IdentifiedAt`
- `OpenedAt`
- `ClosedAt` (nullable)
- `ClosureReason` (nullable)
- `RescueByDate` or `CriticalByDate` (nullable)

### Source Context

- `SourceSystem` (nullable)
- `SourceMeasureID` or source reference (nullable)

### Audit

- `CreatedAt`
- `UpdatedAt`

---

## Domain Responsibilities

Measure is responsible for:

- defining one specific rescue target within the Case
- grouping the Medications that participate in that rescue target
- holding measure-level performance context such as PDC
- holding measure-level operational status and timing

---

## What Should Not Belong to Measure

The following should not belong to Measure:

- direct ownership of ContactAttempt
- direct ownership of Provider or Pharmacy
- PDC on Medication instead of Measure
- default ownership of Barrier

Barriers remain Case-level by default unless later workflow evidence proves that narrower ownership is necessary.

---

## Invariants

The following invariants should hold:

- a Measure belongs to exactly one Case
- within one Case, avoid duplicate active Measures for the same `MeasureCode` and year
- a Measure may exist before all Medication detail is fully known
- a Measure may have more than one qualifying Medication

---

## Notes for v1

PDC belongs on Measure, not on Medication.

That is one of the most important boundaries in this model, because PDC is fundamentally measure performance rather than medication identity.
