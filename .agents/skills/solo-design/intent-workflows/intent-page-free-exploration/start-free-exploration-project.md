# Create Project — Free Fast Path

Use this workflow only when `operatingMode === "free-explore"` and no active Design Library identity exists.

This path optimizes for speed while preserving render correctness. It does not apply to Library-bound, high-fidelity replication, existing-page edit, or image-only graphic flows.

## Non-Negotiable Scope Guard

- If the task has a user-selected Design Library, an existing `.design.config.designLibrary`, `componentPlan`, `actualTokenNameReference`, or a Library path, stop and route to `start-library-bound-project.md`.
- If `intentProfile.caseFamily === "restore_1to1"` or the task has high-fidelity replication intent, stop and use `start-restore-1to1-project.md`.
- If you are reading this file during `restore_1to1`, stop immediately and return to the restoration path.
- If `intentProfile.caseFamily === "graphic_design"` with `graphicStrategy === "layout-static"`, stop and use the standard HTML/page static layout path; do not use the simplified free fast path.
- If the task has persistent visual states (tabs, modal, drawer, search result, loading, empty, error, success), do not use the simple single-page fast path; plan state pages first.

## Fast Path Complexity Router

Free-fast has three lanes. Choose one and stay within it:

| Lane | Use When | Page Generation Template |
| --- | --- | --- |
| `simple-free-fast` | 1 ordinary page, no persistent visual states, no charts, <4 major sections | `free-exploration-page-runtime.md` |
| `stateful-free-fast` | tabs, modal, drawer, search result, loading/empty/error/success states, step flows | `free-exploration-page-runtime.md` with Stateful Packet |
| `chart-free-fast` | dashboard, metrics page, chart tab, chart canvas needed | `free-exploration-page-runtime.md` with `chartsRequired: true` |

Stateful/chart free-fast is still free-fast. Do not fall back to the full create-project flow solely because tabs or charts exist.

Escalate out of free-fast only for:
- Library-bound mode
- high-fidelity restoration
- layout-static graphic design requiring exact typography / long-form PPT / manual layout
- multi-device split
- long PRD where page count exceeds the fast path cap

## Free Mode Fast Path Card

1. Read routing and user-facing policy only: `SKILL.md route priority`, `delivery-quality/user-facing-language-guidelines.md`, this file, and the relevant dispatch packet section.
2. Build a compact `Route Card`: mode, surface, complexity, whether questions/images/generation tree are needed, and validation level.
3. Build one `Project Brief`: user intent, creative recipe, CSS contract, page plan.
4. Build one `Page Packet` per page: nodeId, htmlSrc, writeMode, sections, device quick rules, assets, domIdsRequired, compact completion schema.
5. Run `CSS Contract Preflight` before page dispatch and persist `cssPreflightEvidence`.
6. Sub-Agent reads `free-exploration-page-runtime.md`, not the full strict page template.
7. Final validation is smoke validation only, but the command must still write `validation-report.json`. Render-blocking errors must be fixed; soft style warnings must not trigger repair loops.

### Mobile Visual Mockup Viewport Rule

For `project.deviceType === "mobile"`, ordinary App/H5/mini-program visual mockup pages default to:

- `viewportMode: "document-scroll"`
- natural document flow (`body` may use `min-h-screen`, never forced `h-screen overflow-hidden`)
- full canvas height: all page content must be visible on the design board

Do not use `viewportMode: "app-shell"` for mobile visual mockups in the current skill. If a future requirement needs a fixed-screen mobile workbench/dashboard, add an explicit schema field and validator exception in a separate change rather than overloading ordinary App UI mockups.

In prototype preview, the Design SDK already wraps mobile pages in a device frame and provides the fixed phone viewport. The generated HTML does not need to implement its own fixed outer viewport for this purpose.

For multi-page mobile projects with shared bottom navigation, write a compact `sharedProjectShellContract.mobileNavigation` object before page dispatch. Include `type`, ordered `items` with stable `key` values, `heightPx`, `position`, `activeState`, and a derived `structure` contract. Pass this object to every Page Packet. Each generated tab item must carry `data-nav-key="<item.key>"`; `data-dom-id` is optional click wiring and must not be used as the active-state key. Do not dispatch a separate shared-nav Sub-Agent only to create a bottom tab partial; the compact contract is enough for free-fast efficiency.

Derive `mobileNavigation.structure` once from `items.length`, `heightPx`, and `position`; do not hardcode a 5-tab / 60px / fixed-bottom layout unless those values are actually in this project contract:

