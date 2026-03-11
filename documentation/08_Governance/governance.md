# Governance

## Metadata

Document ID: GOV-GOVERNANCE-001
Status: Active
Version: 2.0.0
Last Updated: 2026-03-11
Owner: José Palomino
Layer: Governance
Parent Document: PRD-MASTER-001

---

# Purpose

This document defines documentation standards, versioning policies, structural rules, and architectural discipline for the Medication Adherence Platform Specification repository.

The goal of Governance is to:

- Prevent architectural drift
- Maintain consistency across documents
- Ensure scalability of documentation
- Support team collaboration
- Protect domain integrity
- Enable long-term SaaS evolution

Governance rules must be followed before modifying system structure.

---

# 1. Repository Structure Standard

The repository must follow this structure:

Medication-Adherence-Platform-Spec/
│
├── 00_Master_Index.md
├── 01_Product/
├── 02_Domain/
├── 03_Workflows/
├── 04_Rules/
├── 05_Data_Model/
├── 06_Automation/
├── 07_Dashboard/
├── 08_Governance/
└── 99_Archive/

No documents should exist outside this structure.

Structural changes require updates to:
1. Master Index
2. Governance
3. Then individual documents

---

# 2. Layer Responsibilities

Each folder has a strict responsibility:

## 01_Product
Defines vision, strategy, and roadmap.
Must not define domain logic.

## 02_Domain
Defines core entities and aggregate roots.
Defines state and invariants.
Must not define workflow sequencing.
Must not define UI logic.
Must not define automation triggers.

## 03_Workflows
Defines orchestration logic.
Coordinates domain interactions.
Must not define business rules.
Must not define lifecycle rules.

## 04_Rules
Defines deterministic business logic.
Defines eligibility.
Defines state transitions.
Defines escalation logic.
Must not define orchestration steps.

## 05_Data_Model
Defines structural persistence model.
Defines entity relationships.
Defines field-level specifications.

## 06_Automation
Defines domain events.
Defines trigger logic.
Defines voice-agent integrations.
Automation reacts to domain events.
Automation must not override domain state rules.

## 07_Dashboard
Defines projection and KPI logic.
Dashboard reflects domain state.
Dashboard must not define domain behavior.

## 08_Governance
Defines documentation standards and structural discipline.

## 99_Archive
Stores deprecated or historical specifications.
Archived documents are immutable.

---

# 3. Document Structure Standard

Every document must follow this structural order:

1. Title (H1)
2. Metadata block
3. Horizontal separator (`---`)
4. Purpose section (`---`)
5. Structured content sections separated by horizontal separators (`---`)
6. Dependencies section (if applicable) (`---`)
7. Version History section 

The exact naming of content sections may vary depending on the document layer.

Examples:

- Domain documents may include:
  - Attributes
  - Lifecycle States
  - State Transitions
  - Invariants
  - Emitted Events

- Workflow documents may include:
  - Inputs
  - Core Objectives
  - Orchestration Steps
  - Outputs
  - Escalation Conditions

- Rules documents may include:
  - Rule Definitions
  - Preconditions
  - Validation Logic

- Automation documents may include:
  - Event Definitions
  - Trigger Conditions
  - External Integrations

The required order must be preserved, but section names may vary based on context.

---

# 4. Required Metadata Block

Every document must include a Metadata section immediately below the title.

Standard format:

