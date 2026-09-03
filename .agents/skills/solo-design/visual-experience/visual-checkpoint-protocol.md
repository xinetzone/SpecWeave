---
contract: visual-checkpoint-protocol
---

# Visual Checkpoint Protocol

Use this protocol when the selected lane creates a visually critical editable page or layout-static graphic. It turns visual intent into bounded checkpoints before generation, without adding open-ended exploration or model-specific behavior.

## When This Applies

Apply this protocol when any of the following is true:

- `resolvedLane` is `graphic_layout_static`.
- The user asks for poster, PPT cover, one-pager, manual redesign, KV, marketing page, or other composition-heavy deliverables that remain editable HTML.
- The page depends on a clear visual anchor, information hierarchy, composition structure, or implementation strategy to satisfy the request.

Do not use this protocol to expand scope, add pages, or start subjective polishing. It defines the minimum visual decisions required before dispatch.

## Required Summary Field

Before dispatch, write `runtime-orchestration-summary.json.project.visualQualityCheckpoints[]`.

Minimum checkpoint set:

```json
[
  {
    "checkpointId": "vq-anchor",
    "dimension": "visual-anchor",
    "expected": "dominant visual or structural anchor, or explicit reason for text-led composition",
    "evidenceTarget": "pages/index.html#primary-region"
  },
  {
    "checkpointId": "vq-hierarchy",
    "dimension": "information-hierarchy",
    "expected": "title, body, facts, and actions have clear priority",
    "evidenceTarget": "pages/index.html#content"
  },
  {
    "checkpointId": "vq-structure",
    "dimension": "composition-structure",
    "expected": "surface composition uses deliberate balance, density, and whitespace",
    "evidenceTarget": "pages/index.html#layout"
  },
  {
    "checkpointId": "vq-implementation",
    "dimension": "implementation-strategy",
    "expected": "asset, CSS, component, or text-led implementation strategy is declared",
    "evidenceTarget": "pages/index.html#implementation"
  }
]
```

## Repair Rule

When validation or review reports a visual checkpoint issue:

1. Identify exactly one failed checkpoint.
2. Repair only the HTML/CSS region named by `evidenceTarget`.
3. Do not redesign unrelated content, change page count, or re-open style discovery.
4. If the checkpoint cannot be satisfied without changing user requirements or source authority, stop and report the blocking reason.

## Source Authority Relationship

For restore workflows, `restoreVisualCheckpoints[]` remains the stricter contract. This protocol must not override restore source facts, visual authority, or allowed deviations.

For non-restore layout-static work, this protocol provides the visual contract that restore workflows already have: visual anchor, information hierarchy, composition structure, and implementation strategy are explicit before generation.
