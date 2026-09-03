---
contract: generalized-flow-control-fields
---

# Generalized Flow Control Fields

This file defines the model-agnostic flow-control fields introduced in skill version `2026.07.11.0`. These fields describe correct execution boundaries; they must not encode model-specific behavior.

## Context Preflight

Before any Page Sub-Agent dispatch, record one `project.contextRequirementsLoaded[]` row for every non-optional file listed in the selected lane's `INTENT_WORKFLOW.md` Context Requirements section.

Minimum row:

```json
{
  "path": "shared-runtime/runtime-boundaries/lane-runtime-contracts.md",
  "readStatus": "loaded",
  "bodyRead": true,
  "recordedAt": "ISO-8601 timestamp"
}
```

`build-page-dispatch-manifest.mjs` refuses to write `dispatchPreflightManifest[]` when required context files are missing or only named without body-read evidence.

## Source Authority Lock

Reference-driven workflows separate visual authority from supplemental content before dispatch:

```json
{
  "sourceAuthorityLock": {
    "visualAuthority": "user-screenshot | provided-image | full-page-screenshot",
    "contentSupplement": "url | browser-snapshot | extracted-copy | none",
    "browserObservationRole": "targeted-verification-only",
    "mayOverrideVisualAuthority": false,
    "lockedBeforeDispatch": true
  }
}
```

Browser or URL observations may fill copy, navigation labels, and section inventory, but must not replace the chosen visual authority for layout, color rhythm, density, component proportion, or fine detail.

## Visual Quality Checkpoints

Layout-static and visually critical page workflows write `project.visualQualityCheckpoints[]` before dispatch.

Required dimensions for layout-static work:

```json
[
  {"checkpointId": "vq-anchor", "dimension": "visual-anchor", "expected": "dominant visual or structural anchor", "evidenceTarget": "pages/index.html#primary-region"},
  {"checkpointId": "vq-hierarchy", "dimension": "information-hierarchy", "expected": "clear priority among title, facts, body, and actions", "evidenceTarget": "pages/index.html#content"},
  {"checkpointId": "vq-structure", "dimension": "composition-structure", "expected": "balanced composition, density, and whitespace for the target surface", "evidenceTarget": "pages/index.html#layout"},
  {"checkpointId": "vq-implementation", "dimension": "implementation-strategy", "expected": "appropriate asset, CSS, component, or text-led implementation strategy", "evidenceTarget": "pages/index.html#implementation"}
]
```

When a checkpoint fails, repair only the corresponding checkpoint. Do not use this protocol to broaden page count, change business requirements, or start subjective polishing loops.

## Low-Value Call Watchdog

Page-dispatch workflows write:

```json
{
  "lowValueCallWatchdog": {
    "applies": true,
    "noProgressSignals": ["no_tool_call", "no_artifact_diff", "no_structured_decision"],
    "noProgressNextAction": "enter_readiness_or_blocked_summary",
    "recordedAt": "ISO-8601 timestamp"
  }
}
```

This does not expose resource targets to the Agent. It only defines what to do when a long reasoning span produces no tool call, no artifact diff, and no structured decision: enter readiness if the artifact is complete, or produce a minimal blocked summary.
