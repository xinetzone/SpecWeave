---
lane: restore_1to1
surface: page
---

# Intent Workflow: Page Restore 1:1

Use this workflow for high-fidelity restoration from screenshot, URL, or screenshot+URL.

## Context Requirements

### Phase A — Route & Dispatch (load at workflow start)

- `intent-workflows/intent-page-restore-1to1/start-restore-1to1-project.md`
- `shared-runtime/agent-dispatch-runtime/lane-dispatch-index.md`
- `intent-workflows/intent-page-restore-1to1/dispatch-contract.md`
- `intent-workflows/intent-page-restore-1to1/restore-dispatch-packet-format.md`

### Phase B — Validation (load only after Sub-Agent returns, Step 11+)

- `delivery-quality/page-rendering-quality-gate.md` (conditionally — post-dispatch)
- `delivery-quality/design-artifact-validation.md` (conditionally — post-dispatch)
- `intent-workflows/intent-page-restore-1to1/restore-evidence-contract.md` (conditionally — post-dispatch)
- `shared-runtime/runtime-boundaries/lane-runtime-contracts.md` (conditionally — post-dispatch)

Main Agent MUST NOT Read Phase B files during Steps 1-10. They are needed only for post-dispatch finalization.
Sub-Agent-only files (`sub-agent-runtime-boundaries.md`, `page-rendering-quality-gate.md`) are included in the Sub-Agent Task dispatch prompt, not in Main Agent's working memory.

## Runtime Files

- Workflow entry: `start-restore-1to1-project.md`
- Page runtime guide: `restore-1to1-page-runtime.md`
- Dispatch contract: `dispatch-contract.md`
- Dispatch packet format: `restore-dispatch-packet-format.md`
- Summary fields: `orchestration-summary-fields.md`
- Evidence contract: `restore-evidence-contract.md`
- Visual checkpoints: `restore-visual-checkpoints.md`

## Hard Rules

- Source material is the visual authority.
- Do not load `visual-experience/` as a creative authority.
- Do not route through free-exploration or shared legacy runtime.
- Restore dispatch must include visual checkpoints and restore evidence review.
- Do not introduce or request a pixel-level validator; high-fidelity generation uses persisted source facts and checkpoints before dispatch.

## Workflow

1. Capture source evidence for screenshot, URL, or screenshot+URL.
2. Write `resolvedLane: "restore_1to1"` after evidence is ready.
3. Build `RestorePagePacket` with checkpoints, high-priority source facts, allowed deviations, and visual spec excerpt.
4. Dispatch page work with `restore-1to1-page-runtime.md`.
5. Record legal completion data into `project.expectedDispatches[]`, then run artifact readiness.

## Dispatch

- Page runtime guide: `restore-1to1-page-runtime.md`.
- Dispatch contract: `dispatch-contract.md`.
- Packet must include reference capture evidence, at least 8 visual checkpoints, at least 5 high-priority source facts, and source coverage.

## Summary Writes

- Required fields are defined in `orchestration-summary-fields.md`.

## Delivery Quality Gate

- For restore_1to1: skip `validate-design-workspace.mjs`. Run `validate-finish-readiness.mjs --check=all --final-response-file=<draft.md>` directly.
- Do NOT write `restoreEvidenceReview`, `visualDiffReview`, or `sourceFactCoverageMap` — these are deprecated.

## Completion Evidence

- Completion must include source type, checkpoint count, validation result, and page node ids.

## Hard Rules (Restore 1:1)

- Validation loop: maximum 2 rounds. If round 2 fails, deliver with current state.
- Single-screen pages: one apply_patch for complete HTML output.
- Dispatch data: use `dispatch-packet-{nodeId}.json` file, not inline Task text.
- Visual Spec: must include structured `=== VISUAL SPEC ===` block with numeric values.
- Screenshot: must pass reference image path to Sub-Agent.
- Measured facts: high-priority facts must include numeric values with `precision` field.
- Post-dispatch: run `record-dispatch-completion.mjs` then `validate-finish-readiness.mjs`. No other scripts.
