---
lane: free_exploration
surface: page
---

# Intent Workflow: Page Free Exploration

Use this workflow for no-Library open-ended page/UI creation with no 1:1 restoration target.

## Context Requirements

- `shared-runtime/runtime-boundaries/lane-runtime-contracts.md`
- `shared-runtime/agent-dispatch-runtime/lane-dispatch-index.md`
- `delivery-quality/page-rendering-quality-gate.md`
- `delivery-quality/design-artifact-validation.md`
- `delivery-quality/delivery-evidence-contract.md`
- `visual-experience/visual-experience-guidelines.md`

## Runtime Files

- Workflow entry: `start-free-exploration-project.md`
- Page runtime guide: `free-exploration-page-runtime.md`
- Dispatch contract: `dispatch-contract.md`
- Summary fields: `orchestration-summary-fields.md`
- Optional creative guidance: `creative-direction-guidelines.md`, `visual-style-discovery.md`

## Hard Rules

- Do not read restore or Library-bound workflow files.
- Do not use the blocked legacy page template.
- Dispatch contract must not contain Library identity or restore evidence fields unless inherited from an explicit source project heritage.

## Workflow

1. Initialize the project and write `resolvedLane: "free_exploration"`.
2. Build compact page briefs, creative recipe, CSS preflight evidence, and `.design` page nodes.
3. For multi-page, stateful, tabbed, or closed-loop UI requests, write `project.pageCompletenessGate` before dispatch.
4. Build dispatch preflight records for `FreePagePacket`.
5. Dispatch page work with `free-exploration-page-runtime.md`.

## Dispatch

- Page runtime guide: `free-exploration-page-runtime.md`.
- Dispatch contract: `dispatch-contract.md`.
- Supplementary reads are allowed only when declared in the packet; do not load strict Library or restore runbooks.

## Summary Writes

- Required fields are defined in `orchestration-summary-fields.md`.
- `dispatchPreflightManifest[]` must point to this lane's page runtime guide.

## Delivery Quality Gate

- Run `shared-runtime/deterministic-tooling/validate-design-workspace.mjs` before final delivery.
- Free lane style issues may remain warnings, but render and `.design` validity are blocking.

## Completion Evidence

- Completion must include generated page count, page node ids, validation result, and any reduced-scope reason.
- When `project.pageCompletenessGate` exists, completion must report all required pages, states, interactions, and navigation rows as done, reduced-scope, or blocked.
