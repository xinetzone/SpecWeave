# Create Project — Restore 1:1 Path

Use this workflow only when `intentProfile.caseFamily === "restore_1to1"` or the user explicitly asks to restore / replicate / reproduce a UI, page, screenshot, or website 1:1.

This is the single restore path for `image`, `url`, and `image+url` sources. Do not split image restore and URL restore into separate workflows. The downstream restore pipeline is shared; only source capture differs.

## Non-Negotiable Path Isolation

- Read this workflow as the only create-project execution workflow after route lock.
- Do not continue into the generic create-project Step 0.5-5 flow.
- Do not read non-restore workflow files after this workflow is selected.
- Do not route UI/page/site restoration through image-only graphic delivery. Restore output must be editable HTML/CSS pages on the canvas.
- Record the route in `runtime-orchestration-summary.json.project.intentProfile.routingReason`.

## Main Agent Tool Restrictions (restore_1to1)

When `sourceType` is `image` or `image+url`:
- **FORBIDDEN**: Opening the source screenshot in a browser to "analyze" or "zoom in". You are a multimodal model — read the image file directly with the Read tool. Browser navigation adds 30-60 seconds of latency for zero additional information.
- **FORBIDDEN**: Creating Python/PIL/Node.js scripts to extract pixel colors, measure dimensions, or crop regions from the screenshot. Use your visual judgment directly.
- **FORBIDDEN**: Using WebFetch or browser tools to reinterpret the source image.
- **ALLOWED**: Read tool to view the image file directly (your vision capability sees full resolution).
- **ALLOWED**: Browser only when `sourceType` includes `url` AND only for extracting copy/text content, navigation labels, or section inventory — never for visual measurement.

## Restore Source Adapter

| sourceType | Visual authority | Required source work | Forbidden |
| --- | --- | --- | --- |
| `image` | User-provided screenshot/image | Convert the image into `restoreVisualCheckpoints`, `sourceRegionCoverage`, `visualSpecExcerpt`, and `Restoration Contract Lite` | Browser capture, WebFetch reinterpretation, generic app/page redesign, image-only graphic output |
| `url` | Browser full-page screenshot | Capture full-page screenshot first; use browser snapshot and WebFetch only to fill copy, section inventory, and navigation | Text-only WebFetch restore, same-domain redesign, hero-only restore |
| `image+url` | User-provided screenshot/image | Use screenshot as visual authority; use URL only for copy, navigation, and section inventory gaps | Letting the live URL override screenshot layout, color, density, or component proportions |

If both a user-provided image/screenshot and a URL are present, `sourceType` must be `image+url`. Do not downgrade to `image` or `url`. For `image+url`, `referenceCaptureEvidence.visualAuthority` must keep the provided image/screenshot primary; URL evidence is secondary and may only fill copy, navigation labels, and section inventory.

Before dispatch, write `runtime-orchestration-summary.json.project.sourceAuthorityLock`:

```json
{
  "visualAuthority": "user-screenshot | provided-image | full-page-screenshot",
  "contentSupplement": "url | browser-snapshot | extracted-copy | none",
  "browserObservationRole": "targeted-verification-only",
  "mayOverrideVisualAuthority": false,
  "lockedBeforeDispatch": true
}
```

After this lock is written, no later URL, browser, or WebFetch observation may override layout, color rhythm, density, typography hierarchy, component proportions, or fine detail from the visual authority.

Before measuring geometry or dispatching any page, also write `runtime-orchestration-summary.json.project.sourceIdentity` and `runtime-orchestration-summary.json.project.pageStateLock`. These fields lock what the source page is and which state is visible; they are higher priority than low-level geometry measurements.

```json
{
  "sourceIdentity": {
    "businessType": "mobile-todo-app | ecommerce-admin-product-editor | saas-landing-page",
    "coreObjects": ["task-list", "device-shell", "primary-cta"],
    "deviceType": "mobile | desktop | tablet",
    "pageTitle": "short source page identity"
  },
  "pageStateLock": {
    "currentState": "exact visible source state, e.g. product edit form with media card and right status panel",
    "forbiddenDeviations": ["do not change product editor into product list", "do not change dark landing page into light redesign"]
  }
}
```

## Required Restore Sequence