```markdown
## Metadata

Document ID: <Unique Identifier>
Status: Draft | Active | Deprecated | Archived
Version: X.Y.Z
Last Updated: YYYY-MM-DD
Owner: <Name>
Layer: Product | Domain | Workflow | Rules | Data | Automation | Dashboard | Governance
Parent Document: <Document ID of parent document>
(Not required for root-level documents such as PRD-MASTER-001)

Additional metadata fields may be added where necessary.

The field "System Version Alignment" is required only in PRD-MASTER-001 and other root-level product documents.

---

# 5. Document ID Naming Convention

Document IDs must follow this structure:

[LAYER]-[DESCRIPTOR]-[SEQUENCE]

Where:

- LAYER = One of the approved prefixes
- DESCRIPTOR = Uppercase descriptive identifier of the document concept
- SEQUENCE = Three-digit sequential number per descriptor (001, 002, 003...)

---

## Approved Layer Prefixes

| Layer        | Prefix |
|--------------|--------|
| Product      | PRD    |
| Domain       | DOM    |
| Workflow     | WF     |
| Rules        | RULE   |
| Data Model   | DATA   |
| Automation   | AUTO   |
| Dashboard    | DASH   |
| Governance   | GOV    |

---

## Examples

- PRD-MASTER-000
- DOM-MEASURECASE-001
- DOM-MEMBER-001
- WF-INTAKE-001
- WF-CONTACT-001
- RULE-ELIGIBILITY-001
- AUTO-DOMAIN-EVENTS-001
- DATA-DICTIONARY-001
- DASH-KPI-001

---

## Rules

- Document IDs must be unique.
- Document IDs must never change once assigned.
- Document IDs must not be reused.
- File renaming does not change Document ID.
- Sequence numbers are maintained per descriptor category.
---

# 6. Versioning Policy

Semantic versioning must be used:

MAJOR.MINOR.PATCH

- MAJOR: Breaking architectural change
- MINOR: Structural enhancement or new feature layer
- PATCH: Clarifications or non-structural edits

Grammar edits alone do NOT require version bumps.

Version numbers apply at the document level. 

The version number in 00_Master_Index.md represents system-level architecture version.

---

# 7. State and Lifecycle Discipline

Only Domain documents may define lifecycle states.

Workflows may reference states but may not redefine them.

Rules may define allowed transitions but may not redefine entities.

Automation may emit events but may not override state transition rules.

Archived domain records defined as terminal by the active domain model are immutable and must never be reactivated.

---

# 8. Domain Event Discipline

Domain Events must be defined only in 06_Automation/Domain_Events.md.
Domain documents may declare emitted events but may not define event handling logic.
Automation may react to events but may not define new domain state transitions outside Rule definitions.
Event names must be stable and versioned.

---

# 9. Archive Policy

When a document is replaced or deprecated:

- Move it to `99_Archive/`
- Update its Status to Archived
- Do not modify archived documents

Archived documentation files are also immutable.

---

# 10. Architectural Integrity Rules

The following must always remain true:

- Case is the aggregate root for rescue operations.
- Each Referral creates exactly one Case.
- Member is the persistent person identity across time.
- ContactAttempt is communication-scoped, not case-scoped.
- Archived cases are never reactivated.
- Domain defines state.
- Rules define transitions.
- Workflows orchestrate.
- Automation reacts.
- Dashboard projects.

If a change violates these principles, Governance must be updated before implementation.

---

# 11. Documentation Evolution

Before modifying repository structure:

1. Update Master Index if architecture changes.
2. Update Governance if standards change.
3. Only then modify individual documents.

This prevents structural drift.

---

# 12. File Naming Convention

This section defines the official filename standard for all documents in the repository.

File naming discipline ensures:

- Long-term structural consistency
- Cross-platform compatibility
- CLI and tooling safety
- Predictable sorting behavior
- Clear separation between document identity and storage naming

---

## 12.1 Core Principles

1. **Document ID is the authoritative identity.**
   - The Document ID defined in the Metadata block is immutable.
   - Document IDs must never change once assigned.
   - Document IDs must remain unique across the repository.

2. **File name is not the authoritative identity.**
   - File names may differ from the Document ID.
   - File renaming does not change the Document ID.
   - File names exist for repository navigation and filesystem organization only.

3. **File naming must prioritize engineering safety.**
   - The repository must remain compatible with:
     - macOS
     - Linux
     - Containers
     - CI/CD pipelines
     - CLI tooling

---

## 12.2 Standard Format

All file names must:

- Use lowercase snake_case
- Use underscores between logical words
- Avoid spaces
- Avoid special characters (except underscores)
- End in `.md`
- Not include version numbers
- Not include status labels (Draft, Active, Archived, etc.)
- Not duplicate the layer prefix already expressed in the folder structure

---

### Examples

| Document ID | Folder | Valid File Name |
|-------------|--------|----------------|
| DOM-MEASURECASE-001 | 99_Archive | measure_case.md |
| DOM-CASE-001 | 02_Domain | case.md |
| DOM-MEMBER-001 | 02_Domain | member.md |
| DOM-REFERRAL-001 | 02_Domain | referral.md |
| DOM-BARRIER-001 | 02_Domain | barrier.md |
| DOM-TASK-001 | 02_Domain | task.md |
| DOM-CONTACTATTEMPT-001 | 02_Domain | contact_attempt.md |
| DOM-TASKCONTACTATTEMPT-001 | 02_Domain | task_contact_attempt.md |
| WF-INTAKE-001 | 03_Workflows | intake_workflow.md |
| RULE-ELIGIBILITY-001 | 04_Rules | eligibility_rules.md |
| DATA-DICTIONARY-001 | 05_Data_Model | data_dictionary.md |
| GOV-GOVERNANCE-001 | 08_Governance | governance.md |

---

## 12.3 Layer Responsibility Alignment

Folder structure defines document layer:

- `01_Product/`
- `02_Domain/`
- `03_Workflows/`
- `04_Rules/`
- `05_Data_Model/`
- `06_Automation/`
- `07_Dashboard/`
- `08_Governance/`
- `99_Archive/`

Therefore:

- File names must not repeat layer prefixes (DOM, WF, RULE, etc.).
- Layer identity is determined by:
  - Folder placement
  - Metadata `Layer` field
  - Document ID prefix

---

## 12.4 Immutability and Archiving

- File renaming is permitted if clarity improves.
- Document ID must never change.
- When a document is deprecated:
  - Move the file to `99_Archive/`
  - Update Metadata `Status` to `Archived`
  - Archived documents must not be modified.

---

## 12.5 Structural Separation Rule

The following separation must always remain true:

- **Document ID = Structural Identity**
- **File Name = Filesystem Navigation**
- **Title (H1) = Human Concept Label**

These three elements must remain independent.

If a proposed change causes them to collapse into one another, Governance must be updated before implementation.

---

# 13. Document Title Convention

This section defines the official H1 title standard for all documents in the repository.

Title discipline ensures:

- Clear human readability
- Alignment with Domain-Driven Design (DDD) principles
- Separation between domain concepts and filesystem concerns
- Long-term architectural consistency

---

## 13.1 Core Principles

1. **The H1 title represents the conceptual subject of the document.**
   - It must be human-readable.
   - It must reflect the canonical domain concept.
   - It must not mirror the file name format.

2. **The H1 title must not include the Document ID.**
   - Document ID belongs exclusively in the Metadata block.
   - The title must remain concept-focused, not structural.

3. **Titles must preserve canonical domain naming.**
   - Aggregate names must appear exactly as defined in the domain model.
   - Compound domain objects must not be split into grammatical phrases if they represent a single domain type.

---

## 13.2 Domain Layer Title Rules

For Domain documents:

- Aggregate names must be written in PascalCase if they represent a domain type.
- Supporting entities must use their canonical domain names.
- Titles may optionally include a descriptive subtitle if clarity requires it.

### Examples

| Document ID | File Name | Valid H1 Title |
|-------------|-----------|----------------|
| DOM-MEASURECASE-001 | measure_case.md | # MeasureCase Aggregate Root (Archived) |
| DOM-CASE-001 | case.md | # Case |
| DOM-MEMBER-001 | member.md | # Member Entity |
| DOM-CONTACTATTEMPT-001 | contact_attempt.md | # ContactAttempt Entity |

Incorrect examples:

- `# Measure Case Aggregate Root` ❌ (breaks canonical domain type)
- `# DOM-MEASURECASE-001` ❌ (ID belongs in metadata)
- `# measure_case` ❌ (file format leakage into title)