```json
{
  "navTag": "nav",
  "navClass": "{position-derived classes} h-[{heightPx}px]",
  "innerClass": "w-full max-w-md mx-auto grid grid-cols-{itemCount} h-full",
  "itemTag": "a | button",
  "itemClass": "min-w-0 flex flex-col items-center justify-center gap-0.5 px-1 h-full",
  "iconClass": "w-5 h-5 shrink-0",
  "labelClass": "text-[11px] leading-none whitespace-nowrap max-w-full truncate",
  "activeRule": "only color/font-weight/data-active may change; no class changes that affect layout",
  "markerAttr": "data-mobile-nav=\"global\"",
  "canonicalHtmlByKey": {
    "home": "<nav data-mobile-nav=\"global\" ...>...</nav>"
  }
}
```

Default derivation: `itemCount = items.length`; for 3-5 item tabs use `grid-cols-{itemCount}`; for more than 5 items use an explicit scroll-row contract such as `grid-flow-col auto-cols-[72px] overflow-x-auto no-scrollbar`. `heightPx` comes from the contract, or Main Agent sets it once before dispatch (recommended: `64` for icon+label, `56` for icon-only). `position` comes from the contract: `flow-bottom` is preferred for expanded mobile canvas mockups, while `fixed-bottom` is allowed only when the intended app chrome is persistent and page content reserves bottom space.

[FORBIDDEN] Letting each page invent its own bottom tab order, height, icon style, label visibility, active-state geometry, or fixed/absolute positioning. Detail, modal, reward, or other one-off pages may omit global navigation only when the page plan explicitly says so.

Before dispatching each ordinary mobile page, expand `canonicalHtmlByKey[mobileNavigationActiveKey]` into the Task query under `## Mobile Navigation Contract (MANDATORY)`. Use compact icon markers such as `<i data-lucide="home" class="{iconClass}"></i>` by default; do not inline large SVG path payloads into the canonical nav. If `items.length > 6`, store a compact `canonicalHtmlTemplate` plus active key and expand only the current page's block in the Task query.

Before dispatching any Page Sub-Agent, run the deterministic manifest builder:

```bash
node {SKILL_DIR}/shared-runtime/deterministic-tooling/build-page-dispatch-manifest.mjs {designProjectPath} --mode=free-fast
```

If the command exits non-zero, stop before Task dispatch and fix the missing `runtime-orchestration-summary.json` fields. Do not dispatch pages and do not ask Sub-Agents to infer missing fields.

For free-fast mobile projects, bottom navigation alone does not create a generation-tree parent or `project-shell` Task. The Main Agent writes `sharedProjectShellContract.mobileNavigation.structure.canonicalHtmlByKey` directly and passes the current page's canonical nav HTML in the Page Packet.

[FORBIDDEN] Dispatching `Task: Generate project shell fragment` when the only shared region is global mobile bottom navigation.

## Execution Path Lock

After this workflow is selected, do not read high-fidelity restoration sections, Library-bound strict workflow, or the complex create-project flow unless a guard above explicitly escalates out of free-fast. Store the route card in `runtime-orchestration-summary.json.project.intentProfile.routingReason` and use it as the stable routing evidence for the rest of the run.

For execution clarity, also store this project-level read scope in `runtime-orchestration-summary.json.project`:

```json
"contextReadScope": {
  "mainAgent": {
    "forbiddenReads": ["other intent-workflows/**", "Sub-Agent implementation files before dispatch"]
  },
  "pageSubAgent": {
    "allowedReads": ["current lane page runtime guide", "current lane dispatch contract excerpt", "current Page Packet", "supplementaryReads[] only"],
    "forbiddenReads": ["SKILL.md full re-read", "other intent-workflows/**", "full runtime-orchestration-summary.json unless explicitly sliced"]
  },
  "readScopeLedgerWriter": "shared-runtime/deterministic-tooling/build-page-dispatch-manifest.mjs"
}
```

Before running `build-page-dispatch-manifest.mjs`, also record:

