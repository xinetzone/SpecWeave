# Shared Page Rendering Kernel

This is the declared shared kernel for Page Sub-Agents when a selected lane needs the full common HTML rendering discipline.

It contains only rules that are true for every Page Sub-Agent lane. Lane-specific rules live in lane-owned runtime guides and dispatch contracts.

## Scope

Use this kernel only when the selected `INTENT_WORKFLOW.md` declares it. Free fast, restore, and Library-bound lanes may use their lane-owned runtime guides without loading this file.

## Universal Inputs

A page packet provides:

- `nodeId`
- `htmlSrc`
- `title`
- `deviceType`
- `viewportMode`
- `cssPath`
- `brandPrefix`
- `fillHtmlHeadCommand` when the page needs a generated head
- `assets`
- `domIdsRequired`
- `supplementaryReads`

Lane-owned contracts add their own fields.

## Universal Rules

- Generate or patch only assigned HTML/page files.
- Do not write `.design`.
- Do not run validation scripts.
- Do not create helper scripts.
- Do not start preview servers or browser sessions.
- Do not generate images.
- Do not dispatch child agents.
- Return completion JSON as the only status channel.
- Preserve existing `data-dom-id` attributes unless the packet explicitly asks for a new control.
- Use provided assets only; report missing assets instead of inventing file paths.

## Head Handling

- Use `apply-html-head-contract.mjs` only through the exact `fillHtmlHeadCommand` provided by Main Agent.
- Do not rewrite `<head>` manually.
- Derived/copy pages must follow their lane runtime guide and may skip head generation when inheriting an existing head.
- If head generation fails, return `qualityGate: "blocked"` with the command error.

## HTML Quality Baseline

- Use semantic HTML and accessible controls.
- Avoid horizontal overflow.
- Use responsive grid/flex/stack layout for primary structure.
- Avoid absolute positioning for normal content layout.
- Keep text readable, wrapped, and aligned.
- Use CSS variables or approved token references for color, surface, border, radius, and shadow.
- Complete all visible content; no TODO, placeholder, or truncated sections.
- For layout-risk pages, primary layout must survive without Tailwind browser compilation. For shell, frame, first-screen regions, card/list/table grids, and bottom navigation, write normal CSS classes in a responsive-safe static `<style id="critical-layout">` block or equivalent page-local CSS. Tailwind utilities may enhance spacing and responsive variants, but the page must not collapse to a blank or single-column bare document if `<style type="text/tailwindcss">` is delayed or fails.
- Before returning `qualityGate: "passed"` for layout-risk pages, do a production visual stability self-check: no first-screen overlap, no text compressed into character-by-character columns, no zero-gap control clusters, no content hidden by fixed/sticky chrome, no main layout dependent on `position:absolute`, no blank primary content region, and no fixed viewport/frame rule that blocks responsive behavior.

## Completion JSON Base

Every lane completion JSON must include at least:

```json
{
  "nodeId": "page-index",
  "page": "pages/index.html",
  "qualityGate": "passed|failed|blocked",
  "domIds": [],
  "headInfrastructureStatus": {},
  "toolDisciplineEvidence": {
    "todoWriteUsed": false,
    "previewStarted": false,
    "validationScriptsRunBySubAgent": false,
    "helperScriptsCreated": false,
    "imagesGeneratedBySubAgent": false
  },
  "toolCallLedger": {
    "todoWriteCalls": 0,
    "previewCalls": 0,
    "validationScriptCalls": 0,
    "helperScriptWrites": 0
  },
  "blockedReason": null
}
```

Lane-owned runtime guides may require additional evidence fields.

Layout-risk page packets also include:

```json
{
  "staticRenderingEvidence": {
    "criticalLayoutCssPresent": true,
    "runtimeOnlyTailwindDependency": false,
    "layoutCriticalSelectors": []
  },
  "viewportIntegrityEvidence": {
    "targetFrame": "desktop|mobile|tablet|freeSize",
    "firstScreenRegionsVisible": [],
    "horizontalOverflowRisk": "none|known-risk|blocked",
    "overlapRisk": "none|known-risk|blocked"
  }
}
```

## Failure Fallback

If a Sub-Agent returns blocked/failed or invalid completion JSON, Main Agent decides whether to retry, reduce scope, or perform in-context generation according to the selected workflow and `intent-workflows/intent-project-mutation/main-agent-repair-workflow.md`. The Sub-Agent must not self-execute repair routing.
