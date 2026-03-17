# MedicationProvider

## Metadata

Document ID: DOM-MEDICATIONPROVIDER-001
Status: Active
Version: 0.1.2
Last Updated: 2026-03-15
Owner: José Palomino
Layer: Domain
Parent Document: PRD-MASTER-001

---

## Purpose

**MedicationProvider** is a real relationship object between Medication and Provider.

It is not a dumb join table.

It exists because:

- one Medication may involve multiple Providers over time
- the relationship itself carries important business data
- the workflow needs both current and historical prescribing context

---

## Entity Definition

**Entity:** MedicationProvider

MedicationProvider represents the provider relationship for one Medication in an operationally meaningful way.

It allows the system to distinguish between:

- who currently prescribes the medication
- who prescribed it in the past
- who should be contacted for refill-related work

---

## Relationships

- one Medication has many MedicationProvider records
- one Provider has many MedicationProvider records
- each MedicationProvider belongs to exactly one Medication
- each MedicationProvider belongs to exactly one Provider

---

## Core Attributes

### Identity

- `MedicationProviderID` (UUID)
- `MedicationID`
- `ProviderID`

### Relationship Context

- `PrescribingRole`
- `IsCurrentPrescriber`
- `LastPrescribedAt` and/or effective date fields
- `RefillRequestStatus`
- `ProviderNotes`
- `ContactForRefills`

### Audit

- `CreatedAt`
- `UpdatedAt`

---

## Domain Responsibilities

MedicationProvider is responsible for:

- capturing current and historical provider relationships for a Medication
- identifying which Provider is the current or last prescriber
- identifying which Provider should be contacted for refill-related work
- holding provider-specific notes and status relevant to that Medication

---

## What Should Not Belong to MedicationProvider

The following should not belong to MedicationProvider:

- provider master contact information
- medication master identity
- member-level PCP assignment
- pharmacy fill or refill state

Those belong to Provider, Medication, and MedicationPharmacy instead.

---

## Invariants

The following invariants should hold:

- a Medication may have many historical provider relationships
- a Medication should have at most one current or last prescriber at a time
- if `ContactForRefills` is modeled as a single designated contact, a Medication should have at most one refill-contact Provider at a time

---

## Notes for v1

The exact balance between chronology and explicit flags remains partially open.

The current model intentionally allows both:

- explicit flags such as `IsCurrentPrescriber`
- timing fields such as `LastPrescribedAt`

That keeps the model practical even when source-system history is incomplete.

If PCP becomes operationally important later, it should be modeled separately as a member-to-provider relationship rather than overloaded into MedicationProvider.

---

## Version History

Version 0.1.2 - 2026-03-15 - Normalized metadata formatting for the active documentation set.
Version 0.1.1 - 2026-03-14 - Added formal version history tracking to align the document with governance requirements.
Version 0.1.0 - 2026-03-11 - Initial MedicationProvider domain specification established.