---

## 13.3 Workflow Layer Title Rules

Workflow documents must describe orchestration behavior in clear English.

- Titles should use natural language.
- Workflow names may use spaced words.
- They should not mimic snake_case.

### Examples

| Document ID | File Name | Valid H1 Title |
|-------------|-----------|----------------|
| WF-INTAKE-001 | intake_workflow.md | # Intake Workflow |
| WF-CONTACT-001 | contact_workflow.md | # Contact Workflow |
| WF-CLOSURE-001 | closure_workflow.md | # Closure Workflow |

---

## 13.4 Rules Layer Title Rules

Rules documents define deterministic business logic.

Titles should reflect the rule domain clearly and descriptively.

### Examples

| Document ID | File Name | Valid H1 Title |
|-------------|-----------|----------------|
| RULE-ELIGIBILITY-001 | eligibility_rules.md | # Eligibility Rules |
| RULE-STATE-TRANSITIONS-001 | state_transition_rules.md | # State Transition Rules |

---

## 13.5 Automation and Data Model Titles

Automation and Data documents should describe structural or event-driven concepts clearly.

### Examples

| Document ID | File Name | Valid H1 Title |
|-------------|-----------|----------------|
| AUTO-DOMAIN-EVENTS-001 | domain_events.md | # Domain Events |
| DATA-DICTIONARY-001 | data_dictionary.md | # Data Dictionary |

---

## 13.6 Structural Separation Rule

The following must always remain true:

- **Document ID = Structural Identity**
- **File Name = Filesystem Navigation (snake_case)**
- **H1 Title = Canonical Human Concept**

