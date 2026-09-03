# Free Exploration Page Runtime

Use only for `FreePagePacket` with `resolvedLane: "free_exploration"`, no active Design Library, and no high-fidelity restore intent.

If the packet contains Library identity, `componentPlan`, `actualTokenNameReference`, restore evidence, or `replicationMode: "high-fidelity"`, stop and return `qualityGate: "blocked"` with the mismatch.

## Inputs

Main Agent provides a compact packet:

```json
{
  "nodeId": "page-index",
  "htmlSrc": "pages/index.html",
  "title": "Home",
  "writeMode": "SkeletonMainAtomic|SectionPlanThenWrite|SectionedPatch|DerivedCopyMutableOnly",
  "viewportMode": "document-scroll|app-shell",
  "deviceType": "web|mobile|tablet",
  "cssPath": "colors_and_type.css",
  "brandPrefix": "brand",
  "fillHtmlHeadCommand": "node {SKILL_DIR}/shared-runtime/deterministic-tooling/apply-html-head-contract.mjs ...",
  "cssPreflightStatus": "passed",
  "creativeRecipe": {},
  "sections": [],
  "assets": [],
  "domIdsRequired": [],
  "stateGroupId": null,
  "stateRole": "base|derived|null",
  "derivedFromHtmlSrc": null,
  "mutableRegions": [],
  "immutableShellRegions": [],
  "defaultDeliverableVisibility": {
    "applies": false,
    "requiredVisibleRegions": [],
    "hiddenAllowed": []
  },
  "supplementaryReads": [],
  "completionTemplate": {
    "nodeId": "{{nodeId}}",
    "page": "{{htmlSrc}}",
    "title": "",
    "domIds": [],
    "qualityGate": "passed",
    "designIntentEvidence": { "visualNorthStarApplied": "", "compositionPatternUsed": "", "continuityAnchorsApplied": "", "antiSlopCheck": "" },
    "interactionStates": [],
    "motionEvidence": {},
    "visualStructureEvidence": { "primitiveTokenEvidence": "", "layoutGeometryEvidence": "" },
    "alignmentEvidence": "",
    "headingCtaEvidence": "",
    "defaultDeliverableVisibilityEvidence": { "allRequiredRegionsVisible": true, "hiddenRequiredRegions": [] },
    "headManagementEvidence": { "mode": "", "command": "", "usedReplaceHead": false },
    "iconPolicyEvidence": { "emojiUsedAsIcon": false, "explicitUserRequestedEmojiIcons": false },
    "animationLibrariesUsed": [],
    "blockedReason": null
  }
}
```

## Hard Rules

- Generate or patch only the assigned HTML page.
- Do not write `.design`.
- Do not run project validation scripts.
- Do not create helper scripts, start preview servers, call TodoWrite, dispatch child agents, or generate images.
- Use only provided assets.
- No placeholders, TODO sections, or truncated page content.
- Use the exact `fillHtmlHeadCommand` from the packet; do not invent arguments.
- If CSS preflight is not passed for an ordinary/base page, stop as blocked.
- Do not read restore, Library-bound, graphic, complex, mutation, or shared-kernel runbooks unless they appear in `supplementaryReads[]`.

## Head And Write Mode

- `SkeletonMainAtomic`: run the provided head command, then replace `<main>` once.
- `SectionPlanThenWrite`: plan sections briefly, run the head command, then replace `<main>` once.
- `SectionedPatch`: patch at most 3 targeted sections.
- `DerivedCopyMutableOnly`: copy `derivedFromHtmlSrc` first, do not run the head command, then edit only `mutableRegions`.
- Never rewrite `<head>` manually.
- Preserve `<style id="semantic-token-fallback">` and theme/head infrastructure created by `apply-html-head-contract.mjs`.

## Viewport Rules

- `document-scroll` is the default for mobile/H5/page boards; use natural flow and prevent horizontal overflow.
- `app-shell` is only for fixed workbenches, dashboards, admin consoles, or explicit fixed-screen UIs.
- App shell roots use `data-viewport-mode="app-shell"` and a scroll region with `data-scroll-region="primary"`.
- If the packet includes a mobile navigation contract, preserve item order, labels, geometry, `data-nav-key`, and canonical nav structure exactly; only active state may change.

