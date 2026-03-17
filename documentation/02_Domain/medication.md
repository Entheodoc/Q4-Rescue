# Medication

## Metadata

Document ID: DOM-MEDICATION-001
Status: Active
Version: 0.1.2
Last Updated: 2026-03-15
Owner: José Palomino
Layer: Domain
Parent Document: PRD-MASTER-001

---

## Purpose

The **Medication** is a measure-scoped operational medication record.

It is not meant to be a global medication master shared across multiple Measures.

Medication exists so the rescue workflow can reason at the drug level under a specific Measure without overloading either Measure or the shared Provider and Pharmacy records.

---

## Entity Definition

**Entity:** Medication

A Medication exists to:

- represent one medication participating in one Measure
- give the rescue workflow a medication-level object under the Measure
- anchor the relationship to Providers and Pharmacies

Medication should stay fairly lean because provider history and pharmacy fill/refill state live on relationship objects rather than directly on Medication.

---

## Relationships

- one Medication belongs to one Measure
- one Measure has many Medications
- one Medication may link to many Providers through MedicationProvider
- one Medication may link to many Pharmacies through MedicationPharmacy

---

## Core Attributes

### Identity

- `MedicationID` (UUID)
- `MeasureID`

### Display

- `MedicationName`
- `DisplayName` (nullable)

### Audit

- `CreatedAt`
- `UpdatedAt`

### Future Optional Attributes

These are not yet locked, but may be added later if the workflow needs them:

- external medication identifier(s)
- generic and brand naming details
- strength
- dosage form
- medication status

---

## Domain Responsibilities

Medication is responsible for:

- representing one measure-specific drug line
- sitting under a Measure
- anchoring pharmacy-specific and provider-specific relationship objects
- supporting medication-level operational reasoning when a Task applies to a specific Medication

---

## What Should Not Belong to Medication

The following should not belong to Medication:

- `PDC`
- a single `ProviderID`
- a single `PharmacyID`
- provider history as flat fields
- pharmacy-specific fill/refill/pickup data as the primary source of truth

Those details belong to Measure, MedicationProvider, and MedicationPharmacy instead.

---

## Invariants

The following invariants should hold:

- a Medication belongs to exactly one Measure
- a Medication always belongs to a Measure
- a Medication never qualifies for more than one Measure at a time
- a Measure may have more than one qualifying Medication
- a Medication may have many provider relationships
- a Medication may have many pharmacy relationships

---

## Notes for v1

Do not put a single `ProviderID` or `PharmacyID` directly on Medication.

That would incorrectly flatten a many-to-many, data-rich relationship that the workflow clearly cares about.

---

## Version History

Version 0.1.2 - 2026-03-15 - Normalized metadata formatting for the active documentation set.
Version 0.1.1 - 2026-03-14 - Added formal version history tracking to align the document with governance requirements.
Version 0.1.0 - 2026-03-11 - Initial Medication domain specification established.