| Step | Input | Output | Gate |
| --- | --- | --- | --- |
| 1. Route Lock | User request + `intentProfile` | `caseFamily: "restore_1to1"`, `sourceType`, `routingReason` | Stop if route is not restore |
| 2. Source Authority | Image / URL / image+URL evidence | `referenceCaptureEvidence` + `sourceAuthorityLock` | Image-only does not browse; URL-only requires full-page screenshot evidence; image+url requires both provided image and URL evidence; lock must forbid visual override |
| 3. Source Identity & Page State Lock | Visual authority | `sourceIdentity` + `pageStateLock` | Must exist before measured facts; prevents business/page-state drift |
| 4. Source Document Profile | Visual authority | `sourceDocumentProfile.requiredRegionGroups[]` | URL long pages require first/middle/footer groups; device screenshots require outer/device/inner/primary groups |
| 5. Measured Facts | Visual authority + state lock | `measuredSourceFacts` | At least 8 measured facts, at least 5 high priority with `measurementBasis`, required categories covered |
| 6. Visual Contract | Visual authority + measured facts | `restoreVisualCheckpoints` and `visualSpecExcerpt` | At least 8 checkpoints, at least 5 high priority, linked to measured facts |
| 7. Region Coverage | Source regions | `sourceRegionCoverage` | No high/medium unmapped rows; required `regionGroup` coverage is complete |
| 8. Project Init | Page plan + CSS token plan | `.design` skeleton and `colors_and_type.css` | Main Agent owns `.design`; Sub-Agents never write it |
| 9. Restore Contract Preflight | Summary + CSS | `restore-contract-report.json success=true` | Run `validate-restore-contract.mjs`; do not dispatch on fail |
| 10. Dispatch | `RestorePagePacket` file + screenshot path + Visual Spec | Task using `intent-workflows/intent-page-restore-1to1/restore-1to1-page-runtime.md` | Packet file written; screenshot accessible; Visual Spec structured; generic Task dispatch forbidden |
| 11. Post-Dispatch Finalization | Sub-Agent completion JSON | `expectedDispatches[]` recorded | Record completion → Artifact Readiness. No evidence write, no validate-design-workspace. |
| 12. Artifact Readiness | Validation + `.design` project + final draft | `validate-finish-readiness.mjs <designProjectPath> --check=all --final-response-file=<draft.md>` passes | Canvas registration, file references, repair ledger, and response text policy are ready |

## Summary Initialization Template

After Route Lock (Step 1), write the complete `runtime-orchestration-summary.json` skeleton in a **single Write** operation. This prevents preflight loops caused by missing fields.

**IMPORTANT:** This template contains placeholder values (e.g., `"<to-fill>"`, empty arrays `[]`). You MUST populate ALL placeholder fields through Steps 2-8 BEFORE running `validate-restore-contract.mjs`. The preflight script is Step 9 — never run it earlier. Specifically:
- `pages[]` must contain at least one page entry (filled in Step 8 after `.design` is created)
- `measuredSourceFacts[]` must contain ≥8 entries (filled in Step 5)
- `restoreVisualCheckpoints[]` must contain ≥8 entries (filled in Step 6)
- `sourceRegionCoverage[]` must be populated (filled in Step 7)
- `colors_and_type.css` must exist with semantic aliases before preflight (created in Step 8)