```json
{
  "selectedIntentWorkflowRead": true,
  "contextRequirementsLoaded": [
    {"path": "shared-runtime/runtime-boundaries/lane-runtime-contracts.md", "readStatus": "loaded", "bodyRead": true},
    {"path": "shared-runtime/agent-dispatch-runtime/lane-dispatch-index.md", "readStatus": "loaded", "bodyRead": true},
    {"path": "delivery-quality/page-rendering-quality-gate.md", "readStatus": "loaded", "bodyRead": true},
    {"path": "delivery-quality/design-artifact-validation.md", "readStatus": "loaded", "bodyRead": true},
    {"path": "delivery-quality/delivery-evidence-contract.md", "readStatus": "loaded", "bodyRead": true},
    {"path": "visual-experience/visual-experience-guidelines.md", "readStatus": "loaded", "bodyRead": true}
  ],
  "validationRunDiscipline": {
    "maxFullValidationRuns": 2,
    "softWarningsTriggerRepair": false,
    "blockingRepairMode": "targeted-once",
    "forbiddenRepairTriggers": ["soft-warning-only", "provenance-warning-only", "style-warning-only"]
  },
  "lowValueCallWatchdog": {
    "applies": true,
    "noProgressSignals": ["no_tool_call", "no_artifact_diff", "no_structured_decision"],
    "noProgressNextAction": "enter_readiness_or_blocked_summary"
  }
}
```

This read scope is a dispatch contract and declaration audit. `build-page-dispatch-manifest.mjs` records `project.readScopeLedger[]`; the Main Agent must not hand-write ledger entries. Any extra read must first be declared in `supplementaryReads[]` with `{path, reason, ownerLane}`. The ledger does not observe actual tool-call traces; actual context-bloat or sub-agent misuse enforcement still comes from dispatch packet scope, runtime discipline, and external trace/evaluation checks.

## TodoWrite Discipline

- Main Agent uses TodoWrite only for real phase changes, not per-section narration.
- Page Sub-Agent does not use TodoWrite. Every FreePagePacket Task query must include the Tool Discipline block from `shared-runtime/agent-dispatch-runtime/lane-dispatch-index.md`; referencing the schema without copying the block into the Task query is invalid.
- Batch all completed Sub-Agent status changes into one TodoWrite update.
- Do not use TodoWrite for preview, validation warnings, or per-section micro status.

## Minimal Project Entry Template

Use this project-level shape when writing the first `.design` file in free-fast mode. Do not write a temporary `.design` without `config.deviceType`; the host uses this field to choose the default canvas/preview device.

```json
{
  "name": "{project title}",
  "version": 1,
  "description": "{short description}",
  "data": [
    { "...": "page nodes" }
  ],
  "config": {
    "autoLayout": true,
    "deviceType": "{desktop|mobile|tablet|freeSize}",
    "projectName": "{user-facing project name}"
  }
}
```

Rules:
- `config.deviceType` is fixed from the route card/user request before the first `.design` write.
- Mobile App/H5/mini-program visual mockups must write `"deviceType": "mobile"`.
- Later interaction updates must preserve the existing `config` object and must not recreate it as `"desktop"`.

## Minimal Page Node Template

Use this minimal template when writing `.design` page skeletons in free-fast mode. Complex image/theme/library fields still follow `shared-runtime/design-artifact-formats/design-project-file-format.md`.

```json
{
  "id": "page-{slug}",
  "title": "{business title}",
  "type": "page",
  "version": 1,
  "createdAt": 1712476800000,
  "devMetadata": {
    "htmlSrc": "pages/{slug}.html",
    "interactions": []
  },
  "canvasData": {
    "x": 0,
    "y": 0,
    "group": 0
  }
}
```

Rules:
- `id` must match the `htmlSrc` basename: `pages/order-info.html` -> `page-order-info`.
- `version` is a positive integer, normally `1`.
- `createdAt` is the current millisecond timestamp. Do not copy the example timestamp.
- Use `devMetadata`, never `metadata`.
- Page state metadata such as `stateGroupId`, `stateRole`, and `derivedFromHtmlSrc` goes under `devMetadata` when needed.

## Stateful Free-Fast Planning

For persistent visual states, create one canvas page per meaningful state.

## Default Deliverable Visibility

For task-driven, multi-step, or information-complete pages, write `project.defaultDeliverableVisibility` before dispatch. Use this gate when the user names required modules, data blocks, process steps, or business information that must be visible in the delivered artifact.

Rules:
- Required user-facing content is visible by default, or represented by a separate canvas state/page.
- Hidden content is allowed only for optional modal/drawer/popover/hover/transient states that are not part of the core delivered information.
- Do not use JS-only reveal flows to satisfy core user requirements.
- Pass the relevant `defaultDeliverableVisibility` slice to the `FreePagePacket`.

Example:

