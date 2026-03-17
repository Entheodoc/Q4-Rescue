# State Transition Rules

## Metadata

Document ID: RULE-STATE-TRANSITION-001
Status: Active
Version: 1.0.0
Last Updated: 2026-03-14
Owner: José Palomino
Layer: Rules
Parent Document: PRD-MASTER-001

---

## Purpose

This document defines the current authoritative lifecycle transition rules for `Case`.

These rules are implemented in the backend today and should be treated as the governing source for case lifecycle behavior until additional entity-specific rule documents are authored.

---

## Scope

Current governed scope covers `Case` lifecycle transitions only.

Measure, Barrier, Task, and ContactAttempt state models may be documented later, but they are not defined here yet.

---

## Allowed Transitions

- `open -> in_progress`
- `open -> on_hold`
- `on_hold -> in_progress`
- `on_hold -> open`
- `in_progress -> on_hold`
- `in_progress -> closed`
- `closed -> archived`

Any transition not listed above is invalid.

---

## Disallowed Transitions

- `open -> closed`
- `open -> archived`
- `on_hold -> archived`
- `closed -> open`
- `closed -> in_progress`
- `archived -> any state`

Archived cases are terminal.

---

## Operational Rules

- A newly created `Case` starts in `open`.
- Moving to `closed` may record `ClosedAt` and `ClosedReason`.
- Moving to `archived` records `ArchivedAt`.
- A Member may have at most one active `Case` at a time, where active means `open`, `in_progress`, or `on_hold`.

---

## Current Implementation Source

The current implementation source for these rules is:

- `app/domain/case.py`
- `app/application/services/case_service.py`

If implementation changes, this document must be updated in the same change.

---

## Dependencies

- `02_Domain/case.md`
- `app/domain/case.py`
- `app/application/services/case_service.py`

---

## Version History

Version 1.0.0 - 2026-03-14 - Initial governed Case lifecycle transition rules established from the active backend implementation.