```json
{
  "skillProvenance": { "name": "solo-design", "version": "<current skill version from skill-release-manifest.json>" },
  "project": {
    "resolvedLane": "restore_1to1",
    "replicationMode": "high-fidelity",
    "brandPrefix": "<2-4 char prefix for CSS variables, e.g. td>",
    "selectedIntentWorkflowRead": true,
    "intentProfile": {
      "caseFamily": "restore_1to1",
      "sourceType": "<image|url|image+url>",
      "routingReason": "<why restore was selected>"
    },
    "deviceType": "<mobile|desktop|tablet>",
    "sourceType": "<image|url|image+url>",
    "sourceIdentity": {
      "businessType": "<to-fill>",
      "coreObjects": [],
      "deviceType": "<mobile|desktop|tablet>",
      "pageTitle": "<to-fill>"
    },
    "pageStateLock": {
      "currentState": "<to-fill>",
      "forbiddenDeviations": []
    },
    "sourceAuthorityLock": {
      "visualAuthority": "<user-screenshot|provided-image|full-page-screenshot>",
      "contentSupplement": "<url|browser-snapshot|none>",
      "browserObservationRole": "targeted-verification-only",
      "mayOverrideVisualAuthority": false,
      "lockedBeforeDispatch": true
    },
    "referenceCaptureEvidence": {},
    "sourceDocumentProfile": {
      "sourceType": "<image|url|image+url>",
      "documentLengthClass": "<short|medium|long>",
      "viewportScrollRatio": 1.0,
      "deviceFramePresent": false,
      "requiredRegionGroups": []
    },
    "measuredSourceFacts": [],
    "restoreVisualCheckpoints": [],
    "sourceRegionCoverage": [],
    "validationRunDiscipline": {
      "maxFullValidationRuns": 2,
      "softWarningsTriggerRepair": false,
      "blockingRepairMode": "targeted-once"
    },
    "lowValueCallWatchdog": {
      "applies": true,
      "noProgressNextAction": "enter_readiness_or_blocked_summary"
    },
    "contextRequirementsLoaded": [
      { "path": "intent-workflows/intent-page-restore-1to1/start-restore-1to1-project.md", "readStatus": "loaded" },
      { "path": "intent-workflows/intent-page-restore-1to1/dispatch-contract.md", "readStatus": "loaded" },
      { "path": "intent-workflows/intent-page-restore-1to1/restore-evidence-contract.md", "readStatus": "loaded" },
      { "path": "shared-runtime/agent-dispatch-runtime/lane-dispatch-index.md", "readStatus": "loaded" },
      { "path": "delivery-quality/page-rendering-quality-gate.md", "readStatus": "loaded" },
      { "path": "intent-workflows/intent-page-restore-1to1/restore-1to1-page-runtime.md", "readStatus": "loaded" }
    ],
    "contextReadScope": "restore_1to1_minimal"
  },
  "pages": [
    {
      "nodeId": "page-index",
      "htmlSrc": "pages/index.html",
      "title": "<page title>",
      "brandPrefix": "<same as project.brandPrefix>",
      "dispatchStatus": "pending"
    }
  ]
}
```

Write this skeleton in Step 1, then fill data progressively through Steps 2-8. Only run `validate-restore-contract.mjs` (Step 9) after ALL data fields are populated.

## .design File Template (Step 8)

Write the `.design` canvas entry file in a **single Write** operation during Step 8 (Project Init). Use this exact structure:

```json
{
  "data": [
    {
      "id": "page-index",
      "title": "<page title in user language>",
      "type": "page",
      "version": 1,
      "createdAt": <current timestamp ms>,
      "devMetadata": {
        "htmlSrc": "pages/index.html",
        "interactions": []
      },
      "canvasData": { "x": 0, "y": 0, "group": 0 }
    }
  ],
  "config": {
    "autoLayout": true,
    "deviceType": "<mobile|desktop|tablet>",
    "projectName": "<project display name in user language>"
  }
}
```

Critical rules:
- **Page node ID**: must be `page-{slug}` where slug = HTML filename without `.html` (e.g., `pages/index.html` → `page-index`)
- **Image node ID**: must be `image-NNN` format (e.g., `image-001`, `image-002`), monotonically incrementing. Never use semantic names like `img-source-screenshot`
- **Image node `canvasData`**: must NOT have `group` field — only `{ "x": 0, "y": 0 }`
- **Image node `devMetadata`**: must have `imageSrc` pointing to actual file (e.g., `"assets/hero-banner.png"`)
- **Source screenshot**: do NOT register the source screenshot (`source-screenshot.png`) as an image node in `.design`. It is a reference input, not a design asset
- **`config.deviceType`** must match `runtime-orchestration-summary.json.project.deviceType`

## Preflight Iteration Limit

`validate-restore-contract.mjs --mode=preflight` may be run at most **2 times**. If it fails on the second run, apply `--apply-safe-fixes` once and proceed to `build-page-dispatch-manifest.mjs`. Do not enter a third preflight cycle.

## Measured Source Facts

Before dispatch, write at least 8 low-level source facts into `runtime-orchestration-summary.json.project.measuredSourceFacts`.

Each measured fact must use this shape:

