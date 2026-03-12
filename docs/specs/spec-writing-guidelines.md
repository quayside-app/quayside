# Spec Writing Guidelines

Reference: [openai/symphony SPEC.md](https://github.com/openai/symphony/blob/main/SPEC.md)

When planning a project that needs a spec, produce a document following this structure and these principles.

## Document Structure

### 1. Header
- Title: `<Project Name> Service Specification` (or Feature/System Specification)
- Status line: `Status: Draft v1` (or RFC, Final, etc.)
- Purpose: One sentence describing what the system does.

### 2. Problem Statement (Section 1)
- One paragraph defining what the system is.
- Bulleted list of 3-5 operational problems it solves.
- "Important boundary" subsection: what the system is NOT responsible for.

### 3. Goals and Non-Goals (Section 2)
- **Goals**: Bulleted list of concrete, verifiable behaviors the system must support.
- **Non-Goals**: Explicit list of things that are out of scope. This prevents scope creep and sets expectations.

### 4. System Overview (Section 3)
- **Main Components**: Numbered list. Each component gets a name (backtick-quoted), 2-4 bullet points describing its responsibility.
- **Abstraction Levels/Layers**: Name each layer and its concern. Helps implementors understand where code belongs.
- **External Dependencies**: Bulleted list of everything outside the system boundary.

### 5. Core Domain Model (Section 4)
- **Entities**: Each entity gets its own subsection with:
  - One-line description of what it represents.
  - `Fields:` bulleted list where each field has:
    - Name (backtick-quoted) + type in parentheses
    - Indented bullet explaining semantics, defaults, nullability
- **Normalization Rules**: Explicit rules for how identifiers are sanitized, compared, composed.

### 6. Subsystem Specifications (Sections 5-12)
One section per major subsystem. Each section follows this pattern:
- **Discovery/Resolution**: How the subsystem finds its inputs.
- **Format/Schema**: The exact shape of config, messages, or data.
  - For config: field name, type, default, dynamic reload behavior.
  - For protocols: exact message sequence with JSON examples.
- **Validation and Error Surface**: Named error classes. What blocks operation vs. what fails gracefully.
- **Behavioral Contract**: Step-by-step what happens, in what order, under what conditions.

Key subsystem sections to consider:
- Configuration (sources, precedence, dynamic reload, validation)
- State Machine (states, transitions, triggers, idempotency rules)
- Scheduling/Coordination (polling, candidate selection, concurrency, retry/backoff formulas)
- Resource Management (lifecycle, creation, reuse, cleanup, safety invariants)
- Integration Protocols (launch contract, handshake sequence, streaming, event handling)
- External Service Integration (required operations, query semantics, normalization, error handling)
- Prompt/Template Construction (inputs, rendering rules, failure semantics)

### 7. Observability (Section 13)
- **Logging Conventions**: Required context fields, message formatting rules.
- **Logging Outputs**: What sinks are required/optional.
- **Metrics**: What must be tracked (tokens, runtime, etc.), accounting rules.
- **Optional API/Dashboard**: If applicable, define endpoints with example JSON response shapes.

### 8. Failure Model (Section 14)
- **Failure Classes**: Numbered categories (config, workspace, session, external service, observability).
- **Recovery Behavior**: For each failure class, what happens (skip dispatch, retry, keep running, etc.).
- **Restart Recovery**: What state survives restarts and what doesn't. How the system bootstraps from nothing.
- **Operator Intervention Points**: How operators can control behavior without code changes.

### 9. Security (Section 15)
- **Trust Boundary**: What is trusted, what isn't. What each implementation must document.
- **Filesystem/Resource Safety**: Mandatory invariants (path containment, sanitization).
- **Secret Handling**: How secrets are referenced, resolved, and protected from logging.
- **Hardening Guidance**: Possible measures, explicitly not mandating a single posture.

### 10. Reference Algorithms (Section 16)
- Language-agnostic pseudocode for the most complex flows.
- Use `function name():` style with clear variable names.
- Cover: startup, main loop, reconciliation, dispatch, worker lifecycle, retry handling.
- These are reference implementations, not prescriptive code.

### 11. Test and Validation Matrix (Section 17)
- Define validation profiles: Core Conformance, Extension Conformance, Real Integration.
- Organize test requirements by subsystem.
- Each bullet is a specific testable behavior, not a vague category.
- Extension tests are prefixed with "If ... is implemented".
- Real integration tests acknowledge credential/network requirements.

### 12. Implementation Checklist (Section 18)
- Definition of Done, organized by the same validation profiles.
- Each item is a concrete deliverable, not a process step.
- Include a "Recommended Extensions" section with TODO items for future work.
- Include "Operational Validation" for pre-production checks.

## Writing Principles

### Be Explicit About Defaults
Every configurable value must have:
- Type (string, integer, map, list)
- Default value (exact, not "reasonable")
- Whether it supports dynamic reload
- Coercion rules (string-to-int, comma-separated-to-list, etc.)

### Be Explicit About Error Handling
For every operation that can fail:
- Name the error class
- State what happens to the caller (abort, skip, retry, log-and-continue)
- State what happens to the system (keep running, block dispatch, fail startup)

### Separate Required from Optional
- Use clear language: "required for conformance" vs "optional extension"
- Optional features that are implemented must still meet their extension spec
- Never leave it ambiguous whether something is required

### Use Concrete Examples
- JSON examples for message formats and API responses
- Pseudocode for algorithms
- Example values for config fields

### State What You Don't Prescribe
- "Implementation-defined" for things that vary by deployment
- "This specification does not require..." for explicit non-requirements
- "The spec does not prescribe..." followed by what IS required

### Forward Compatibility
- Unknown config keys should be ignored
- Document extensibility points
- Extensions should document their own schema

### Normalization Rules
- Always specify how strings are compared (trim + lowercase, exact match, etc.)
- Always specify how identifiers are sanitized
- Always specify how composite keys are formed

### Cross-Reference
- Use "Section X.Y" references when behaviors depend on other sections
- Include a "Cheat Sheet" subsection for config fields that are scattered across sections
- Repeat critical information (like safety invariants) where it matters, noting the repetition is intentional

## Section Numbering Convention
- Top-level sections: `## 1. Problem Statement`
- Subsections: `### 1.1 Goals`
- Sub-subsections: `#### 1.1.1 Specific Topic`
- Consistent depth — don't go deeper than 3 levels

## Length Calibration
- A spec for a significant system should be 1500-2500 lines.
- Each subsystem section: 100-200 lines.
- Domain model: 150-250 lines.
- Test matrix: 100-150 lines.
- Reference algorithms: 200-300 lines of pseudocode.
- If it's shorter than 500 lines, it's probably missing failure handling, test requirements, or normalization rules.

## Relationship to ADRs

Every spec should link to its corresponding ADR, and vice versa.

- **ADR** answers *"why this approach?"* — write it first to get alignment.
- **Spec** answers *"how do we build it?"* — write it after the ADR is accepted.

Include this in the spec header:

```
ADR: [docs/decisions/YYYY-MM-DD-adr-name.md](../decisions/YYYY-MM-DD-adr-name.md)
```

Specs live in `docs/specs/` and follow the naming convention `YYYY-MM-DD-spec-name.md`.
