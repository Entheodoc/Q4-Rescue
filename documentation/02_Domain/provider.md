# Provider

## Metadata

Document ID: DOM-PROVIDER-001
Status: Active
Version: 0.1.0
Last Updated: 2026-03-11
Owner: Jose Palomino
Layer: Domain
Parent Document: PRD-MASTER-001

---

## Purpose

The **Provider** is a shared business actor.

It represents the single provider actor used across the active rescue domain model.

Provider exists as a reusable contact identity for provider outreach and provider-medication relationships.

---

## Entity Definition

**Entity:** Provider

A Provider is not case-owned.

It is a shared entity that may appear repeatedly across the rescue domain as different members, cases, and medications intersect with the same provider organization.

---

## Relationships

- one Provider may be linked to many Medications through MedicationProvider
- one Provider may be the target of many ContactAttempts

---

## Core Attributes

### Identity

- `ProviderID` (UUID)
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

Provider is responsible for:

- holding provider identity and contact information
- supporting provider outreach
- supporting provider-medication relationships

---

## What Should Not Belong to Provider

The following should not belong to Provider:

- case ownership
- measure ownership
- medication-specific prescribing history
- pharmacy-specific fill data

Medication-specific provider context belongs on MedicationProvider instead.

There is no separate active `Prescriber` entity in the model. A prescriber is a Provider acting in a medication relationship.

---

## Invariants

The following invariants should hold:

- a Provider is shared across cases rather than owned by one Case
- a Provider may appear in many ContactAttempts
- a Provider may be linked to many Medications over time

---

## Notes for v1

Whether provider contact details should later move into a reusable contact-point value object remains an open design question.

PCP is not modeled as its own entity.

If the domain later needs to represent a member's PCP even when that PCP does not prescribe a medication in the case, that should be modeled through a future member-to-provider relationship object such as `MemberProvider`, not through a separate PCP entity and not through `MedicationProvider`.