```json
{
  "id": "msf-01",
  "category": "viewport | layout-region | color-surface | typography-scale | component-proportion | density-spacing | focal-object",
  "sourceRegion": "header | hero | sidebar | card | list | table | bottom-nav | footer",
  "fact": "hero image occupies about 58% viewport width and is vertically centered below nav",
  "measurementBasis": "visual estimation from screenshot region, or browser computed style when URL available",
  "measurement": {
    "unit": "percent | px | color | ratio | count",
    "value": "58vw / #fbfbfd / 3:2 / row height 48px"
  },
  "priority": "high | medium | low",
  "tolerance": "exact | small | approximate",
  "usedByCheckpointIds": ["vc-01"]
}
```

Coverage requirements:

- At least 5 high priority measured facts.
- At least 5 high priority measured facts must include `measurementBasis`.
- Must cover `viewport`, `layout-region`, `color-surface`, `component-proportion`, and `density-spacing`.
- URL long-page restore must cover `first-screen`, `middle-section`, and `footer-bottom` region groups.
- Mobile screenshot restore must record device canvas ratio, top system/navigation height, content width, and bottom bar/gesture area when present.
- Every high-priority measured fact must map to at least one restore checkpoint through `usedByCheckpointIds[]`.

## Mandatory Quantification Rules

High-priority measured facts MUST include numeric values. The following patterns are FORBIDDEN as standalone high-priority facts:

- "左侧栏较窄" → MUST be "sidebar width = 168px (11.7% of 1440px viewport)"
- "浅灰背景" → MUST be "sidebar bg ≈ #f4f4f5 (sampled from screenshot region)"
- "小字号" → MUST be "task list item font-size ≈ 12px, line-height ≈ 20px"
- "紧凑间距" → MUST be "task list vertical gap ≈ 4px, item padding ≈ 6px 8px"
- "有阴影" → MUST be "card shadow ≈ 0 1px 3px rgba(0,0,0,0.04)"

Required numeric types by category:

| Category | Required numeric content |
|----------|------------------------|
| `color-surface` | HEX value (sampled or estimated from screenshot) |
| `density-spacing` | px value for gap, padding, or margin |
| `typography-scale` | font-size px and line-height |
| `component-proportion` | ratio, percentage, or px width/height |
| `layout-region` | px or percentage width/height |

Each high-priority fact must include a `precision` field:

```json
{
  "precision": "exact | estimated-±5% | approximate-±15%"
}
```

Facts with `precision: "approximate-±15%"` trigger post-generation visual calibration.

## Source Document Profile And Region Groups

Before measured facts, write `runtime-orchestration-summary.json.project.sourceDocumentProfile`:

```json
{
  "sourceType": "image | url | image+url",
  "documentLengthClass": "short | medium | long",
  "viewportScrollRatio": 1.0,
  "deviceFramePresent": false,
  "requiredRegionGroups": ["first-screen", "middle-section", "footer-bottom"]
}
```

Write source region coverage at `project.sourceRegionCoverage[]` using `regionGroup` and `status` / `mappedStatus`. High and medium priority rows must be `mapped` or `intentionally-deviated`; `unmapped` blocks preflight.

## Restore Visual Checkpoints

Before dispatch, write 8-12 compact checkpoints into `runtime-orchestration-summary.json.project.restoreVisualCheckpoints`.

Each checkpoint must use this shape:

```json
{
  "id": "vc-01",
  "priority": "high | medium | low",
  "dimension": "layout | color-rhythm | typography | component-proportion | density | fine-detail",
  "sourceObservation": "exact observed visual fact from the source",
  "targetImplementation": "how it must be rebuilt in HTML/CSS",
  "tolerance": "none | small spacing variance | approximate icon acceptable",
  "region": "header | hero | card | table | bottom-nav | modal | sidebar | form"
}
```

Coverage requirements:

- At least 5 high priority checkpoints.
- Must cover all checkpoint dimensions: `layout`, `color-rhythm`, `typography`, `component-proportion`, `density`, and `fine-detail`.
- `component-proportion` must appear at least twice, or represent at least 25% of all checkpoints.
- Checkpoints must be executable visual facts. Avoid vague taste language.
- `similarityFreeze` remains a short 3-5 anchor summary; `restoreVisualCheckpoints` is the enforceable implementation contract.

