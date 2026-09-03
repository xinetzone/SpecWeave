# Restore Completion Contract

Restore quality is established during generation from the reference image, structured Visual Spec, measured facts, and visual checkpoints. Post-dispatch flow records only legal completion data and artifact readiness.

## Compact Completion JSON

The Sub-Agent returns:

```json
{
  "nodeId": "page-index",
  "page": "business page title",
  "htmlSrc": "pages/index.html",
  "changedFiles": ["pages/index.html"],
  "qualityGate": "passed",
  "toolCallLedger": {
    "source": "main-agent-runtime-trace",
    "todoWriteCalls": 0,
    "previewCalls": 0,
    "validationScriptCalls": 0,
    "helperScriptWrites": 0
  },
  "blockedReason": null
}
```

`toolCallLedger` is populated from the Main Agent's runtime trace before it is passed to `record-dispatch-completion.mjs`; the Sub-Agent must not fabricate a trace digest.

`qualityGate: "failed"` requires a short `blockedReason`. `qualityGate: "passed"` requires legal `changedFiles[]`, implemented high-priority checkpoints, required region coverage, and no prohibited tool calls.

## Persisted Fields

- `project.expectedDispatches[]`: written only by `record-dispatch-completion.mjs`.
- `project.measuredSourceFacts`: written before dispatch.
- `project.restoreVisualCheckpoints`: written before dispatch.

## Deprecated Fields

Do not write `project.restoreEvidenceReview`, `project.visualDiffReview`, `pages[].restoreEvidence`, or `project.sourceFactCoverageMap`. Do not run `validate-design-workspace.mjs` for restore finalization.