```json
{
  "applies": true,
  "requiredVisibleRegions": [
    {
      "htmlSrc": "pages/appointment.html",
      "selector": "#section-doctors",
      "label": "doctor schedule",
      "source": "user requirement"
    }
  ],
  "hiddenAllowed": []
}
```

Required state plan:

```json
{
  "stateGroupId": "order-detail-tabs",
  "basePage": {
    "nodeId": "page-order-info",
    "htmlSrc": "pages/order-info.html",
    "stateRole": "base"
  },
  "derivedPages": [
    {
      "nodeId": "page-order-chart",
      "htmlSrc": "pages/order-chart.html",
      "stateRole": "derived",
      "derivedFromHtmlSrc": "pages/order-info.html",
      "mutableRegions": ["active tab styling", "tab panel content", "chart/table content"],
      "chartsRequired": true
    }
  ],
  "immutableShellRegions": ["body/main frame", "order summary header", "tab bar", "tab-panel container"]
}
```

Rules:
- Generate the base page first.
- Derived pages copy the base HTML and edit only `mutableRegions`.
- Derived pages do not run `apply-html-head-contract.mjs`.
- If a derived page needs charts, the base or derived copy must inherit a head generated/replaced with `--charts`.
- The `.design` page nodes must record state metadata consistently with `lane-dispatch-index.md §7`.
- Tab switching controls must have stable `data-dom-id` values. Main Agent registers hidden interactions with `hideEdge: true` and verifies targets using `tabInteractionSelfCheck`.

## Chart Free-Fast Planning

When a page or state contains charts:
- Set `chartsRequired: true` in the Page Packet.
- The `fillHtmlHeadCommand` must include `--charts` for that page or for the base page inherited by derived chart states.
- Use real-looking mock data but keep chart implementation simple.
- Do not introduce additional chart libraries.

## Creative Recipe

Generate one compact recipe instead of reading the full aesthetics system by default:

```json
{
  "businessTone": "...",
  "layoutArchetype": "...",
  "visualSignature": "...",
  "densityTarget": "simple|balanced|dense",
  "avoidOneThing": "..."
}
```

Ask at most one style question only when the task is marketing/showcase/brand-heavy and the user gave no visual direction.

## CSS Contract Preflight

Before dispatching any page Sub-Agent:

1. Create `colors_and_type.css` with a stable `brandPrefix`.
2. Ensure the CSS defines semantic aliases resolvable by `apply-html-head-contract.mjs`: background, foreground, card, card foreground, popover, popover foreground, primary, primary foreground, muted, muted foreground, border, input, ring, plus the core radius scale (`sm`/`md`/`lg` or supported `small`/`medium`/`large` aliases). For prefixed CSS, use variables such as `--<prefix>-background`, `--<prefix>-foreground`, `--<prefix>-card`, `--<prefix>-card-foreground`, `--<prefix>-primary`, `--<prefix>-primary-foreground`, `--<prefix>-border`, `--<prefix>-muted`, `--<prefix>-ring`, and `--<prefix>-radius-md`.
   - These aliases must map to the single primary hue, neutral surfaces/text, or semantic state colors. They must not introduce `secondary` / `accent` brand hues in free-explore mode.
   - Do not add `secondary` or `accent` aliases only to satisfy Tailwind classes. Replace generated `bg-secondary`, `text-accent`, `border-accent`, or similar classes with primary/neutral/state token usage instead.
3. Run `apply-html-head-contract.mjs` once against a preflight HTML path outside `{designProjectPath}/pages/`, preferably `{designProjectPath}/.preflight/preflight.html`:
   `node {SKILL_DIR}/shared-runtime/deterministic-tooling/apply-html-head-contract.mjs <css-path> <preflight-html> --title="Preflight" --lang=<lang> --prefix=<prefix>`
4. Verify the command exits `0` and the generated head contains `id="theme-vars"`, `id="semantic-token-fallback"`, `@theme inline`, Tailwind CDN, and `<html class="light|dark">`. A command that exits `0` but generates no `@theme inline` or no `semantic-token-fallback` is a failed preflight, not a pass.
5. Pass `cssPreflightStatus: "passed"`, compact `cssPreflightEvidence`, and the exact `fillHtmlHeadCommand` into every Page Packet.
6. If skeleton generation fails with `CSS semantic theme mapping failed` or missing `@theme inline` / semantic fallback, rewrite `colors_and_type.css` once by adding the missing semantic aliases and re-run.
7. After one failed rewrite, stop with the render-blocking error. Do not enter open-ended CSS debugging.