## RestorePagePacket

Every restore page dispatch must use `RestorePagePacket` and `intent-workflows/intent-page-restore-1to1/restore-1to1-page-runtime.md`.

Required fields:

```json
{
  "nodeId": "page-index",
  "htmlSrc": "pages/index.html",
  "cssPath": "{designProjectPath}/colors_and_type.css",
  "htmlFilePath": "{designProjectPath}/pages/index.html",
  "brandPrefix": "string",
  "sourceType": "image | url | image+url",
  "referenceCaptureEvidence": {},
  "sourceAuthorityLock": "<copy exact runtime-orchestration-summary.json.project.sourceAuthorityLock object>",
  "sourceIdentity": {},
  "pageStateLock": {},
  "sourceDocumentProfile": {},
  "measuredSourceFacts": [],
  "restoreVisualCheckpoints": [],
  "restorationContractLite": {},
  "visualSpecExcerpt": "compact page or page-slice visual spec",
  "sourceRegionCoverage": [],
  "contentToPreserve": [],
  "fillHtmlHeadCommand": "node {SKILL_DIR}/shared-runtime/deterministic-tooling/apply-html-head-contract.mjs <css-path> <html-file> --title=\"...\" --lang=\"...\" --prefix=...",
  "completionSchema": "restore"
}
```

Packet gates:

- `RestorePagePacket` has priority over every non-restore packet shape.
- The packet must include `restoreCompactPacket` generated by `build-page-dispatch-manifest.mjs`; do not paste full `runtime-orchestration-summary.json` into a Sub-Agent task.
- Dispatch is forbidden until `validate-restore-contract.mjs <design-project-path> --mode=preflight` has written `restore-contract-report.json success=true`. If the report contains `fixPlan[]`, apply only safe fixes through `--apply-safe-fixes`; do not hand-edit visual authority fields.
- Do not dispatch if `sourceType` does not match the available source evidence.
- Do not dispatch if `sourceIdentity`, `pageStateLock`, or `sourceDocumentProfile` is missing.
- Do not dispatch if `measuredSourceFacts` is missing or has fewer than 8 rows.
- Do not dispatch if `restoreVisualCheckpoints` is missing or has fewer than 8 rows.
- Do not dispatch if any high/medium `sourceRegionCoverage` row is `unmapped`.
- Do not dispatch if `visualSpecExcerpt` is empty or only points to a file path.
- For `sourceType: "url"`, do not dispatch without `referenceCaptureEvidence.fullPageScreenshotEvidence`.

## Step 10 — Dispatch Data Delivery

### 10a. RestorePagePacket File Delivery

Main Agent MUST write the complete `RestorePagePacket` to `{designProjectPath}/dispatch-packet-{nodeId}.json` before dispatch. This file is the Sub-Agent's authoritative data source.

The file must contain ALL fields from the RestorePagePacket schema above, assembled from:
- **Manifest entry outer fields**: `nodeId`, `htmlSrc`, `cssPath`, `htmlFilePath`, `brandPrefix`, `restoreContractStatus`, `fillHtmlHeadCommand`
- **restoreCompactPacket inner fields**: `sourceType`, `sourceIdentity`, `pageStateLock`, `sourceDocumentProfile`, `measuredSourceFacts`, `restoreVisualCheckpoints`, `sourceRegionCoverage`, `contentToPreserve`
- **Summary-level fields**: `referenceCaptureEvidence`, `sourceAuthorityLock`, `restorationContractLite`, `visualSpecExcerpt`

For `fillHtmlHeadCommand`: if `build-page-dispatch-manifest.mjs` returns `null`, Main Agent must construct the command using the pattern:
```bash
node {SKILL_DIR}/shared-runtime/deterministic-tooling/apply-html-head-contract.mjs {cssPath} {htmlFilePath} --title="{pageTitle}" --lang="{lang}" --prefix={brandPrefix}
```

FORBIDDEN: Inlining the packet as text in the Task description. FORBIDDEN: Writing only `restoreCompactPacket` without outer fields.

### 10b. Reference Screenshot Delivery

Task dispatch MUST include the reference screenshot workspace path in the description:

```
Reference image: {designProjectPath}/reference/source-screenshot.png
```

