# Domain Events

## Metadata

Document ID: AUTO-DOMAIN-EVENTS-001
Status: Draft
Version: 0.1.1
Last Updated: 2026-03-15
Owner: José Palomino
Layer: Automation
Parent Document: PRD-MASTER-001

---

## Purpose

This document defines the planned domain event contract for Q4-Rescue.

It separates future integration events from the audit log records that already exist in the backend.

---

## Current State

The backend currently records audit events for sensitive reads and writes and emits runtime telemetry through logs, metrics, and traces, but it does not yet emit a governed domain event stream for downstream automation.

This document therefore defines the intended event contract, not a fully implemented feature.

---

## Event Contract Baseline

Every future domain event should include:

- event name
- occurred-at timestamp
- resource type
- resource id
- request id or correlation id
- actor subject when user-initiated
- a minimal payload that supports downstream automation without copying full sensitive records

Domain events should carry the smallest payload needed for coordination.

---

## Planned Initial Events

The initial event set should include:

- `case.created`
- `case.status.updated`
- `case.archived`
- `intake.eligibility.rejected`
- `rescue.initial_risk_detected`
- `rescue.escalation.detected`

These names may be refined, but they represent the current expected automation boundary.

---

## Audit Events Versus Domain Events

Audit events and domain events serve different purposes:

- audit events are operational evidence and compliance-oriented trace records
- domain events are coordination signals for workflows, projections, or integrations
- logs, metrics, and traces are runtime telemetry for debugging and operations

One action may create both, but they should not be treated as the same system artifact.

---

## Deferred Design Areas

The following event concerns are still open:

- delivery mechanism
- retry behavior
- subscriber ownership
- ordering guarantees
- dead-letter or failure handling

---

## Dependencies

- `03_Workflows/intake_workflow.md`
- `04_Rules/state_transition_rules.md`
- `app/application/services/case_service.py`

---

## Version History

Version 0.1.1 - 2026-03-15 - Clarified that runtime telemetry is distinct from both audit records and future domain events.
Version 0.1.0 - 2026-03-14 - Initial draft domain event contract separating future automation events from current audit logging.
