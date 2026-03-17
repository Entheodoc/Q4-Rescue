# Adherence Rules

## Metadata

Document ID: RULE-ADHERENCE-001
Status: Draft
Version: 0.1.0
Last Updated: 2026-03-14
Owner: José Palomino
Layer: Rules
Parent Document: PRD-MASTER-001

---

## Purpose

This document defines the current adherence interpretation baseline used by the domain model and intake workflow.

It does not yet define payer-specific calculation formulas or outreach prioritization math.

---

## Current Baseline Rules

- `PDC` belongs to `Measure`, not to `Medication`
- `TargetThreshold` belongs to `Measure`, not to `Medication`
- a `Measure` represents one adherence opportunity within one `Case`
- a `Medication` belongs to exactly one `Measure`
- duplicate active Measures for the same normalized `MeasureCode` and `PerformanceYear` are not allowed within one `Case`

These are the core adherence-shape rules currently reflected in the backend model.

---

## Current Data Expectations

- `pdc`, when provided, must be between `0.0` and `1.0`
- `target_threshold`, when provided, must be between `0.0` and `1.0`
- `critical_by_date` may be supplied from upstream risk logic
- adherence calculations are currently stored from upstream input rather than computed inside the backend

---

## Deferred Adherence Logic

The following areas are intentionally deferred:

- claims-window and refill-gap calculation rules
- measure-specific qualification formulas
- grace periods and rescue timing windows
- standardized prioritization thresholds by plan or measure

---

## Dependencies

- `02_Domain/measure.md`
- `02_Domain/medication.md`
- `03_Workflows/intake_workflow.md`
- `app/api/schemas/case.py`

---

## Version History

Version 0.1.0 - 2026-03-14 - Initial draft adherence rules documenting the current modeling baseline and deferred calculation logic.
