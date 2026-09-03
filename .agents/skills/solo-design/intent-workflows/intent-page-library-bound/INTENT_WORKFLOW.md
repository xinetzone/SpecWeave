---
lane: library_bound
surface: page
---

# Intent Workflow: Page Library Bound

Use this workflow when an active Design Library identity, token reference, component plan, or UI Kit exists.

## Context Requirements

- `shared-runtime/runtime-boundaries/lane-runtime-contracts.md`
- `shared-runtime/agent-dispatch-runtime/lane-dispatch-index.md`
- `delivery-quality/page-rendering-quality-gate.md`
- `delivery-quality/design-artifact-validation.md`
- `delivery-quality/delivery-evidence-contract.md`
- `visual-experience/visual-experience-guidelines.md` only as fallback for gaps not covered by Library evidence.

## Runtime Files

- Workflow entry: `start-library-bound-project.md`
- Page runtime guide: `library-bound-page-runtime.md`
- Dispatch contract: `dispatch-contract.md`
- Summary fields: `orchestration-summary-fields.md`
- Library ingestion: `design-library-ingestion.md`
- Fidelity rules: `design-token-fidelity-rules.md`, `component-conformance-rules.md`, `icon-source-priority-rules.md`

## Hard Rules

- Library identity and actual token references are hard requirements.
- Library evidence wins over generic visual-experience guidance.
- Do not use free-exploration runtime shortcuts.

## Workflow

1. Confirm Library identity, token source, component plan, and UI Kit evidence.
2. Write `resolvedLane: "library_bound"` after identity confirmation.
3. Create page nodes and page packets with strict Library evidence.
4. Dispatch page work with `library-bound-page-runtime.md`.

## Dispatch

- Page runtime guide: `library-bound-page-runtime.md`.
- Dispatch contract: `dispatch-contract.md`.
- Packet must include Library identity, token reference, component evidence, and strict token fidelity.

## Summary Writes

- Required fields are defined in `orchestration-summary-fields.md`.
- `designSource.libraryIdentity` and runtime Library identity must match.

## Delivery Quality Gate

- Run `shared-runtime/deterministic-tooling/validate-design-workspace.mjs`.
- Missing Library identity, token reference, or strict token fidelity evidence is blocking.

## Completion Evidence

- Completion must include Library identity, token evidence, component conformance evidence, validation result, and page node ids.