Free mode may use support hues, radius mood, and depth mood as design choices. These are style decisions, not post-validation repair gates.

Persist the preflight result in `runtime-orchestration-summary.json.project.cssPreflightEvidence`:

```json
{
  "applies": true,
  "status": "passed | failed",
  "command": "node {SKILL_DIR}/shared-runtime/deterministic-tooling/apply-html-head-contract.mjs <css-path> <preflight-html> --title=\"Preflight\" --lang=<lang> --prefix=<prefix>",
  "brandPrefix": "string",
  "checks": {
    "themeVars": "present | missing",
    "semanticTokenFallback": "present | missing",
    "themeInline": "present | missing",
    "tailwindCdn": "present | missing",
    "htmlClass": "present | missing",
    "semanticMappings": "resolved | missing"
  },
  "retryCount": 0,
  "blockingReason": null
}
```

`cssPreflightStatus: "passed"` in a `FreePagePacket` is invalid unless this evidence exists and records `status: "passed"`.

## Write Mode Routing

| Mode | Trigger | Rule |
| --- | --- | --- |
| `SkeletonMainAtomic` | Ordinary single page, fewer than 4 major sections | Generate skeleton, then replace `<main>` once |
| `SectionPlanThenWrite` | Information-dense/dashboard, 4-7 major sections | Plan sections first, then replace `<main>` once |
| `SectionedPatch` | 7+ sections, stateful base page, or expected HTML > 45KB | Maximum 3 section patches |

Unplanned iterative SearchReplace as a creative loop is forbidden. Sectioned writing is allowed only when the selected mode says so.

## Interaction Registration Self-Check

After writing `.design` interactions and before running full smoke validation, immediately re-read the `.design` file and verify every expected `domId` in the planned `--require-interactions` list exists in the owning page node's `devMetadata.interactions`.

Record this compact evidence in `runtime-orchestration-summary.json.project.wiringRegistrationEvidence` when a summary exists:

```json
{
  "expectedDomIds": ["cta-library:home.html", "cta-book-detail:home.html"],
  "allExpectedDomIdsRegistered": true,
  "missingDomIds": []
}
```

If `missingDomIds` is non-empty, fix `.design` once, re-read once, and stop if it still fails. Do not run full `validate-design-workspace.mjs` merely to discover missing interaction entries.

## Smoke Validation

Before dispatch preflight, `runtime-orchestration-summary.json.project.validationRunDiscipline` must already exist:

```json
{
  "maxFullValidationRuns": 2,
  "softWarningsTriggerRepair": false,
  "blockingRepairMode": "targeted-once",
  "forbiddenRepairTriggers": ["soft-warning-only", "provenance-warning-only", "style-warning-only"]
}
```

Run `validate-design-workspace.mjs` once after generation and always write machine-readable validation evidence:

```bash
node {SKILL_DIR}/shared-runtime/deterministic-tooling/validate-design-workspace.mjs <design-project-path> \
  --expected-pages=<N> \
  --report-json=<design-project-path>/validation-report.json
```

Completion cannot be claimed unless `validation-report.json` exists and records `success: true`. If the report contains `terminalState`, stop and report the blocking summary instead of repairing again. Fix only render-blocking errors:

- invalid or missing `.design`
- empty `data`
- page node points to missing HTML
- missing HTML document structure
- missing head infrastructure needed for rendering
- broken local images
- external/base64 image sources
- `apply-html-head-contract.mjs` failures

Soft warnings such as radius, shadow, secondary/accent, named colors, hardcoded colors, missing provenance, or missing generation tree do not trigger repair in this path.

Before completing, also verify:
- `validation-report.json` exists and records `success: true`.
- `validate-finish-readiness.mjs <design-project-path> --check=all` passes the Design Artifact Readiness Gate.
- The final response contains no manual file paths, markdown artifact links, or `computer://` URLs.

## Compact Completion

Sub-Agent reports compact JSON:

```json
{
  "nodeId": "page-index",
  "htmlSrc": "pages/index.html",
  "changedFiles": ["pages/index.html"],
  "qualityGate": "passed",
  "htmlWriteMode": "SkeletonMainAtomic",
  "domIds": [],
  "headInfrastructureStatus": {"themeVars": "present", "themeInline": "present"},
  "toolDisciplineEvidence": {"wroteOnlyAllowedPaths": true},
  "renderRisk": "none",
  "styleRecipeApplied": true,
  "sections": ["hero", "content", "actions"]
}
```
