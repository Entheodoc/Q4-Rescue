# Escalation Rules

## Metadata

Document ID: RULE-ESCALATION-001
Status: Draft
Version: 0.1.0
Last Updated: 2026-03-14
Owner: José Palomino
Layer: Rules
Parent Document: PRD-MASTER-001

---

## Purpose

This document defines the current escalation categories recognized by the intake and rescue workflow design.

It also clarifies that dedicated escalation automation is not yet implemented in the backend.

---

## Current Escalation Categories

The current documentation model treats these conditions as escalation triggers:

- member hospitalized
- member deceased
- member disenrolled
- critical demographic or plan discrepancy
- incorrect measure assignment

These categories represent conditions that should interrupt routine rescue processing.

---

## Current Operating Rule

The backend does not yet contain a dedicated escalation engine, queue, or event dispatcher.

Until that exists, upstream intake flows or authorized operators must treat escalation categories as manual-review conditions and decide whether rescue work should be blocked, held, or rerouted.

---

## Recommended Handling Baseline

- deceased or disenrolled: do not open a new case without explicit policy override
- critical discrepancy: route for manual review before create or continue
- incorrect measure assignment: stop normal intake flow and correct source context first
- hospitalized: review operational policy before standard outreach continues

These recommendations are provisional until a governed operational ruleset is authored.

---

## Deferred Escalation Logic

The following areas remain to be formalized:

- escalation ownership and queue routing
- SLA or timing targets
- event emission for escalations
- automatic case hold or closure behavior

---

## Dependencies

- `03_Workflows/intake_workflow.md`
- `06_Automation/domain_events.md`

---

## Version History

Version 0.1.0 - 2026-03-14 - Initial draft escalation rules documenting current categories and manual-review expectations.
