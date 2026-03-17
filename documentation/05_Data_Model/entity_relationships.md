# Entity Relationships

## Metadata

Document ID: DATA-ENTITY-RELATIONSHIPS-001
Status: Active
Version: 0.1.0
Last Updated: 2026-03-14
Owner: José Palomino
Layer: Data Model
Parent Document: PRD-MASTER-001

---

## Purpose

This document defines the current structural relationships in the active Q4-Rescue persistence model.

It is the governed relational view of the domain shape implemented in the database schema and repositories.

---

## Core Relationship Map

| From | To | Cardinality | Current Constraint |
|------|----|-------------|--------------------|
| Member | Referral | 1 to many | `referrals.member_id` |
| Member | Case | 1 to many over time | `cases.member_id` plus one-active-case partial unique index |
| Referral | Case | 1 to 1 | `cases.referral_id` unique and `referrals.case_id` unique |
| Case | Measure | 1 to many | `measures.case_id` |
| Case | Barrier | 1 to many | `barriers.case_id` |
| Case | Task | 1 to many | `tasks.case_id` |
| Measure | Medication | 1 to many | `medications.measure_id` |
| Medication | MedicationProvider | 1 to many | `medication_providers.medication_id` |
| Provider | MedicationProvider | 1 to many | `medication_providers.provider_id` |
| Medication | MedicationPharmacy | 1 to many | `medication_pharmacies.medication_id` |
| Pharmacy | MedicationPharmacy | 1 to many | `medication_pharmacies.pharmacy_id` |
| MedicationPharmacy | MedicationPharmacyRefill | 1 to many | `medication_pharmacy_refills.medication_pharmacy_id` |
| Task | TaskContactAttempt | 1 to many | `task_contact_attempts.task_id` |
| ContactAttempt | TaskContactAttempt | 1 to many | `task_contact_attempts.contact_attempt_id` |

---

## Key Structural Constraints

- one Member may have many Cases over time, but only one active Case at a time
- one Referral creates exactly one Case in the current model
- duplicate active Measures for the same normalized `MeasureCode` and `PerformanceYear` are blocked within one Case
- one Medication may have at most one current prescriber flag
- one Medication may have at most one refill-contact provider flag
- one Task and one ContactAttempt may only be linked once as a pair

---

## Indirect Associations

- `ContactAttempt` does not belong directly to `Case`
- `Case` relates to `ContactAttempt` through `Task -> TaskContactAttempt -> ContactAttempt`
- `Provider` and `Pharmacy` are shared actors and are not owned by a single Case

These indirect relationships are intentional and should not be flattened without explicit domain review.

---

## Current Implementation Source

The active persistence implementation for this model lives in:

- `app/persistence/schema.sql`
- `alembic/versions/20260314_0001_initial_schema.py`
- `app/persistence/repositories/case_repo.py`

---

## Dependencies

- `02_Domain/case.md`
- `02_Domain/referral.md`
- `02_Domain/measure.md`
- `02_Domain/medication.md`
- `app/persistence/schema.sql`

---

## Version History

Version 0.1.0 - 2026-03-14 - Initial governed entity relationship document aligned to the active schema and repository model.
