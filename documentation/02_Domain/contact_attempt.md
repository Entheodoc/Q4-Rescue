# ContactAttempt

## Metadata

Document ID: DOM-CONTACTATTEMPT-001
Status: Active
Version: 0.1.0
Last Updated: 2026-03-11
Owner: Jose Palomino
Layer: Domain
Parent Document: PRD-MASTER-001

---

## Purpose

A **ContactAttempt** is one communication event directed at one contacted party.

It records that an outreach action actually happened, such as:

- a call to a Member
- a call to a Provider
- a call to a Pharmacy
- a text to a Member
- a fax to a Provider or Pharmacy

ContactAttempt is communication-scoped, not case-scoped.

---

## Entity Definition

**Entity:** ContactAttempt

A ContactAttempt represents one real-world outreach event and its result.

The same ContactAttempt may advance work for multiple Tasks, including Tasks from different Cases, when the contacted party is shared across that work.

This is especially important for Providers and Pharmacies, where one call or fax may address several medications for several members.

---

## Relationships

- one ContactAttempt targets exactly one contact party at a time
- the contact party may be one Member, one Provider, or one Pharmacy
- one ContactAttempt can link to many Tasks through TaskContactAttempt

ContactAttempt does not belong directly to Case because:

- one event may affect several Tasks
- those Tasks may belong to different Cases

---

## Core Attributes

### Identity

- `ContactAttemptID` (UUID)

### Target

- `ContactPartyType` - Initial working values: `member`, `provider`, `pharmacy`
- `ContactPartyID`

### Communication

- `ContactMethod` - Initial working values: `call`, `text`, `fax`
- `AttemptedAt`
- `Outcome`
- `OutcomeNotes` (nullable)

### Execution

- `InitiatedBy` (nullable)

### Audit

- `CreatedAt`
- `UpdatedAt`

---

## Domain Responsibilities

ContactAttempt is responsible for:

- recording that outreach happened
- recording who was contacted
- recording how they were contacted
- capturing the outcome of that event
- serving as the shared communication event linked back to Tasks

ContactAttempt is not responsible for:

- replacing the Task that motivated the outreach
- owning Case lifecycle state
- acting as the member, provider, or pharmacy record itself

---

## Invariants

The following invariants should hold:

- every ContactAttempt must have exactly one target party
- every ContactAttempt must use exactly one contact method
- a ContactAttempt may link to zero, one, or many Tasks
- linked Tasks may span multiple Cases when the communication event legitimately advanced each of them
- one ContactAttempt must not be duplicated simply because it affected multiple Tasks

---

## Notes for v1

The key design decision is that ContactAttempt models the actual communication event.

That keeps the domain aligned with reality:

- one call is one call
- one fax is one fax
- one message is one message

Task linkage is what connects that event back to the operational work it advanced.