Before dispatch, if the screenshot is in `.uploads/` (outside design project directory), Main Agent must copy it into `{designProjectPath}/reference/` (NOT `assets/`) to ensure Sub-Agent file access. The `reference/` directory is for source inputs — `assets/` is only for generated design assets that appear on the canvas.

### 10c. Structured Visual Spec

Task description MUST include a structured `=== VISUAL SPEC ===` block with these sections:

```
=== VISUAL SPEC ===

[LAYOUT]
viewport: {width}×{height}, {shell-type}
{region}: {position}, {size}

[SPACING]
{element}-padding: {values}
{element}-gap: {values}

[TYPOGRAPHY]
{element}: {size}/{line-height} {weight}

[COLORS]
{surface}-bg: {hex}
{element}-border: {hex}

[SHADOWS & DEPTH]
{element}-shadow: {css-shadow-value}

[RADII]
{element}: {px}

=== END SPEC ===
```

FORBIDDEN: Replacing the Visual Spec with natural language descriptions like "左侧固定浅灰侧栏".

### 10d. Output Strategy

- `documentLengthClass === "single-screen"`: Sub-Agent MUST output the complete HTML in a single `apply_patch` operation (including `<html>`, `<head>`, `<body>`, `<style>`).
- `documentLengthClass === "medium" | "long"`: Sub-Agent may split into 2-3 `apply_patch` operations, each covering a complete `regionGroup`.

### 10e. Task Description Template

```
Task: Restore page {nodeId} using restore-1to1-page-runtime.md

Data: Read dispatch packet from {designProjectPath}/dispatch-packet-{nodeId}.json
Reference image: {designProjectPath}/reference/source-screenshot.png

=== VISUAL SPEC ===
[LAYOUT]
...
[SPACING]
...
[TYPOGRAPHY]
...
[COLORS]
...
[SHADOWS & DEPTH]
...
[RADII]
...
=== END SPEC ===

Constraints:
- Single apply_patch output (single-screen page)
- Use exact numeric values from Visual Spec and measuredSourceFacts
- Do not use reference image as page body/background
- Run fillHtmlHeadCommand after writing HTML
```

## CSS And Head Discipline

- Generate or derive `colors_and_type.css` from the visual authority.
- Before dispatch, `colors_and_type.css` must include semantic aliases required by `apply-html-head-contract.mjs` for the selected `brandPrefix`:
  - `--{brandPrefix}-background`
  - `--{brandPrefix}-foreground`
  - `--{brandPrefix}-card`
  - `--{brandPrefix}-primary`
  - `--{brandPrefix}-border`
  - `--{brandPrefix}-muted`
  - `--{brandPrefix}-radius-sm`
  - `--{brandPrefix}-radius-md`
  - `--{brandPrefix}-radius-lg`
- Use exact colors from the visual authority when available; approximate only when extraction is impossible and record the deviation.
- Sub-Agents use `apply-html-head-contract.mjs` exactly as provided in `RestorePagePacket`.
- Sub-Agents must not hand-edit `<head>`, run validation scripts, start preview, or use TodoWrite.

### Color Extraction Priority

Color values in `colors_and_type.css` MUST follow this extraction priority:

1. **Screenshot available**: Visually identify colors from key regions (background, sidebar, card, primary accent, border) using your multimodal vision capability. Record the region name as `measurementBasis`. Do NOT create Python/PIL/Pillow scripts to extract pixel colors — use visual estimation directly.
2. **URL available**: Extract computed colors from browser DevTools.
3. **Neither available**: Estimate colors and mark every variable with `/* approximate */`.

**FORBIDDEN for Main Agent in restore_1to1:** Creating any ad-hoc Python, Shell, or Node.js scripts to process/measure/crop the source screenshot. Color extraction must use visual judgment, not programmatic pixel sampling.

### Minimum Color Differentiation

