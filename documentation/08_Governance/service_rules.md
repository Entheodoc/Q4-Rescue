# Service Rules

## Metadata

Document ID: GOV-SERVICE-RULES-001
Status: Active
Version: 1.1.0
Last Updated: 2026-03-15
Owner: José Palomino
Layer: Governance
Parent Document: PRD-MASTER-001

---

## Purpose

This document defines how application services must be designed in the Q4-Rescue backend.

Its purpose is to keep new backend work consistent, auditable, observable, secure, and maintainable as the system grows.

These rules are especially important because the platform handles healthcare-adjacent operational data and may later handle PHI.

---

## Scope

These rules apply to all service-layer code under:

- `app/application/services/`

They also define expectations for how the following layers interact with services:

- `app/api/`
- `app/observability/`
- `app/persistence/repositories/`

---

## Service Layer Responsibilities

The service layer is the application workflow layer.

Services are responsible for:

- coordinating repository calls
- enforcing workflow order
- applying permission-sensitive business flow
- deciding which response shape should be returned
- writing audit events for sensitive reads and writes
- emitting logs, metrics, and traces using approved observability patterns
- preserving minimum-necessary access patterns

Services are not responsible for:

- request parsing
- HTTP wiring details beyond raising application-relevant errors
- low-level persistence mechanics
- direct SQL construction
- vendor-specific observability setup

---

## Required Service Rules

Every service method must follow these rules:

1. Accept `actor` and `request_id`.
2. Authorize before reading or mutating sensitive data when feasible.
3. Load only the data needed for the current action.
4. Keep workflow logic in the service, not in the route.
5. Use repositories for persistence and retrieval only.
6. Return the minimum necessary response shape.
7. Write an audit event for sensitive reads and writes.
8. Avoid logging raw sensitive payloads.
9. Emit observability signals with stable, low-cardinality naming.
10. Keep audit records, domain events, and runtime telemetry as separate concerns.

---

## Route Rules

Routes must remain thin.

Routes should only:

- parse input
- resolve dependencies
- enforce route-level permission gates
- call one service method
- return the service result

Routes must not:

- implement multi-step workflow logic
- coordinate several repositories directly for business flow
- construct raw persistence responses for callers

---

## Repository Rules

Repositories must remain focused on persistence.

Repositories should:

- store data
- fetch data
- expose clear read and write methods
- serialize intentional response shapes when required by the application

Repositories should not:

- make business-policy decisions
- decide whether an operation is allowed
- own HTTP concerns

---

## Authorization Rules

Authorization must be explicit.

The default pattern is:

1. route-level permission gate through `require_permissions(...)`
2. service-level protection for especially sensitive behavior

Sensitive actions include:

- reading full case detail
- creating or updating case data
- archiving records
- exporting or bulk-reading sensitive data

If a new service action is sensitive, it must not rely on implicit trust from the caller.

---

## Audit Rules

Audit logging is mandatory for sensitive service actions.

At minimum, audit records should include:

- action
- resource type
- resource id when available
- actor subject
- actor permissions
- request id
- minimal metadata about the event

Audit metadata should prefer:

- ids
- counts
- status transitions
- boolean flags

Audit metadata should avoid:

- full names
- addresses
- phone numbers
- free-text notes
- full request payloads

unless there is a documented operational reason to include them.

Audit records are not a substitute for logs, metrics, or traces.

---

## Observability Rules

Runtime telemetry must support debugging and operations without becoming a shadow database of sensitive information.

Required patterns:

- logs are structured and correlated with `request_id`
- traces use request, service, and repository boundaries that mirror the real workflow
- metrics use low-cardinality labels only
- logs, traces, and metrics must avoid full payload capture

Do not put the following into metric labels:

- `case_id`
- `member_id`
- `request_id`
- actor-specific raw identifiers beyond stable low-cardinality categories

Prefer high-cardinality identifiers in logs and traces only, and only when operationally necessary.

When a service emits telemetry, it should prefer:

- action names
- route or operation names
- status values
- result counts
- boolean flags

Observability setup must remain vendor-neutral in code. App code should instrument OpenTelemetry and Prometheus-compatible concepts, while exporters and collectors remain environment concerns.

Detailed telemetry conventions are governed by `08_Governance/observability.md`.

---

## Response Rules

Service responses must be intentionally shaped.

Default rules:

- list endpoints return summaries
- detail endpoints return full graphs only when a specific permission and workflow need exists
- responses should expose only fields needed by the caller

It must always be possible to explain why each exposed field is necessary for that operation.

---

## Logging Rules

Application logging must not become a shadow database of sensitive data.

Do not:

- print request bodies for debugging
- log raw repository rows
- log full case graphs
- send sensitive payloads to generic tracing or error tooling without explicit review

If debugging requires context, prefer:

- request id
- resource id
- actor subject
- action name
- status or count values

---

## Required Service Method Shape

New service methods should generally follow this shape:

```python
def perform_action(
    self,
    *,
    resource_id: UUID,
    payload: dict,
    actor: AuthContext,
    request_id: str,
) -> dict:
    record = self.repo.get_by_id(resource_id)
    if not record:
        raise HTTPException(status_code=404, detail="Not found")

    if not actor.has_permission("resource:write"):
        raise HTTPException(status_code=403, detail="Forbidden")

    # Apply workflow rules
    # Persist updates
    # Record audit event
    # Emit safe logs, metrics, and traces

    return {"id": str(resource_id), "status": "updated"}
```

The exact details may vary, but the control flow should remain recognizable.

---

## Contributor Checklist

Every new service or sensitive service change should be reviewed against this checklist:

- route stays thin
- service accepts `actor` and `request_id`
- route uses explicit permission requirements
- authorization is checked before sensitive access or mutation
- workflow logic lives in the service
- repositories are used only for persistence and retrieval
- response returns the minimum necessary fields
- sensitive read or write actions create an audit event
- raw sensitive payloads are not logged
- metrics use low-cardinality labels only
- traces and logs carry request correlation
- tests cover success, permission failure, and audit behavior

---

## Definition Of Done

A service change is not done unless:

- the service method follows the rules in this document
- tests verify authorized success
- tests verify unauthorized or forbidden behavior where applicable
- tests verify audit behavior for sensitive actions
- responses do not expose extra sensitive fields by convenience
- emitted telemetry follows the observability rules for cardinality and sensitive-data handling

---

## Dependencies

- `08_Governance/governance.md`
- `08_Governance/observability.md`
- `app/api/security.py`
- `app/application/services/case_service.py`
- `app/observability/metrics.py`
- `app/observability/tracing.py`
- `app/persistence/repositories/audit_repo.py`

---

## Version History

Version 1.1.0 - 2026-03-15 - Added observability requirements, clarified telemetry boundaries, and aligned service guidance to the implemented logging, metrics, and tracing foundation.
Version 1.0.1 - 2026-03-14 - Aligned dependency references with the governance path convention.
Version 1.0.0 - 2026-03-14 - Initial service-layer rulebook and contributor checklist.
