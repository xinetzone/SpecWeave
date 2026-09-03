---
lane: graphic_layout_static
runtime: page-sub-agent
---

# Graphic Layout Page Runtime

Use this guide for text-critical static graphic deliverables implemented as editable HTML layouts.

The final primary artifact must remain a static layout page. Do not substitute image-only delivery when `layoutStaticRequired=true`.

## Required Inputs

The packet must include:

- `graphicStrategyGate="layout-static"`
- `layoutStaticRequired=true`
- `textCriticality="medium" | "high"`
- `requiredCopyBlocks[]` with `{ label, text, htmlSrc, selector, role }`
- `hierarchyContract` when textCriticality is high

If `requiredCopyBlocks[]` is missing or contains only string labels, return `qualityGate: "failed"` and do not generate a weak layout.

## Rendering Rules

- Every required copy block must appear as editable DOM text, not as bitmap text.
- `role="primary"` copy must be one of the page's primary visual anchors. It cannot be placed in a corner, decorative caption, hidden panel, or low-contrast background.
- Required copy must be visible in the default delivered HTML. Do not use `display:none`, `hidden`, `visibility:hidden`, `opacity-0`, or `aria-hidden=true`.
- Keep text on top of stable surfaces. Do not place required copy on noisy generated imagery, decorative screenshots, or low-contrast backgrounds.
- Prefer semantic IDs from the packet selectors. If you must adjust a selector, report the new selector in completion JSON and keep it stable.

## Completion JSON Additions

Return `copyBlockEvidence[]`:

```json
{
  "copyBlockEvidence": [
    {
      "label": "main title",
      "selector": "#cover-main-title",
      "text": "年度资金使用分析",
      "role": "primary",
      "visible": true
    }
  ]
}
```

`qualityGate: "passed"` is invalid when any required copy block is missing, hidden, unreadable, or not represented as editable DOM text.