- Adjacent visual surfaces intended to be distinct (e.g., sidebar vs. main stage) MUST differ by at least 2 perceptible color steps (≈ ΔL*≥3 in CIELAB, or ≥ #030303 hex difference).
- If two surfaces cannot be distinguished by color alone, the distinction MUST be achieved through borders or shadows.
- FORBIDDEN: Using generic gray palettes (#f6f6f6, #f7f7f8, #e3e3e3) without explicit sampling evidence from the visual authority.

### CSS Variable Annotation

Each CSS variable MUST include a comment with its source:

```css
--{prefix}-sidebar: #f2f3f5; /* sampled: sidebar region center */
--{prefix}-panel: #fafbfc;   /* sampled: main stage background */
--{prefix}-primary: #6549e8; /* sampled: send button fill */
```

## Restore Contract Preflight

Before running `build-page-dispatch-manifest.mjs --mode=restore`, run:

```bash
node {SKILL_DIR}/shared-runtime/deterministic-tooling/validate-restore-contract.mjs <design-project-path> --mode=preflight
```

If this fails and `restore-contract-report.json.fixPlan[]` contains safe structural fixes, run exactly once:

```bash
node {SKILL_DIR}/shared-runtime/deterministic-tooling/validate-restore-contract.mjs <design-project-path> --mode=preflight --apply-safe-fixes
```

Only continue when `restore-contract-report.json` reports `success: true`. Then run:

```bash
node {SKILL_DIR}/shared-runtime/deterministic-tooling/build-page-dispatch-manifest.mjs <design-project-path> --mode=restore
```

**Manifest Build Iteration Limit:** `build-page-dispatch-manifest.mjs` may be run at most **2 times**. If it fails on the first run, fix the specific error reported (usually missing `brandPrefix` at project level or `pages[]` structure issues), then run once more. If it still fails after the second attempt, manually write `runtime-dispatch-manifest.json` with the required fields from `pages[]` and proceed to dispatch. Do not enter a third+ build cycle.

This writes `dispatchPreflightManifest[]`, `restoreContractStatus`, `restoreCompactPacket`, `allowedWritePaths[]`, `toolPolicy`, `deterministicCommands`, and pre-dispatch controlled file hashes. It does not write final `expectedDispatches[]`; the Main Agent must persist `expectedDispatches[]` only after Sub-Agent completion, using each completion's legal `nodeId`, `status`, `changedFiles[]`, and `toolCallLedger`. Do not hand-write or SearchReplace preflight fields. After this point, copy validator/repair commands from `deterministicCommands`; do not search the workspace for script paths or guess arguments.

## Post-Dispatch Finalization (Step 11)

After Sub-Agent returns completion JSON, Main Agent executes a streamlined finalization.
The Sub-Agent already has access to the reference screenshot and structured Visual Spec,
so post-dispatch is two steps: record completion, then artifact readiness.

### 11a. Record Dispatch Completion

Run `record-dispatch-completion.mjs`:
```bash
node {SKILL_DIR}/shared-runtime/deterministic-tooling/record-dispatch-completion.mjs <design-project-path> --node-id=<nodeId> --status=completed --changed-files=<comma-separated> --trace-digest=<hash> --tool-ledger-json=<json-or-file>
```

### 11b. Proceed Directly to Artifact Readiness

Do NOT write evidence fields. Do NOT patch `runtime-orchestration-summary.json`.
The Sub-Agent validated visual quality against the reference screenshot during generation.
Evidence fields (`restoreEvidenceReview`, `visualDiffReview`, `sourceFactCoverageMap`) serve
no purpose in the current flow and are skipped entirely.

FORBIDDEN in restore_1to1 post-dispatch:
- Running `validate-design-workspace.mjs`
- Running `record-validation-repair-entry.mjs`
- Reading or writing `validation-report.json`
- Any `apply_patch` to `runtime-orchestration-summary.json` after dispatch completion
- Writing `restoreEvidenceReview`, `visualDiffReview`, `sourceFactCoverageMap`, or `scrollRegionMarkers`

If you find yourself reading a validation report or patching the summary JSON,
STOP IMMEDIATELY and proceed to Artifact Readiness.

## Artifact Readiness

After recording dispatch completion (Step 11a), run the Design artifact readiness gate directly:

```bash
node {SKILL_DIR}/shared-runtime/deterministic-tooling/validate-finish-readiness.mjs <designProjectPath> --check=all --final-response-file=<draft.md>
```

The gate checks that the restored page(s), generated image assets, and interactions are registered in `.design` and point to existing files. In restore mode it also checks the final response draft is link-free and path-free.

## Final Response

The final response may be a concise natural-language completion summary. Do not include manual artifact links, local paths, or `computer://` URLs.
