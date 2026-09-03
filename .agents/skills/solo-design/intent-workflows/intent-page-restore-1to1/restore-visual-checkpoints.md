---
lane: restore_1to1
contract: visual-checkpoints
---

# Restore Visual Checkpoints

Checkpoint rows must cover layout geometry, spacing, typography, colors, icon/image treatment, navigation/header/footer, below-fold content, and interaction states when present.

Each checkpoint records `id`, `priority`, `dimension`, `sourceRegion`, `sourceFact`, `expected`, `allowedDeviationRef`, `implementationEvidence`, and `status`.

High-priority checkpoints must be grounded in `project.measuredSourceFacts[]`. Each high-priority checkpoint must either be listed by at least one measured fact's `usedByCheckpointIds[]`, or explicitly include a compact `measuredSourceFactIds[]` list that references existing measured fact ids.

New restore outputs must use the existing `dimension` field. Required dimensions are:

- `layout`
- `color-rhythm`
- `typography`
- `component-proportion`
- `density`
- `fine-detail`

`component-proportion` must appear at least twice, or represent at least 25% of all checkpoints.

High-priority checkpoint facts must be executable visual facts, not vague taste language.

High-priority checkpoints guide the Sub-Agent's visual generation but do NOT require post-dispatch `visualDiffReview` mapping. The Sub-Agent validates checkpoints by direct visual comparison with the source screenshot.

High-priority checkpoints must cover at minimum:

1. Overall page geometry and viewport density.
2. Header / navigation / hero structure when present.
3. Primary content grouping and card/table/list proportions.
4. Typography scale and major text alignment.
5. Color/surface/icon/image treatment.

The goal is high-fidelity similarity through compact facts. Do not introduce a pixel-level validator; this contract feeds the Sub-Agent's visual reference comparison during generation.
