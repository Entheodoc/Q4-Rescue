# Member

## Metadata

Document ID: DOM-MEMBER-001
Status: Active
Version: 0.1.0
Last Updated: 2026-03-11
Owner: Jose Palomino
Layer: Domain
Parent Document: PRD-MASTER-001

---

## Purpose

The **Member** is the persistent person record in the Q4-Rescue domain.

It represents the plan member across time, even when:

- multiple referrals arrive
- multiple cases are created in different periods
- demographic or contact information changes later

Member is not the rescue work itself. It is the stable identity that referrals, cases, and downstream operational records refer to.

---

## Entity Definition

**Entity:** Member

A Member is the canonical person record used to connect rescue activity across time for the same covered person.

The Member is responsible for:

- preserving one stable person identity
- holding the latest known member information
- linking multiple referrals to the same person over time
- linking multiple cases to the same person over time

The Member does not represent:

- a referral
- a case
- a measure problem
- a medication
- a task
- a contact attempt

---

## Relationships

- one Member can have many Referrals over time
- one Member can have many Cases over time
- one Member should have at most one active Case at a time in this workflow

Member is the person-centered anchor for the rescue domain.

---

## Core Attributes

### Identity

- `MemberID` (UUID) - Internal system identifier
- `HealthPlanMemberID` - Primary external/business identifier for the member

### Demographics

- `FirstName`
- `LastName`
- `BirthDate`
- `Sex` (nullable)

### Contact

- `PhoneNumber`
- `PreferredContactMethod` - Expected initial values: `call`, `text`, `unknown`

### Language

- `PreferredLanguage` - Primary language to use first for outreach
- `SupportedLanguages` - Additional languages that can be used for outreach

### Address

- `AddressLine1`
- `AddressLine2` (nullable)
- `City`
- `State`
- `Zip`

### Plan Context

- `PBP`
- `LowIncomeSubsidyLevel` (nullable)
- `ActiveStatus`

### Audit

- `CreatedAt`
- `UpdatedAt`

---

## Identity and Uniqueness

The current working business key for Member is:

- `HealthPlanMemberID`

This means the domain should treat repeated intake records with the same `HealthPlanMemberID` as the same Member unless later source-system analysis proves a more stable identifier is required.

The internal `MemberID` exists to provide a durable system identity even if external source formats change.

---

## Domain Responsibilities

Member is responsible for:

- representing the current known person record
- receiving updates when later referrals provide newer member data
- allowing historical referrals and cases to remain linked to the same person

Member is not responsible for preserving the exact intake-time snapshot of every incoming referral. That historical responsibility belongs to Referral.

---

## Snapshot Rule

Some data points appear both on Member and on Referral, but for different reasons.

- Member stores the current canonical view of the person
- Referral stores the intake-time snapshot that arrived with that specific referral

This rule is especially important for fields that may change over time, such as:

- phone number
- address
- language
- PBP
- active status

The system should be able to answer both of these questions:

- what is the latest known member information now
- what information was present when a specific referral was received

---

## Invariants

The following invariants should hold:

- every Member must have exactly one internal `MemberID`
- every Member must have one `HealthPlanMemberID`
- `PreferredLanguage` and `SupportedLanguages` must not conflict
- `PreferredLanguage` should also appear in `SupportedLanguages` when `SupportedLanguages` is populated
- Member contact and plan fields may change over time
- changing Member data must not rewrite historical Referral snapshots

---

## Notes for v1

The initial Member model is intentionally pragmatic.

It includes only fields that are expected to affect:

- person identification
- routing and outreach
- plan context
- longitudinal linkage across referrals and cases

Additional channels, demographic attributes, and consent details may be added later if operational workflows require them.
