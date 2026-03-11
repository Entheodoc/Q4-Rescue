# Rescue Workflow Overview

## Metadata

Document ID: WF-RESCUE-001
Status: Active
Version: 0.1.0
Last Updated: 2026-03-11
Owner: Jose Palomino
Layer: Workflow
Parent Document: PRD-MASTER-001

---

## Purpose

This document is a working visual reference for the current rescue operations model.

It combines:

- the current domain structure
- the current high-level workflow

It is intended to support design conversations and should be updated as the model changes.

---

## Domain Structure

```mermaid
graph TD
    M["Member"]
    R["Referral"]
    C["Case<br/>Aggregate Root"]
    ME["Measure"]
    MD["Medication"]
    B["Barrier"]
    T["Task"]
    CA["ContactAttempt"]
    TCA["TaskContactAttempt"]
    P["Provider"]
    PH["Pharmacy"]
    MP["MedicationProvider"]
    MPH["MedicationPharmacy"]

    M -->|"1 to many"| R
    M -->|"1 to many over time"| C

    R -->|"1 to 1"| C

    C -->|"1 to many"| ME
    C -->|"1 to many"| B
    C -->|"1 to many"| T

    ME -->|"1 to many"| MD

    MD -->|"1 to many"| MP
    MD -->|"1 to many"| MPH

    MP -->|"many to 1"| P
    MPH -->|"many to 1"| PH

    T -->|"many to many via"| TCA
    CA -->|"many to many via"| TCA

    CA -->|"targets one"| M
    CA -->|"targets one"| P
    CA -->|"targets one"| PH
```

---

## Workflow Overview

```mermaid
flowchart TD
    A["Referral arrives"] --> B["Find or create Member"]
    B --> C["Create Case"]
    C --> D["Add Measure(s)"]
    D --> E["Add Medication(s)"]
    E --> F["Identify Barrier(s)"]
    F --> G["Create Task(s)"]
    G --> H["Perform outreach"]
    H --> I["Log ContactAttempt"]
    I --> J["Link Task to ContactAttempt<br/>through TaskContactAttempt"]
    J --> K["Update Task / Barrier / Case status"]
```

---

## Key Modeling Notes

- `Case` is the aggregate root.
- `Referral` creates exactly one `Case`.
- `Task` is case-scoped work.
- `ContactAttempt` is the real communication event.
- `TaskContactAttempt` links work to communication when one event affects one or more tasks.
- `Provider` and `Pharmacy` are shared actors that may appear across many cases.
- `MedicationProvider` and `MedicationPharmacy` are relationship objects, not just technical join tables.

---

## Open Design Areas

- exact fields for `Measure`
- exact fields for `Medication`
- exact fields for `Provider`
- exact fields for `Pharmacy`
- exact fields for `MedicationProvider`
- exact fields for `MedicationPharmacy`
- whether any barriers need optional measure-level or medication-level references

---

## Version History

Version 0.1.0 - 2026-03-11 - Initial visual overview for the current rescue domain and workflow.
