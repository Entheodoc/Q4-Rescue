# Observability

## Metadata

Document ID: GOV-OBSERVABILITY-001
Status: Active
Version: 1.0.0
Last Updated: 2026-03-15
Owner: José Palomino
Layer: Governance
Parent Document: PRD-MASTER-001

---

## Purpose

This document defines the observability conventions for the Q4-Rescue backend.

Its purpose is to make logs, metrics, and traces useful for operations and debugging while preserving vendor neutrality, low-cardinality metrics, and minimum-necessary handling of sensitive data.

---

## Scope

These rules apply to:

- `app/observability/`
- `app/main.py`
- `app/api/`
- `app/application/services/`
- `app/persistence/connection.py`

They govern runtime telemetry only. They do not redefine:

- audit logging
- domain event contracts
- dashboard semantics

---

## Current Runtime Foundation

The backend currently implements:

- structured JSON application logs
- request correlation through `X-Request-ID`
- trace correlation through response headers and log context
- Prometheus metrics exposed at `/metrics` when enabled
- OpenTelemetry spans across HTTP middleware, services, and DB queries

Current implementation entry points:

- `app/observability/context.py`
- `app/observability/http.py`
- `app/observability/logging.py`
- `app/observability/metrics.py`
- `app/observability/tracing.py`

---

## Core Principles

1. Telemetry must be useful without exposing full sensitive records.
2. Logs, metrics, traces, audit records, and domain events are separate artifacts.
3. Code instrumentation must remain vendor-neutral.
4. Metric dimensions must stay low-cardinality.
5. Correlation must be consistent across request, service, and persistence boundaries.

---

## Logging Rules

Application logs must be structured JSON and should prefer stable operational fields such as:

- `request_id`
- `trace_id`
- `span_id`
- `actor_subject` when available
- operation name
- route
- status code
- duration

Logs must not include:

- full request bodies
- full case graphs
- phone numbers
- addresses
- free-text notes
- auth tokens

When additional context is needed, prefer ids, counts, booleans, and controlled status values.

---

## Metrics Rules

Metrics must support dashboards and alerts without exploding cardinality.

Approved metric styles:

- counters for event totals
- histograms for duration
- gauges only when the value is genuinely point-in-time state

Metric labels must be low-cardinality. Approved label categories include:

- HTTP method
- route template
- status code
- operation name
- outcome category
- destination lifecycle status

Metric labels must never include:

- `case_id`
- `member_id`
- `request_id`
- raw bearer tokens
- names, phone numbers, or addresses

High-cardinality identifiers belong in logs or traces only, and only when operationally justified.

---

## Tracing Rules

Tracing should reflect the real execution path:

- HTTP request span
- service method span
- DB query span

Spans should include:

- request correlation
- stable operation names
- low-sensitivity ids when operationally necessary
- success or failure outcome

Spans should avoid:

- full payload dumps
- raw repository rows
- large nested JSON documents

Tracing configuration must use OpenTelemetry in application code. Export is an environment concern and may point to any OTLP-compatible collector or backend.

---

## Correlation Rules

Every request should be traceable through:

- `request_id`
- `trace_id`
- service and repository span names

The application should preserve request correlation through middleware and dependency resolution so logs and traces can be joined during investigations.

When a request is user-initiated, actor identity should be represented by a safe subject identifier rather than a raw token.

---

## Data Minimization Rules

Observability data must follow the same minimum-necessary mindset as the rest of the backend.

Prefer:

- ids
- counts
- booleans
- lifecycle statuses
- operation names

Avoid:

- unredacted payload snapshots
- clinical or contact details unless explicitly required for incident response
- duplicating sensitive data across logs, metrics, and traces

If a telemetry field is not clearly needed to operate or debug the system, it should not be emitted.

---

## Vendor Neutrality Rules

The codebase should instrument open concepts and leave backend choice outside the application whenever possible.

Required defaults:

- OpenTelemetry for tracing instrumentation
- OTLP for trace export
- Prometheus-compatible metric exposition
- stdout JSON logs

A Collector or backend-specific exporter may be introduced by environment configuration, but the domain and service code should not be rewritten around vendor-specific APIs unless governance is updated first.

---

## Current Baseline Metrics

The current implementation exposes metrics for:

- HTTP request count and latency
- service operation latency
- DB operation count and latency
- cases created
- case status transitions
- create conflicts
- idempotency replays

These metrics define the baseline naming pattern for future instrumentation.

---

## Dependencies

- `00_master_index.md`
- `08_Governance/service_rules.md`
- `app/main.py`
- `app/observability/http.py`
- `app/observability/logging.py`
- `app/observability/metrics.py`
- `app/observability/tracing.py`

---

## Version History

Version 1.0.0 - 2026-03-15 - Initial observability governance document covering structured logs, metrics, traces, correlation, and vendor-neutral instrumentation rules.
