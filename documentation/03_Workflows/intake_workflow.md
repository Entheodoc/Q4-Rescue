# Intake Workflow

## Metadata

Document ID: WF-INTAKE-001
Status: Active
Version: 2.0.0
Last Updated: 2026-03-11
Owner: José Palomino
Layer: Workflow
Parent Document: PRD-MASTER-001

---

# Purpose

The Intake Workflow receives a Referral, validates intake data, determines whether rescue work should be opened, creates a Case for the Member, and initializes the starting Measure and Medication work context.

This workflow orchestrates domain interactions but does not define business rules, lifecycle rules, or state transition logic.

Eligibility logic is defined in `04_Rules/Eligibility_Rules.md`.

Case lifecycle behavior is defined in `02_Domain/case.md`.

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
4. Create one Case from the Referral when rescue work should be opened.
5. Emit appropriate domain events.

---

# Orchestration Steps

## 1. Referral Validation

- Confirm Member is active in the program.
- Verify enrollment status.
- Confirm correct plan assignment.
- Validate referral data completeness.

If Member is not active:
- No Case is created.
- Workflow terminates.

---

## 2. Data Verification

- Validate demographic information.
- Confirm primary care provider or primary provider information when available.
- Confirm pharmacy information.
- Identify critical data discrepancies.

If PCP information is captured, treat it as member-level context rather than medication-level provider data. A future member-to-provider relationship may model that explicitly if it becomes operationally important.

If discrepancies are detected:
- Emit appropriate escalation events as defined in `Escalation_Rules.md`.

---

## 3. Measure Eligibility Evaluation

For each supported adherence Measure (e.g., DM, RASA, Statin):

- Apply eligibility rules defined in `Eligibility_Rules.md`.
- Determine whether the Member qualifies for that Measure.

If eligible:
- Proceed to Case creation and measure initialization.

If not eligible:
- No new rescue work is opened for that referral.

---

## 4. Case Creation

For a referral that should open rescue work:

- Instantiate a new Case.
- Link the Case to exactly one Referral and one Member.
- Assign a unique CaseID.
- Initialize lifecycle state to `open`.
- Create the starting Measure and Medication records needed for the Case.

Emit domain event:
- `CaseCreated`

---

## 5. Initial Risk Detection

For the newly created Case and its Measures:

- Evaluate early adherence signals (e.g., declining PDC, GNR).
- Flag at-risk indicators for downstream workflows.
- Emit domain events if required (e.g., `InitialRiskDetected`).

Risk evaluation logic is governed by `Adherence_Rules.md`.

---

## 6. Initial Work Activation

After initialization, downstream Tasks may be created based on identified barriers, measures, and medications.

Task creation and follow-up sequencing are governed by workflow and rule documents rather than by a special intake-only activation state.

---

# Outputs

For each referral that opens rescue work:

- A new Case is created.
- Initial Measure and Medication context is recorded.
- Domain events are emitted.
- The Case becomes eligible for downstream task creation and contact workflows.

For ineligible Members:

- No Case is created.
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

- `02_Domain/case.md`
- `04_Rules/Eligibility_Rules.md`
- `04_Rules/Adherence_Rules.md`
- `04_Rules/State_Transition_Rules.md`
- `04_Rules/Escalation_Rules.md`
- `06_Automation/Domain_Events.md`

---

# Version History

Version 2.0.0 – 2026-03-11 – Workflow revised to align intake around Referral and Case instead of MeasureCase.
Version 1.0.0 – 2026-03-01 – Governance-compliant workflow aligned to MeasureCase episode-based architecture
