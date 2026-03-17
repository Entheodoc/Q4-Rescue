# MedicationPharmacy

## Metadata

Document ID: DOM-MEDICATIONPHARMACY-001
Status: Active
Version: 0.1.2
Last Updated: 2026-03-15
Owner: José Palomino
Layer: Domain
Parent Document: PRD-MASTER-001

---

## Purpose

**MedicationPharmacy** is a real relationship object between Medication and Pharmacy.

It is not a dumb join table.

It exists because:

- one Medication may be refilled at more than one Pharmacy
- the relationship itself carries important operational data
- fill and refill state is pharmacy-specific

---

## Entity Definition

**Entity:** MedicationPharmacy

MedicationPharmacy represents how one Medication is being handled at one Pharmacy.

It allows the workflow to reason about pharmacy-specific fill, pickup, and refill state without incorrectly flattening those details onto Medication or Pharmacy.

---

## Relationships

- one Medication has many MedicationPharmacy records
- one Pharmacy has many MedicationPharmacy records
- each MedicationPharmacy belongs to exactly one Medication
- each MedicationPharmacy belongs to exactly one Pharmacy

---

## Core Attributes

### Identity

- `MedicationPharmacyID` (UUID)
- `MedicationID`
- `PharmacyID`

### Pharmacy-Specific Medication State

- `PharmacyStatus`
- `LastFillDate`
- `NextFillDate`
- `PickupDate`
- `LastFillDaysSupply`
- `Refills` - structured relationship-level refill data

### Audit

- `CreatedAt`
- `UpdatedAt`

---

## Domain Responsibilities

MedicationPharmacy is responsible for:

- holding pharmacy-specific fill and refill state for one Medication
- representing how that Medication is being handled at that Pharmacy
- supporting pharmacy-specific operational decisions

---

## What Should Not Belong to MedicationPharmacy

The following should not belong to MedicationPharmacy:

- pharmacy master contact information
- provider history
- measure-level performance such as PDC

Those belong to Pharmacy, MedicationProvider, and Measure instead.

---

## Invariants

The following invariants should hold:

- a Medication may have multiple pharmacy relationships
- fill and refill data belongs primarily here, not directly on Medication, when multiple Pharmacies are possible

---

## Refill Modeling

### Current Decision

`Refill` is not a standalone top-level domain entity at this time.

Instead:

- refill data is tied to a specific Medication and Pharmacy relationship
- refill data lives under MedicationPharmacy

### Why

Refill availability is always specific to:

- one Medication
- at one Pharmacy

Also, refill data carries relationship-level detail such as:

- days supply
- expiration date

### Recommended Shape

Treat `Refills` as structured relationship-level data inside MedicationPharmacy.

Each refill item should include at least:

- `DaysSupply`
- `ExpirationDate`

Optional future fields if needed:

- refill sequence or index
- refill status such as available, used, or expired
- source metadata

### Important Note

If implementation later needs refill rows in storage, that can be done as child or value-object-style data under MedicationPharmacy.

The current domain decision remains:

- Refill is not a first-class shared top-level entity
- Refill belongs to the MedicationPharmacy relationship

---

## Notes for v1

One open design question is whether MedicationPharmacy should store both:

- detailed refill entries
- convenience summary fields such as refill count

That detail does not need to be fully locked before the broader domain shape is accepted.

---

## Version History

Version 0.1.2 - 2026-03-15 - Normalized metadata formatting for the active documentation set.
Version 0.1.1 - 2026-03-14 - Added formal version history tracking to align the document with governance requirements.
Version 0.1.0 - 2026-03-11 - Initial MedicationPharmacy domain specification established.
