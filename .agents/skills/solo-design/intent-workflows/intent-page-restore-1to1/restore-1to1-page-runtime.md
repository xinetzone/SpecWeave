# Page Generation — Restore 1:1 Card

Use this card only for a `RestorePagePacket` from `intent-workflows/intent-page-restore-1to1/start-restore-1to1-project.md`.

The source reference is the design authority. Do not apply creative reinterpretation, generic aesthetics, or Library/free-explore shortcuts unless explicitly present in the packet.

## Phase 0 — Required Constraints

Read only the implementation constraints needed for this page:

- `shared-runtime/agent-dispatch-runtime/sub-agent-runtime-boundaries.md`
- `shared-runtime/html-rendering-primitives/shared-html-rendering-primitives.md`
- `shared-runtime/html-rendering-primitives/mobile-html-rendering-primitives.md` when the target is mobile
- `shared-runtime/html-rendering-primitives/web-html-rendering-primitives.md` when the target is desktop/tablet
- `intent-workflows/intent-page-restore-1to1/restore-evidence-contract.md`

Do not read `visual-experience/visual-experience-guidelines.md`. Consume the provided `restoreCompactPacket`; `sourceIdentity`, `pageStateLock`, `visualSpecExcerpt`, `measuredSourceFacts`, `restoreVisualCheckpoints`, and `sourceRegionCoverage` are the only visual authority for restore. Do not read full `runtime-orchestration-summary.json`.

## Phase 1 — Packet Gate

### Phase 1 Steps

1. **Read Reference Image**: If `visualReferenceImage` path is provided in the task description, Read the image file first to establish visual calibration context. Use it only for calibration — never embed it in output HTML.

2. **Read Dispatch Packet**: Read `dispatch-packet-{nodeId}.json` from the project directory. This file is the authoritative data source for all packet fields. Do not rely solely on the Task description text.

3. **Parse Visual Spec**: Extract the `=== VISUAL SPEC ===` block from the task description. Parse each section ([LAYOUT], [SPACING], [TYPOGRAPHY], [COLORS], [SHADOWS & DEPTH], [RADII]) into working values.

4. **Verify Required Fields**: Confirm the packet file contains: `nodeId`, `htmlSrc`, `cssPath`, `htmlFilePath`, `brandPrefix`, `sourceType`, `measuredSourceFacts` (≥8), `restoreVisualCheckpoints` (≥8), `sourceRegionCoverage`, `visualSpecExcerpt`, `fillHtmlHeadCommand`. If any required field is missing, report the gap and halt.

Before writing HTML, verify the packet contains:

- `nodeId`
- `htmlSrc`
- `cssPath`
- `htmlFilePath`
- `brandPrefix`
- `sourceType`
- `sourceIdentity`
- `pageStateLock`
- `sourceDocumentProfile`
- `referenceCaptureEvidence`
- `restoreContractStatus.success === true`
- `restoreCompactPacket`
- `measuredSourceFacts` with at least 8 rows
- `restoreVisualCheckpoints` with at least 8 rows
- `restorationContractLite`
- `visualSpecExcerpt`
- `sourceRegionCoverage`
- `fillHtmlHeadCommand`

If any required field is missing, return:

```json
{
  "qualityGate": "failed",
  "blockedReason": "missing RestorePagePacket fields: <field-list>"
}
```

Do not infer missing visual context from generic page patterns.

## Phase 2 — Implementation Rules

- Rebuild the source as editable HTML/CSS components.
- Use `measuredSourceFacts` as the low-level geometry, color, density, and proportion authority.
- Preserve all high-priority `restoreVisualCheckpoints`.
- Implement every high/medium `sourceRegionCoverage` row unless it is explicitly `intentionally-deviated`.
- Preserve visible text from `contentToPreserve`; do not fabricate alternative copy.
- Match source layout grid, density, color rhythm, typography hierarchy, component proportions, and app/site chrome.
- Preserve `sourceIdentity.businessType`, `sourceIdentity.coreObjects[]`, and `pageStateLock.currentState`; do not substitute a different app/site/page state.
- Do not use the source screenshot/reference image as the dominant page body.
- Source images are allowed only as small media/product/content regions when the original UI genuinely contains images.
- Do not write `.design`.
- Do not create helper scripts.
- Do not run project validation scripts.
- Do not start preview or browser sessions.
- Do not call TodoWrite.

### Implementation Precision Requirements

- Use exact numeric values from the Visual Spec `[SPACING]`, `[TYPOGRAPHY]`, `[COLORS]`, `[SHADOWS & DEPTH]`, and `[RADII]` sections.
- Use `measuredSourceFacts` measurements as fallback when Visual Spec lacks a specific value.
- FORBIDDEN: Rounding values to "convenient" numbers (e.g., 14px → 16px).
- FORBIDDEN: Replacing sampled colors with "safe" generic grays.
- FORBIDDEN: Omitting shadows or border-radius present in the source.
- FORBIDDEN: Redesigning icons or logos. Reproduce the exact shape, color, and structure visible in the source. Never substitute a "similar concept" graphic.
- Cross-reference the reference image when making proportion or spacing decisions.

### Output Strategy

- If `sourceDocumentProfile.documentLengthClass === "single-screen"`: Output the COMPLETE page HTML in a SINGLE `apply_patch` (including `<html>`, `<head>`, `<body>`, all `<style>` blocks). Do not split into multiple patches.
- If `documentLengthClass === "medium" | "long"`: Split into at most 3 `apply_patch` operations, each covering a complete `regionGroup` from top to bottom. Each patch must produce valid partial HTML that can be concatenated.

## Phase 3 — Head Command

Use the exact `fillHtmlHeadCommand` from the packet after writing the page skeleton/content.

For ordinary/base restore pages:

- `headCommandEvidence.headCommandUsed` must match the packet command.
- `headCommandEvidence.usedReplaceHead` must be `false` unless the packet explicitly requires full HTML replacement.

Do not run extra commands only to populate evidence.

## Completion Contract

Return the compact JSON defined in `restore-evidence-contract.md`. Bare paths, Markdown-only summaries, and deprecated restore evidence maps are invalid.

`qualityGate: "passed"` requires:

- Every high-priority checkpoint is implemented, or has a packet-approved deviation.
- Every required high/medium source region is implemented or intentionally deviated.
- The reference image was not embedded as the page body.
- `changedFiles[]` stays within `allowedWritePaths[]`.
- The runtime-trace `toolCallLedger` reports zero TodoWrite, preview, validation-script, and helper-script calls.

If any requirement fails, return `qualityGate: "failed"` with a compact `blockedReason`. The Main Agent records completion with `record-dispatch-completion.mjs`; neither agent writes deprecated evidence fields.
