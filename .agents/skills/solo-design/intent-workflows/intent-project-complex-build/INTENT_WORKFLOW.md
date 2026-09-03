---
lane: complex_html_page
surface: project
---

# Intent Workflow: Project Complex Build

Use this workflow for long PRDs, multi-page projects, generation trees, layout-static graphics, fragment mode, and complex interaction/state expansion.

## Context Requirements

- `shared-runtime/runtime-boundaries/lane-runtime-contracts.md`
- `shared-runtime/agent-dispatch-runtime/lane-dispatch-index.md`
- `shared-runtime/agent-dispatch-runtime/shared-page-rendering-kernel.md` as Declared Load for Page Sub-Agent shared runtime.
- `delivery-quality/page-rendering-quality-gate.md`
- `delivery-quality/design-artifact-validation.md`
- `delivery-quality/delivery-evidence-contract.md`
- `visual-experience/visual-experience-guidelines.md`
- `visual-experience/visual-checkpoint-protocol.md`

## Runtime Files

- Entry: `start-complex-project-build.md`
- Phase runbooks: `00-requirement-and-style-intake.md`, `01-graphic-asset-preparation.md`, `02-page-composition.md`, `03-interaction-validation-delivery.md`
- Page runtime guides: `complex-page-runtime.md`, `graphic-layout-page-runtime.md`
- Dispatch contracts: `complex-page-dispatch-contract.md`, `graphic-layout-dispatch-contract.md`
- Summary fields: `orchestration-summary-fields.md`
- Planning: `page-composition-tree.md`, `interaction-wiring-plan.md`

## Hard Rules

- Dispatch children only after parent/shared fragments exist.
- Layout-static graphic deliverables must remain editable HTML and must not degrade to image-only.
- Layout-static graphic dispatch requires `project.deliverableCompletenessChecklist` before page dispatch; missing required copy, dates, prices, tables, sections, or pages is blocking unless explicitly reduced in scope.
- Layout-static graphic dispatch requires `project.visualQualityCheckpoints[]` before page dispatch; missing visual-anchor, information-hierarchy, composition-structure, or implementation-strategy checkpoint is blocking.
- Shared page kernel is declared per need and is not an Always Load file.

## Workflow

1. Run `00-requirement-and-style-intake.md` to create project skeleton, summary, CSS preflight, and lane mode.
2. Run `01-graphic-asset-preparation.md` only when page assets are needed.
3. Run `02-page-composition.md` to build dispatch preflight records and dispatch page/subtree work.
4. Run `03-interaction-validation-delivery.md` for wiring, validation, repair, and delivery evidence.

## Dispatch

- Complex page runtime guide: `complex-page-runtime.md`.
- Layout-static graphic runtime guide: `graphic-layout-page-runtime.md`.
- Dispatch contracts: `complex-page-dispatch-contract.md` or `graphic-layout-dispatch-contract.md`.
- Shared kernel is declared only for Page Sub-Agent execution.

## Summary Writes

- Required fields are defined in `orchestration-summary-fields.md`.
- `graphic_layout_static` and `complex_html_page` are resolved at the end of intake before page dispatch.

## Delivery Quality Gate

- Run `shared-runtime/deterministic-tooling/validate-lane-runtime-contract.mjs` before dispatch when summary exists.
- Run `shared-runtime/deterministic-tooling/validate-design-workspace.mjs` before final delivery.

## Completion Evidence

- Completion must include phase readiness, dispatch manifest proof, generated page/fragments, validation result, and any remaining blocking issue.
