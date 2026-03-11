# Pharmacy

## Metadata

Document ID: DOM-PHARMACY-001
Status: Active
Version: 0.1.0
Last Updated: 2026-03-11
Owner: Jose Palomino
Layer: Domain
Parent Document: PRD-MASTER-001

---

## Purpose

The **Pharmacy** is a shared business actor.

It represents a reusable pharmacy entity across many Medications, Cases, and ContactAttempts.

Pharmacy exists as the contact identity for pharmacy outreach and as the shared party linked to pharmacy-specific medication handling.

---

## Entity Definition

**Entity:** Pharmacy

A Pharmacy is not case-owned.

It is a shared entity that may recur across many MedicationPharmacy relationships and many ContactAttempts.

---

## Relationships

- one Pharmacy may be linked to many Medications through MedicationPharmacy
- one Pharmacy may be the target of many ContactAttempts

---

## Core Attributes

### Identity

- `PharmacyID` (UUID)
- `Name`

### Contact

- `PhoneNumbers` (multi-valued)
- `PreferredPhoneNumber`
- `FaxNumber`

### Address

- `AddressLine1`
- `AddressLine2` (nullable)
- `City`
- `State`
- `Zip`

### Audit

- `CreatedAt`
- `UpdatedAt`

---

## Domain Responsibilities

Pharmacy is responsible for:

- holding pharmacy identity and contact information
- supporting pharmacy outreach
- supporting pharmacy-medication relationships

---

## What Should Not Belong to Pharmacy

The following should not belong to Pharmacy:

- case ownership
- measure ownership
- medication-specific fill or refill state directly on the pharmacy record

Medication-specific fill and refill state belongs on MedicationPharmacy instead.

---

## Invariants

The following invariants should hold:

- a Pharmacy is shared across cases rather than owned by one Case
- a Pharmacy may appear in many ContactAttempts
- a Pharmacy may be linked to many Medications over time

---

## Notes for v1

Whether pharmacy contact details should later move into a reusable contact-point value object remains an open design question.
