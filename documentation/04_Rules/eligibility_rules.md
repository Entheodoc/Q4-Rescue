# Eligibility Rules

## Metadata

Document ID: RULE-ELIGIBILITY-001
Status: Draft
Version: 0.1.0
Last Updated: 2026-03-14
Owner: José Palomino
Layer: Rules
Parent Document: PRD-MASTER-001

---

## Purpose

This document defines the current case-opening gate for intake and clarifies which eligibility decisions are already system-enforced versus still delegated to upstream workflow.

---

## Current System-Enforced Gate

The backend currently enforces these requirements before a new `Case` is accepted:

- the caller must be authorized to create cases
- the request must include `Member`, `Referral`, and at least one `Measure`
- the Member must not already have another active `Case`
- the requested `Case` must not contain duplicate active Measures for the same normalized `MeasureCode` and `PerformanceYear`

If any of these checks fail, the request is rejected.

---

## Upstream Eligibility Inputs

The intake workflow expects the following business inputs to exist, even though the backend does not yet compute them automatically:

- enrollment status
- active program participation
- plan alignment
- measure qualification from source data
- adherence or rescue risk indicators

These inputs are currently expected to be screened by the upstream source or by an authorized operator before a case is submitted.

---

## Current Operating Rule

Until automated intake is implemented, an authorized caller is responsible for performing upstream business eligibility review before invoking case creation.

The backend currently acts as the enforcement point for structural and duplicate-case validation, not as the full eligibility engine.

---

## Deferred Eligibility Logic

The following areas are intentionally deferred and should be added in later rule versions:

- measure-specific qualification logic from claims or payer files
- disenrollment and hospitalization gating logic
- plan-based routing and exclusion logic
- timing windows for when rescue work should or should not open

---

## Dependencies

- `03_Workflows/intake_workflow.md`
- `02_Domain/case.md`
- `app/api/schemas/case.py`
- `app/application/services/case_service.py`

---

## Version History

Version 0.1.0 - 2026-03-14 - Initial draft eligibility rules separating current enforced gates from deferred intake logic.