## Visual Rules

- Follow the packet `creativeRecipe`.
- Make the page complete, coherent, content-rich enough for the task, and responsive.
- For layout-risk pages (mobile, app-shell, dense list/table/calendar/product-card layouts, or fixed chrome), add responsive-safe static `critical-layout` CSS for the root frame and first-screen primary structure; Tailwind runtime classes alone are not enough for shell geometry, mobile frames, lists/tables/cards, or bottom chrome.
- For layout-risk pages, verify viewport integrity before completion: visible first-screen regions, no horizontal overflow, no chrome/content overlap, no blank primary content, no character-by-character compression, and no fixed viewport/frame rule that breaks responsive behavior.
- For layout-risk pages, final JSON must include `staticRenderingEvidence` and `viewportIntegrityEvidence`.
- Use real icons from provided assets, Lucide, Design Library SVGs, or inline SVG. Do not use emoji as functional UI icons unless the user explicitly requested emoji icons.
- Use token or semantic-variable sources for visible dividers, borders, strokes, shadows, and surfaces.
- Avoid absolute positioning for primary layout; prefer grid, flex, or stack.
- If `defaultDeliverableVisibility.applies=true`, every listed `requiredVisibleRegions[]` selector must exist and be visible in the default HTML. Core user requirements must not be hidden behind JS-only flows, `display:none`, `hidden`, `visibility:hidden`, `opacity-0`, or `aria-hidden=true`.

## Completion JSON

When `completionTemplate` is present in the packet, use it as the base structure for the completion report. Fill in all placeholder values and return the completed JSON. Do not memorize field names from other sources — the template is authoritative.

Return only:

```json
{
  "nodeId": "page-index",
  "page": "pages/index.html",
  "qualityGate": "passed|failed|blocked",
  "cssPreflightStatus": "passed|failed|not-needed",
  "htmlWriteMode": "SkeletonMainAtomic|SectionPlanThenWrite|SectionedPatch|DerivedCopyMutableOnly",
  "stateGroupId": null,
  "stateRole": "base|derived|null",
  "derivedBaseCopied": true,
  "sharedShellPreserved": [],
  "domIds": [],
  "headInfrastructureStatus": {
    "themeVars": "present|missing|inherited",
    "semanticTokenFallback": "present|missing|inherited",
    "themeInline": "present|missing|inherited",
    "tailwindCdn": "present|missing|inherited",
    "lucideCdn": "present|missing|inherited",
    "htmlClass": "light|dark|missing|inherited",
    "needsMainAgentReplaceHead": false
  },
  "toolDisciplineEvidence": {
    "todoWriteUsed": false,
    "previewStarted": false,
    "validationScriptsRunBySubAgent": false,
    "helperScriptsCreated": false,
    "imagesGeneratedBySubAgent": false
  },
  "iconPolicyEvidence": {
    "emojiUsedAsIcon": false,
    "explicitUserRequestedEmojiIcons": false,
    "iconSources": []
  },
  "visualStructureEvidence": {
    "primitiveTokenEvidence": [],
    "layoutGeometryEvidence": []
  },
  "headCommandEvidence": {
    "headCommandUsed": "exact command or null for derived pages",
    "matchesPacketCommand": true,
    "usedReplaceHead": false
  },
  "styleRecipeApplied": true,
  "defaultDeliverableVisibilityEvidence": {
    "allRequiredRegionsVisible": true,
    "hiddenRequiredRegions": []
  },
  "sections": [],
  "blockedReason": null
}
```

`qualityGate: "passed"` requires no tool discipline violations, no forbidden emoji-icon use, non-empty primitive/layout evidence, production stability evidence passing when layout-risk applies (`criticalLayoutCssPresent=true`, `runtimeOnlyTailwindDependency=false`, visible first-screen regions, overflow/overlap risk `"none"`), matching head command evidence, and all required default regions visible.
