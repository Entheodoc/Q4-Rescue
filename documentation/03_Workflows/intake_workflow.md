# MeasureCase Intake Workflow

## Metadata

Document ID: WF-INTAKE-001
Status: Active
Version: 1.0.0
Last Updated: 2026-03-01
Owner: José Palomino
Layer: Workflow
Parent Document: PRD-MASTER-001

---

# Purpose

The Intake Workflow evaluates Member eligibility for CMS Star adherence measures and initializes MeasureCases for eligible Measure episodes.

This workflow orchestrates domain interactions but does not define business rules, lifecycle rules, or state transition logic.

Eligibility logic is defined in `04_Rules/Eligibility_Rules.md`.

MeasureCase lifecycle behavior is defined in `02_Domain/MeasureCase.md`.

---

# Inputs

- Referral list
- Claims data
- Enrollment status
- Measure eligibility data
- Plan information (PBP / HPID if applicable)

---

# Core Objectives

1. Validate Member enrollment and program participation.
2. Evaluate eligibility for each supported Measure.
3. Detect initial adherence risk signals.
4. Create MeasureCases for eligible Measure episodes.
5. Emit appropriate domain events.

---

# Orchestration Steps

## 1. Referral Validation

- Confirm Member is active in the program.
- Verify enrollment status.
- Confirm correct plan assignment.
- Validate referral data completeness.

If Member is not active:
- No MeasureCase is created.
- Workflow terminates.

---

## 2. Data Verification

- Validate demographic information.
- Confirm PCP information.
- Confirm pharmacy information.
- Identify critical data discrepancies.

If discrepancies are detected:
- Emit appropriate escalation events as defined in `Escalation_Rules.md`.

---

## 3. Measure Eligibility Evaluation

For each supported adherence Measure (e.g., DM, RASA, Statin):

- Apply eligibility rules defined in `Eligibility_Rules.md`.
- Determine whether the Member qualifies for that Measure.

If eligible:
- Proceed to MeasureCase creation.

If not eligible:
- No MeasureCase is created for that Measure.

---

## 4. MeasureCase Creation

For each eligible Measure:

- Instantiate a new MeasureCase.
- Assign a unique CaseID.
- Associate MemberID and MeasureID.
- Initialize lifecycle state to `New`.

Emit domain event:
- `MeasureCaseCreated`

---

## 5. Initial Risk Detection

For newly created MeasureCases:

- Evaluate early adherence signals (e.g., declining PDC, GNR).
- Flag at-risk indicators for downstream workflows.
- Emit domain events if required (e.g., `InitialRiskDetected`).

Risk evaluation logic is governed by `Adherence_Rules.md`.

---

## 6. Lifecycle Activation

After initialization:

- Transition MeasureCase from `New` to `Active`.
- Emit domain event:
  - `MeasureCaseActivated`

State transition rules are governed by `State_Transition_Rules.md`.

---

# Outputs

For each eligible Measure:

- A new MeasureCase is created.
- Lifecycle state is set to `Active`.
- Domain events are emitted.
- MeasureCase becomes eligible for the Contact Workflow.

For ineligible Members:

- No MeasureCase is created.
- Workflow terminates without lifecycle changes.

---

# Escalation Conditions

Escalation events may be emitted if:

- Member is hospitalized.
- Member is deceased.
- Member is disenrolled.
- Critical data discrepancy detected.
- Incorrect measure assignment identified.

Escalation logic is governed by `Escalation_Rules.md`.

---

# Edge Case Handling

- Medication discontinued but still counted in measure.
- Recent refill outside claims visibility window.
- Dual coverage discrepancies.
- Partial eligibility due to plan transitions.

Edge cases are handled through rule evaluation and event emission.

---

# Dependencies

- `02_Domain/MeasureCase.md`
- `04_Rules/Eligibility_Rules.md`
- `04_Rules/Adherence_Rules.md`
- `04_Rules/State_Transition_Rules.md`
- `04_Rules/Escalation_Rules.md`
- `06_Automation/Domain_Events.md`

---

# Version History

Version 1.0.0 – 2026-03-01 – Governance-compliant workflow aligned to MeasureCase episode-based architecture