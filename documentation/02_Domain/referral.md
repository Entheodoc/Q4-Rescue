# Referral

## Metadata

Document ID: DOM-REFERRAL-001
Status: Active
Version: 0.1.2
Last Updated: 2026-03-15
Owner: José Palomino
Layer: Domain
Parent Document: PRD-MASTER-001

---

## Purpose

The **Referral** is the intake record that starts rescue work for a member.

It captures:

- one incoming referral event
- the source information received at intake time
- the historical snapshot associated with that intake event

Each Referral creates exactly one Case in the current domain design.

---

## Entity Definition

**Entity:** Referral

A Referral is the business record of one specific intake event. It is not just a transport payload and it is not the same thing as the Case created from it.

Referral is responsible for:

- recording that a referral was received
- preserving the intake-time member and plan snapshot
- linking the intake event to the resulting Case
- maintaining source traceability back to the incoming referral feed or source record

---

## Relationships

- one Referral belongs to one Member
- one Referral creates exactly one Case
- one Case is linked to exactly one Referral

This makes Referral and Case a one-to-one relationship in the current model, while still preserving their separate responsibilities.

The separation matters because:

- Referral is the intake event and historical snapshot
- Case is the operational rescue record

If the same Member is referred again later, that should create:

- a new Referral
- a new Case

---

## Core Attributes

### Identity

- `ReferralID` (UUID) - Internal system identifier
- `MemberID` - Reference to Member
- `CaseID` - Reference to the Case created from this referral

### Intake Context

- `ReceivedAt`
- `ReferralSource` - Example values: payer file, internal queue, manual entry
- `SourceRecordID` (nullable) - External identifier for traceability
- `ReferralReason` (nullable)
- `ReferralNotes` (nullable)

### Snapshot: Member Information at Intake

- `SnapshotHealthPlanMemberID`
- `SnapshotFirstName`
- `SnapshotLastName`
- `SnapshotBirthDate`
- `SnapshotPhoneNumber`
- `SnapshotPreferredLanguage`
- `SnapshotSupportedLanguages`
- `SnapshotAddressLine1`
- `SnapshotAddressLine2` (nullable)
- `SnapshotCity`
- `SnapshotState`
- `SnapshotZip`

### Snapshot: Plan Context at Intake

- `SnapshotPBP`
- `SnapshotLowIncomeSubsidyLevel` (nullable)
- `SnapshotActiveStatus`

### Audit

- `CreatedAt`
- `UpdatedAt`

---

## Domain Responsibilities

Referral exists so the system can preserve what was true when intake happened, even if later canonical Member data changes.

Referral is responsible for:

- preserving intake-time facts
- keeping source provenance
- initiating the Case lifecycle

Referral is not responsible for:

- owning the full operational workflow after case creation
- storing all task or contact history
- acting as the aggregate root for case work

---

## Snapshot Rule

Referral must preserve the intake-time view of data, even when the Member record is later updated.

Examples:

- a Member phone number may change after intake
- address information may be corrected later
- language preferences may be updated
- plan context such as `PBP` or `ActiveStatus` may change

Those later changes belong on Member.

The original intake values must remain preserved on Referral.

---

## Invariants

The following invariants should hold:

- every Referral must belong to exactly one Member
- every Referral must create exactly one Case
- every Case must have exactly one Referral
- a Referral cannot be reassigned to a different Member after case creation
- a Referral must retain source traceability
- a Referral snapshot is historical and should not be overwritten with newer canonical Member data

---

## Notes for v1

The Referral model intentionally stays focused on intake identity, provenance, and historical preservation.

Measure-level and medication-level operational details should be normalized into Case, Measure, and Medication during intake processing rather than overloading Referral itself.

---

## Version History

Version 0.1.2 - 2026-03-15 - Normalized metadata formatting for the active documentation set.
Version 0.1.1 - 2026-03-14 - Added formal version history tracking to align the document with governance requirements.
Version 0.1.0 - 2026-03-11 - Initial Referral domain specification established.
