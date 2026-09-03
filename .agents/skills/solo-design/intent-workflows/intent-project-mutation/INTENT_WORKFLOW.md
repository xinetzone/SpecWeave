---
lane: existing_edit_add_comparison
surface: project
---

# Intent Workflow: Project Mutation

Use this workflow for existing project edits, redesign copies, variants, and theme customization.

## Context Requirements

- `shared-runtime/runtime-boundaries/lane-runtime-contracts.md`
- `shared-runtime/agent-dispatch-runtime/lane-dispatch-index.md`
- `shared-runtime/agent-dispatch-runtime/shared-page-rendering-kernel.md` as Declared Load when a Page Sub-Agent is needed.
- `delivery-quality/page-rendering-quality-gate.md`
- `delivery-quality/design-artifact-validation.md`
- `delivery-quality/delivery-evidence-contract.md`
- `visual-experience/visual-experience-guidelines.md` conditionally when source project continuity requires it.

## Runtime Files

- Workflows: `edit-existing-project.md`, `redesign-project-ui.md`, `generate-project-variants.md`, `customize-project-theme.md`
- Dispatch contracts: `existing-edit-dispatch-contract.md`, `redesign-dispatch-contract.md`, `variant-dispatch-contract.md`, `theme-customization-dispatch-contract.md`
- Page runtime guides: `existing-edit-page-runtime.md`, `redesign-page-runtime.md`, `variant-page-runtime.md`
- Summary fields: `orchestration-summary-fields.md`
- Comparison page contract: `comparison-page-contract.md`
- Repair flow: `main-agent-repair-workflow.md`

## Hard Rules

- Based-on/reference edits create comparison pages by default.
- Redesign writes a duplicate project, not the source project.
- Variant generation must keep a baseline and explicit variant axis.
- Theme customization updates theme dimensions and must not create new page nodes.

## Workflow

1. Classify mutation mode: existing edit, redesign, variants, theme customize, delete/adopt/refresh, or image append redirect.
2. Confirm source project/page and write the corresponding `resolvedLane`.
3. Apply `comparison-page-contract.md` unless explicit in-place edit is allowed.
4. Dispatch page work or run Main-Agent-only theme/head updates as required.

## Dispatch

- Existing edit runtime guide: `existing-edit-page-runtime.md`.
- Redesign runtime guide: `redesign-page-runtime.md`.
- Variant runtime guide: `variant-page-runtime.md`.
- Theme customize is Main-Agent-owned and uses `theme-customization-dispatch-contract.md` for evidence, not page generation.

## Summary Writes

- Required fields are defined in `orchestration-summary-fields.md`.
- Source project lane heritage must be recorded when Library, restore, or graphic-layout constraints are inherited.

## Delivery Quality Gate

- Run `shared-runtime/deterministic-tooling/validate-lane-runtime-contract.mjs` when a summary exists.
- Run `shared-runtime/deterministic-tooling/validate-design-workspace.mjs` before final delivery when pages exist.

## Completion Evidence

- Completion must include mutation mode, source/target page ids, comparison or in-place proof, validation result, and any source heritage constraints.