These three must remain independent.

If a change causes leakage between filesystem naming and domain language, Governance must be updated before implementation.

---

## 13.7 Architectural Integrity Reminder

In the Domain layer:

- Aggregates are proper nouns.
- Aggregate names must be stable.
- Canonical naming must not drift over time.

If the aggregate name changes, this constitutes a MAJOR architectural revision.

---

# 14. Structural Change Protocol

This section defines the mandatory review process for any structural modification to the repository.

A structural change is any modification that affects:

- Repository structure
- Document naming conventions
- Layer responsibilities
- Aggregate definitions
- Lifecycle states
- Invariants
- Cross-layer contracts
- Canonical domain vocabulary

Structural changes must follow a top-down review sequence to prevent architectural drift.

---

## 14.1 Definition of Structural Change

A change is considered structural if it modifies any of the following:

- Folder hierarchy
- Document ID patterns
- File naming standards
- Layer responsibilities
- Aggregate root identity
- Lifecycle states
- State invariants
- Domain event vocabulary
- Canonical entity names
- Cross-document references

Grammar edits, clarifications, or formatting corrections are not structural changes.

---

## 14.2 Mandatory Review Sequence

Structural changes must follow this order:

1. Governance
2. PRD-MASTER-001
3. Affected Layer Documents
4. Cross-Reference Audit
5. Version Review

No structural change may begin at the Domain, Workflow, Rules, or Automation layer without first validating Governance alignment.

Bottom-up structural edits are prohibited.

---

## 14.3 Governance Alignment Check

Before implementing a structural change, confirm:

- Does the change affect naming conventions?
- Does it modify layer responsibilities?
- Does it introduce a new document category?
- Does it alter architectural separation principles?

If YES:

- Update Governance first.
- Increment version according to Versioning Policy.
- Then update PRD.
- Then update affected documents.

---

## 14.4 PRD Alignment Check

If the structural change impacts:

- System architecture description
- Aggregate definitions
- Lifecycle model
- Folder structure
- Core system principles

PRD-MASTER-001 must be updated before modifying lower-layer documents.

PRD is the authoritative architectural reference.

---

## 14.5 Layer Discipline Verification

Before finalizing a structural change, confirm:

- Domain defines state and invariants only.
- Rules define transitions and deterministic logic.
- Workflows define orchestration only.
- Automation defines reactions and integrations only.
- Dashboard defines projections only.

If a change causes responsibility leakage across layers, it must be corrected before approval.

---

## 14.6 Aggregate Boundary Protection

If the change touches Domain:

Verify:

- Case remains the aggregate root unless Governance is intentionally revised again.
- Each Referral still creates exactly one Case.
- Archived cases remain immutable.
- ContactAttempt remains outside the Case aggregate and links through TaskContactAttempt.
- Subordinate entities remain inside the intended aggregate boundary.

Any violation of these principles constitutes a MAJOR architectural revision.

---

## 14.7 Naming Integrity Verification

Before committing a structural change:

- Confirm file names follow snake_case.
- Confirm Document IDs remain unchanged.
- Confirm H1 titles follow Title Convention.
- Confirm canonical domain names are preserved.
- Confirm no grammatical phrasing replaces domain type names.

Naming drift must be corrected before merge.

---

## 14.8 Cross-Reference Audit

After updating documents:

- Search the repository for outdated file names.
- Search for outdated state names.
- Search for outdated terminology.
- Confirm no stale references remain.

This prevents silent divergence across layers.

---

## 14.9 Versioning Determination

Apply Semantic Versioning rules:

- PATCH: Clarifications or non-structural edits.
- MINOR: Structural enhancement without breaking architectural principles.
- MAJOR: Breaking changes to aggregates, lifecycle model, or invariants.

If uncertain, default to MINOR.

Version changes must be documented in Version History.

---

## 14.10 Final Integrity Check

Before finalizing:

Ask:

If this system operated at scale with:

- Millions of Cases
- Multiple developers
- External integrations
- Automation pipelines

Would this structural decision remain valid?

If not, reconsider before implementation.

---

## 14.11 Architectural Integrity Rule

Structural stability is more important than convenience.

If a structural change introduces ambiguity in:

- Aggregate boundaries
- Lifecycle semantics
- Naming conventions
- Layer responsibilities

The change must be rejected or Governance updated before proceeding.

---

# Version History

Version 2.0.0 – 2026-03-11 – Governance updated to make Case the active aggregate root and retire MeasureCase as the active domain center.
Version 1.0.0 – 2026-03-01 – Initial governance standard established
