---
lane: graphic_layout_static
contract: dispatch
---

# Graphic Layout Dispatch Contract

Required fields: `graphicStrategyGate=layout-static`, `layoutStaticRequired=true`, `textCriticality`, `copyDensity`, page layout plan, and delivery proof requirements.

The dispatch must explicitly forbid image-only delivery as the final primary artifact.

When `layoutStaticRequired=true`, write `project.deliverableCompletenessChecklist` before page dispatch:

```json
{
  "requiredPagesOrAssets": ["cover", "toc"],
  "requiredCopyBlocks": [
    {
      "label": "main title",
      "text": "年度资金使用分析",
      "htmlSrc": "pages/cover.html",
      "selector": "#cover-main-title",
      "role": "primary"
    }
  ],
  "requiredInfoTypes": ["price | date | venue | table | chart | legal-copy | source-image-caption"],
  "hierarchyContract": {
    "primaryCount": 1,
    "secondaryRequired": true,
    "minReadableFontPx": 24,
    "mustFitViewport": true
  },
  "expectedPageCount": 2,
  "actualPageCount": 2,
  "missingRequiredItems": [],
  "sourceMaterialCoverage": "complete | partial",
  "blocking": false
}
```

Final validation fails when `missingRequiredItems` is non-empty, `blocking=true`, `actualPageCount < expectedPageCount`, a required copy block lacks `htmlSrc` / `selector`, or a required copy selector is missing/hidden in the delivered HTML.

`sourceMaterialCoverage` must be `complete` for text-critical deliverables unless the packet records a user-approved reduction. Do not substitute a generated bitmap or screenshot as the primary artifact when `layoutStaticRequired=true`.

The page completion JSON must echo the checklist result and include `copyBlockEvidence[]` for every required copy block: `{label, selector, text, role, visible}`. Do not bury missing text, dates, prices, tables, or required sections in natural language.
