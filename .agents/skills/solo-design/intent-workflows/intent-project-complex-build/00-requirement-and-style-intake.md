## Step 0.5 — Reference Material & Requirement Analysis (Main Agent, conditional)

> **Skip condition**: If the user's message is a straightforward text-only requirement with < 500 characters and no attached materials, skip this step entirely and proceed to Step 1.

This step handles two common real-world scenarios that the standard flow does not cover by default:

### A) Reference Material Analysis (when non-text materials are present)

When the user provides screenshots, URLs, ZIP files, or other attached artifacts:

1. **Read** `{SKILL_DIR}/delivery-quality/reference-material-ingestion-rules.md`
2. **Execute** the analysis flow appropriate to the material type (screenshot → visual analysis, URL → fetch & extract, ZIP → extract & classify)
3. **Produce** a "Design Constraints Document" (structured output format defined in that file)
4. **Feed forward**: The extracted constraints replace or augment Step 1's style selection:
   - If reference provides clear visual direction → **skip style inquiry** in Step 1
   - If reference provides page structure → inform Step 2 page list planning
   - If reference is "Reconstruct + Extend" intent → first page in Step 3 uses reference layout as guide

### B) Long Requirement Parsing (when text input is extensive)

When the user's message exceeds ~500 characters or contains PRD-like structured content:

1. **Read** `{SKILL_DIR}/delivery-quality/long-requirement-intake-rules.md`
2. **Execute** the 4-phase parsing: Structured Extraction → Page Prioritization → Feature Density Control → Requirement-to-Page Mapping
3. **Produce** a "Page Plan" (structured output format defined in that file)
4. **Feed forward**: The Page Plan provides the pre-determined page list (Step 2 nodeId pre-assignment), per-page feature requirements (Step 3 dispatch), visual direction summary (augments Step 1), and the page count cap decision when applicable

### C) Visual Checkpoint Planning (when layout-static or visually critical)

When the task is `graphic_layout_static`, composition-heavy, or otherwise depends on a strong visual result, read `visual-experience/visual-checkpoint-protocol.md` and write `runtime-orchestration-summary.json.project.visualQualityCheckpoints[]` before page dispatch.

The minimum checkpoint set covers:

- `visual-anchor`
- `information-hierarchy`
- `composition-structure`
- `implementation-strategy`

These checkpoints must describe observable output targets, not taste words. They guide generation and targeted repair only; they must not broaden page count, business content, or subjective polishing scope.

### Combined scenario (reference materials + long requirements)

When both are present (for example, screenshot + ZIP + long structured requirements):

1. Execute Reference Material Analysis first (extracts visual/structural constraints)
2. Then execute Long Requirement Parsing (extracts functional/content requirements)
3. Merge: visual direction from reference + page plan from text = complete project specification
4. Conflict resolution: text requirements win for content/features; reference materials win for visual style (unless text explicitly overrides)

### Multi-Device Project Split (when dual device types detected)

When Pre-Execution Preparation detects `multiDeviceProject: true` (user requirements span mobile + desktop):

1. **Phase 1 output includes device classification**: The Page Plan must tag each page with `targetDevice: 'mobile' | 'desktop'`
2. **Step 1 (Style Selection)**: Execute once — generate a single shared brand CSS
3. **Step 2 onwards**: Execute the per-project pipeline once per device project. The two device projects **may run interleaved in parallel**: Pass B initialization and its image/page generation dispatches may overlap with Pass A page generation (e.g., start Pass B project initialization while Pass A page Sub-Agents are still running). The only serialization constraint is that **all `.design` writes are executed by the Main Agent serially** (one write at a time per project file); Sub-Agent image/page generation across the two projects may interleave freely.
   - **Pass A (Mobile)**: Create mobile project directory, write `.design` with `deviceType: 'mobile'`, dispatch mobile-tagged pages
   - **Pass B (Desktop)**: Create desktop project directory, write `.design` with `deviceType: 'desktop'`, dispatch desktop-tagged pages
4. **Step 4 (Validation)**: Run validation independently on each project
5. **Step 5 (Preview)**: Present both projects to user with clear labels

**TodoWrite for multi-device**: Use a single todo list covering both passes. Example:
- Understanding your requirements (multi-device detected)
- Confirming design style (shared)
- Preparing mobile design project
- Designing mobile pages ({list})
- Preparing desktop design project
- Designing desktop pages ({list})
- Done, ready to preview (2 projects)

## Step 0.7 — Style Discovery & Definition (Main Agent, conditional)

> **Skip condition**: Skip if ANY of the following is true:
> - `operatingMode === "library-bound"` (Library provides the style)
> - Step 0.5 reference analysis already extracted a clear visual direction
> - The user's message already states explicit style preferences (color, font, mood)
> - Current project history provides usable `styleContinuityAnchors` for the requested continuation
> - `replicationMode === "high-fidelity"` (source site IS the style)
>
> **Reverse MUST-ASK**: If the user explicitly says they have no visual idea or preference ("no idea", "you decide", "anything is fine", "not sure", "surprise me" without a concrete style anchor), and the task is not Library-bound and not high-fidelity replication, do not skip style discovery. Ask one multiple-choice style question with 2-4 concrete directions.

When the user is in free-explore mode and hasn't stated visual preferences, proactively collect creative direction **before** mechanical style generation:

1. **Ask via AskUserQuestion** (pick 1–2 most relevant questions, not all):
   - What is the business tone? (e.g., professional/playful/luxurious/editorial)
   - Any reference brands or websites whose visual feel you like?
   - Primary color preference? (or "surprise me")
   - Content-heavy or visual-heavy?

2. **Produce a `styleDefinitionBrief`** (≤ 200 chars): A single sentence capturing the creative direction. Example: "Finance SaaS, cool neutral + indigo accent, Inter + Noto Sans SC, editorial rhythm, restrained surfaces."

3. **Produce compact execution controls**:
   - `designRead` (≤ 160 chars): `{pageKind} / {audience} / {businessTone} / {density} / {visualRiskToAvoid}` as a compact business design interpretation.
   - `designDials`: `{ layoutVariance, motionIntensity, visualDensity }` using 1-5 values derived from the current complex-build style decision.

4. **Store**: Write `styleDefinitionBrief`, `designRead`, and `designDials` into `runtime-orchestration-summary.json > project`. These fields inform Step 1's style derivation and Step 3's Sub-Agent dispatch.

> **Design rationale**: Without explicit creative direction, the AI defaults to "safe generic" output (mint accent, centered hero, 3-column cards). Collecting direction upfront enables distinctive, business-appropriate design choices from the start.

## Step 1 — Style Selection (Main Agent)

> **Library-bound out of scope**: If the pre-execution preparation phase detected `operatingMode: "library-bound"`, stop and use `intent-workflows/intent-page-library-bound/start-library-bound-project.md`. This file does not extract Library identity, token reference, component plan, or UI Kit fidelity.

**Default Path (Free Explore Mode)** — no Design Library available:

> **Step 0.7 Handoff**: If Step 0.7 already produced a `styleDefinitionBrief`, use it directly as the creative direction input below — do NOT re-ask the user for style preferences. AskUserQuestion in step 1 below fires only when Step 0.7 was skipped AND no clear direction exists.
>
> **Historical continuity handoff**: If existing project files provide `styleContinuityAnchors`, reuse those anchors directly and do NOT ask for a new style. The user query may override only explicitly mentioned dimensions.

1. Extract **industry/business scenario** keywords from user description, combine with audience characteristics, brand tone, and competitor visual conventions for that industry, independently derive 2–4 most fitting style options, and let the user choose via **AskUserQuestion**. All option fields must match the user's query language; avoid generic safe-default style options.
2. Based on the user's selected style direction, **generate a temporary `colors_and_type.css`** (format identical to Design Library output, including brand prefix CSS variables, typography class names, light/dark dual-mode variables). This file will be written to the project directory in Step 2, unifying HTML consumption with the Design Library path.
   - **Free-explore color policy (blocking)**: generate exactly one brand primary hue and its tints. Do not generate `secondary`, `accent`, `--color-secondary`, `--color-accent`, or their light/dark scales. If status colors are needed, generate a separate `stateColors` token set named only `--state-success`, `--state-warning`, `--state-error`, and `--state-info`; these are for semantic status only, not identity/category styling.
   - Identity/category/member-role styling must use text, icons, neutral tints, layout, or the primary tint. Do not use extra hues for parent/child, book genre, recommendation/comment/share type, avatars, or progress ownership.
   - **Free-explore semantic alias policy (blocking)**: the CSS must include the semantic aliases required by `apply-html-head-contract.mjs` before any page dispatch. With a `brandPrefix`, define aliases such as `--<prefix>-background`, `--<prefix>-foreground`, `--<prefix>-card`, `--<prefix>-card-foreground`, `--<prefix>-popover`, `--<prefix>-popover-foreground`, `--<prefix>-primary`, `--<prefix>-primary-foreground`, `--<prefix>-muted`, `--<prefix>-muted-foreground`, `--<prefix>-border`, `--<prefix>-input`, `--<prefix>-ring`, and `--<prefix>-radius-small|medium|large`. Without a prefix, use the equivalent `--color-*`, `--background`, `--foreground`, or supported radius aliases recognized by the script. These aliases may point to the single primary scale, neutral scale, or state tokens; they must not introduce a second brand hue.
   - **No secondary/accent bridge in free-explore**: do not add `secondary` / `accent` aliases merely to satisfy Tailwind semantic classes. If generated HTML uses `bg-secondary`, `text-accent`, `border-accent`, or similar classes in free-explore mode, replace those classes with primary/neutral/state token usage instead of adding `--<prefix>-secondary`, `--<prefix>-accent`, `--color-secondary`, or `--color-accent`.
   - **Free-explore radius policy (blocking)**: generate a restrained radius scale only: `--radius-sm: 2px or 4px`, `--radius-md: 8px`, `--radius-lg: 12px or 16px`, `--radius-full: 9999px`. Do not generate `--radius-xl`, `--radius-2xl`, `--radius-3xl`, or any card/button/input radius above `16px` unless the user's current query explicitly asks for large/soft/round shapes. Warm, family, child, lifestyle, friendly, storybook, premium, or playful tone is not enough to exceed 16px.
   - In `runtime-orchestration-summary.json`, set `designSource.styleConstraints.radiusMax` to `16` by default, and write `shapeSystem` / `sharedProjectShellContract.radiusScale` using the same restrained scale. Do not record `24px`, `28px`, `32px`, `rounded-2xl`, or `rounded-3xl` as continuity anchors unless directly requested by the user.
   - **Free-explore typography policy (blocking)**: generate one stable project font system, not per-page font experiments. Chinese pages default to sans-serif. If editorial/culture/publishing tone justifies serif, choose exactly one CJK serif display/title family and one body stack; do not generate competing serif stacks such as `Playfair Display` + `Georgia` + `Noto Serif SC` for Chinese headings. Decorative Latin serif names may be used only as Latin fallback/accent and must not precede the CJK serif in Chinese title variables. Record the selected title/body stacks in `styleContinuityAnchors.typographySystem` and `sharedProjectShellContract`, then pass them unchanged to every Sub-Agent.
   - **Free-explore shadow policy (blocking)**: ordinary/static cards, tables, lists, sections, buttons, and panels must use border or surface layering first. If they use shadow, every shadow color alpha must be `<= 0.05`. Shadow alpha above `0.05` is allowed only for real floating layers: modal, popover, dropdown, drawer, tooltip, toast, or menu. Do not use colored shadows or glow shadows.
   - In `runtime-orchestration-summary.json`, set `designSource.styleConstraints.staticShadowAlphaMax` to `0.05`, and write `surfaceAndDepth` / `sharedProjectShellContract.surfaceDepthModel` with the same rule: static surfaces are border/surface-led, only floating layers may use deeper elevation.
   - **Default icon policy (blocking)**: by default, do not record emoji as functional UI icons, UI icon placeholders, or primary visual markers in `styleContinuityAnchors`, `sharedProjectShellContract`, page requirements, or page packets. Translate emoji examples into an explicit icon plan before dispatch: provided/generated image assets when visual richness is needed; otherwise Design Library SVGs, Lucide icon names, or simple inline SVG. If the user explicitly asks for emoji icons or emoji visual style, preserve that intent in the icon plan and mark it as explicit user request.

### Multi-Style Exploration Path (Free Explore Mode Only)

When the user explicitly requests **multiple distinct styles in a single creation** (e.g., "give me 3 different style versions of this site", "I want to see completely different directions"), the following flow replaces the standard Default Path above:

1. **Derive differentiated style directions**: Based on user context, derive 2–3 **dramatically different** style directions. Each direction must differ from others in ≥ 2 of the 6 dimensions defined in `generate-project-variants.md` "Differentiation Mandate". Use AskUserQuestion to let the user confirm or adjust the directions.

2. **Generate independent brand CSS for each direction**: Each style gets its own `colors_and_type.css` file (named `colors_and_type-{direction-slug}.css`, e.g., `colors_and_type-minimal.css`, `colors_and_type-expressive.css`). The CSS files must reflect genuinely different design decisions across color system, typography, spacing/density, shape language, and shadow/depth — not just color swaps. Contrast dimension examples: see `generate-project-variants.md` "Differentiation Mandate".

3. **Generate pages per style in parallel**: For each style direction, dispatch page generation Sub-Agents using that direction's brand CSS. All pages across all styles are dispatched in the same round in parallel.

4. **Canvas organization**: Each style direction's pages are placed in a separate `group` value in the `.design` file, so they appear as distinct rows on the canvas for easy visual comparison.

> **[FORBIDDEN]** In multi-style exploration:
> - Generating the same layout with different colors (reskinning)
> - Using the same Hero/section structure across styles
> - Varying only surface parameters (radius, shadow) without structural changes
> - Generating more than 3 style directions (overwhelms comparison)

## Step 2 — Project Initialization + Canvas Entry → Main Agent direct execution

> **[FORBIDDEN] Delegating this step to Sub-Agents via the Task tool.** This step involves writing `.design` metadata and must be executed directly by the Main Agent in-context. The operations are trivial (mkdir + write 2-3 JSON files) and do not warrant a sub-task dispatch. Using the Task tool here wastes tokens and latency on Sub-Agent overhead for no benefit.

The Main Agent directly creates the directory structure, brand CSS file (if no Design Library), and `.design` entry file in one pass. This metadata initialization must not be delegated to Page Sub-Agents, because the Main Agent exclusively manages `.design` files.

> **[Note] Critical Format Constraints**: Format requirements for `data` field, `devMetadata` field, etc. are detailed in `shared-runtime/design-artifact-formats/design-project-file-format.md` JSON specification section.

> **[Architecture Critical]** The `.design` file created in this step **must contain all page skeleton nodes**. Page skeleton node IDs are pre-assigned by the Main Agent before dispatch using the `page-{slug}` format (derived from the HTML filename minus `.html` suffix, e.g., `pages/about-us.html` → `page-about-us`). Page Sub-Agents in Step 3 only generate HTML files and never write to `.design`, completely eliminating concurrent race conditions.

Before executing Step 2, the Main Agent must plan all pages and pre-assign:

| Field | Description |
|-------|-------------|
| `nodeId` | Format: `page-{slug}` (e.g., `page-index`, `page-pricing`, `page-about-us`). Slug is derived from the HTML filename minus `.html` suffix |
| `htmlSrc` | `pages/{slug}.html`, corresponding to the page filename |
| `title` | Page title — **must use the user's most frequently used language** (e.g., Chinese user → "首页", "产品介绍"; English user → "Home", "Products"). See `delivery-quality/user-facing-language-guidelines.md` "Artifact Naming Language Rule" |
| `pageIndex` | Logical sequence number, starting from 1 |

### Interaction-State Expansion

When the user requests interactions that change what the page visibly shows, the
Main Agent must expand each meaningful visual state into a separate canvas page
state before writing the `.design` skeleton.

**Trigger signals**:
- Tabs: "两个tab切换", "多个 tab", "tab1 为...", "tab2 为...", "第一个 tab",
  "第二个 tab", "tabs for ...", "switch between tabs"
- Search/filter/sort: "搜索后", "筛选后", "排序后", "选择条件后",
  "after search", "filtered state", "selected filter"
- Overlays: "打开弹窗", "弹窗初始态", "抽屉", "popover", "modal", "drawer"
- Disclosure/detail: "展开详情", "查看更多", "点击后展示", "选择后显示",
  "expanded state", "details open"
- Process/system states: "loading", "加载中", "empty", "空状态", "error",
  "错误态", "success", "提交成功", "step 1/2", "wizard"

**Behavior**:
1. Generate one page per meaningful visual state, even when the product concept
   sounds like a single screen. Example: "订单详情页，tab1 为订单信息，tab2 为订单数据图表"
   creates two pages: "订单详情页 - 订单信息" and "订单详情页 - 数据图表".
2. Keep state pages for the same source screen in the same `group` and adjacent
   logical order.
3. All state pages must share an identical page shell: outer frame size,
   header/sidebar/navigation, identity/summary area, control bar position,
   spacing, typography, radius, and brand treatment.
4. Only these areas may differ by state: active control styling, the stateful
   content region, overlay/drawer/modal layer, selected row/card, validation
   feedback, loading/empty/error content, chart/table content, and state-specific
   helper text.
5. Do not implement requested visual states only as internal JS in one HTML page.
   Canvas needs one visible page node for each requested visual state.
6. Register controls that switch between same-screen states as hidden
   interactions (`hideEdge: true`) so Preview can navigate between state pages
   without drawing extra canvas edges. Visible business-flow wiring should not be
   used for same-screen state switching.
7. In `runtime-orchestration-summary.json`, give state pages shared `continuityAnchors`
   that explicitly say "identical shell; only the active control/stateful region
   differs".
8. Keep lightweight hover/active/focus micro-interactions inside the same HTML
   page when they do not reveal persistent new content. Do not create extra pages
   for ordinary hover-only visual feedback.

**Overlay / Floating Layer State Rule** (Main Agent planning duties; Sub-Agent rendering rules in `shared-page-rendering-kernel.md` "Overlay / floating layer states"):
- For any floating layer (modal, drawer, popover, menu, command palette, toast detail, preview panel) opened on top of an existing page, plan a derived state page copied from the source/base page; the layer renders on top of the visible source context (transparent/translucent/blurred/dimmed backdrop per product style; opaque scrim only when the reference design uses one).
- Register the backdrop/scrim as a hidden interaction back to the source/base page (`hideEdge: true`) with a stable `data-dom-id` (e.g., `modal-backdrop-close`, `drawer-scrim-close`, `popover-outside-close`).
- Every dedicated close/cancel/back control inside the layer must also be registered as a hidden interaction to the source/base page; visual close icons without `data-dom-id` are not enough.
- A primary confirmation action that keeps the user in the same flow is registered per the planned target state: hidden interaction for same-screen state transitions, visible wiring only when it is the main business-flow next page.

#### Shared Shell Generation Protocol (Blocking)

State pages in the same interaction-state group are **not independent full-page
design tasks**. The Main Agent must make their shared shell explicit before
dispatch:

1. Create a stable `stateGroupId` for the source screen, choose one base/default
   state (`stateRole: "base"`), and mark all sibling states as
   `stateRole: "derived"` with `baseStatePageId`.
2. Write `sharedShellContract` and `mutableRegions` into each page record —
   the exact region inventories (immutable shell regions incl. outer `<main>`
   frame/wrapper/tab-bar geometry for tab/modal/overlay states; allowed mutable
   regions) are defined in `shared-runtime/orchestration-summary-contract/orchestration-summary-contract.md` field notes
   (`sharedShellContract` / `mutableRegions`).
3. Generate the shared state branch first, then generate the base state leaf,
   then generate derived state leaves. Derived state pages must start by copying
   the base HTML file byte-for-byte (or the existing source HTML for comparison
   state pages), then edit only the declared `mutableRegions`. [FORBIDDEN]
   Rebuilding a sibling state page from scratch, rerunning `apply-html-head-contract.mjs`
   for a derived state, or reassembling the full shell from fragments instead of
   copying the base page.
4. Pages with the same `stateGroupId` are not parallelizable until the base HTML
   and `sharedShellContract` exist. The normal flow is sequential
   `shared branch → base page → copy base → derived state edit`. Do not dispatch
   a derived state while the base page is still generating. If parallel
   Sub-Agents are unavoidable after the base exists, pass the base HTML path and
   immutable shell excerpts; each Sub-Agent must preserve those excerpts
   verbatim and may only edit declared slots.
   Derived-state Sub-Agent readiness (poll, copy, retry up to 10 times, then
   return `qualityGate: "blocked"`) is defined once and completely in
   `shared-page-rendering-kernel.md` Pre-step "Derived state pages: poll and copy
   the base HTML first".
   Only the Main Agent may dispatch the next node in this sequence. Sub-Agents
   must not dispatch child Sub-Agents; they only produce their assigned fragment
   or page and completion JSON. Parent completion / subtree wait gates: see
   SKILL.md §Architecture.
5. Same-screen state switching controls still use hidden interactions
   (`hideEdge: true`) so Preview can jump between state pages without drawing
   canvas edges.
6. For overlay/floating-layer derived states, include hidden return interactions
   for both the backdrop/scrim and every explicit close/cancel/back control,
   all targeting `baseStatePageId` with `hideEdge: true`.

Example: "订单详情页，tab1 为订单信息，tab2 为订单数据图表" creates
`订单详情页 - 订单信息` as the base page, copies it to
`订单详情页 - 数据图表`, and changes only the active tab and tab panel —
both pages keep the same shell (`<main>` padding/background, header/sidebar,
order summary, tab bar geometry, tab-panel wrapper); the tab switcher stays
attached to the tab panel through a shared content frame.

**Main Agent Direct Execution Checklist:**

1. ✅ Read `{SKILL_DIR}/shared-runtime/design-artifact-formats/design-project-file-format.md` (format reference)
2. ✅ Create directory structure: `{designProjectPath}/assets/`, `{designProjectPath}/pages/`
3. ✅ Write `{designProjectPath}/colors_and_type.css` (complete brand CSS from Step 1)
4. ✅ Run CSS semantic preflight once before any page dispatch:
   `node {SKILL_DIR}/shared-runtime/deterministic-tooling/apply-html-head-contract.mjs {designProjectPath}/colors_and_type.css {designProjectPath}/.preflight/preflight.html --title="Preflight" --lang=<lang> --prefix=<prefix>`. The command must exit `0` and generate `id="theme-vars"`, `id="semantic-token-fallback"`, `@theme inline`, Tailwind CDN, and `<html class="light|dark">`. A command that exits `0` but produces no `@theme inline` or no `semantic-token-fallback` is still a failed preflight. If preflight fails with missing semantic mappings, add the missing semantic aliases to `colors_and_type.css` once and rerun; do not inspect or patch page HTML because no page has been dispatched yet. After one retry, stop with the render-blocking error. Persist the result in `runtime-orchestration-summary.json.project.cssPreflightEvidence`; the `.preflight/` file is not a deliverable page.
5. ✅ Write `{designProjectPath}/{project-name}.design` — JSON with N page skeleton nodes. Set `config.autoLayout: true`, `config.deviceType` to the selected project device, and `config.projectName` to the user-facing project name on the first write. Set `config.designLibrary` to `null` or omit it; active Library projects must not use this workflow. Do not create an intermediate `.design` file without `config.deviceType`, and preserve the existing `config` object during later interaction/wiring updates.

**Operation mode**: CREATE (vs. UPDATE in edit-existing-project.md)

**Input data**:
- Project name: {name}
- Project path: {designProjectPath}
- Brand CSS source: CSS content = {complete CSS string from Step 1}, prefix = {prefix}
- Page list (pre-assigned by Main Agent in logical order):

| nodeId | title | htmlSrc | pageIndex |
|--------|-------|---------|-----------|
| page-{slug} | {title} | pages/{page-name}.html | 1 |
| ... | ... | ... | ... |

**Page skeleton node constraints**:
- `devMetadata.interactions` = `[]` (wiring in Step 3.5; interactions live under `devMetadata` per the `.design` Page Node template)
- `canvasData.x/y` = 0 (SDK autoLayout)
- pages/ directory empty at this point (expected)

[SKIP] Do NOT run validate-design-file-format.mjs here. Full validation in Step 4.

> **Next**: After Step 2 metadata initialization completes, write the orchestration summary, then proceed to Step 2.5 Image Pre-generation phase.

## Step 2.2 — Orchestration Summary → Main Agent direct execution

Before image pre-generation and page dispatch, the Main Agent must write `{designProjectPath}/runtime-orchestration-summary.json` following `{SKILL_DIR}/shared-runtime/orchestration-summary-contract/orchestration-summary-contract.md`.

### Mobile Visual Mockup Viewport Rule

When `project.deviceType === "mobile"` and the deliverable is an App/H5/mini-program visual mockup, every ordinary page must default to:

- `viewportMode: "document-scroll"`
- natural document flow (`body` may use `min-h-screen`, never forced `h-screen overflow-hidden`)
- no fixed-height outer phone frame or full-page `overflow-hidden` wrapper
- full canvas height: all page content must be visible on the design board

The Design SDK prototype preview already wraps mobile pages in a device frame and provides the fixed phone viewport. The generated HTML must not implement its own fixed outer viewport for ordinary mobile visual mockups.

[FORBIDDEN] Writing `sharedProjectShellContract.navigationShell` as "mobile app-shell mode" for ordinary mobile mockups; setting all mobile pages to `viewportMode: "app-shell"` merely because the product is an App; generating a project shell whose root clips content to one phone screen.

### Mobile Shared Navigation Contract

For multi-page mobile projects with shared bottom navigation, write `project.sharedProjectShellContract.mobileNavigation` before dispatch:

```json
{
  "applies": true,
  "type": "bottom-tab",
  "items": [
    { "key": "home", "label": "首页", "icon": "home" }
  ],
  "heightPx": 56,
  "position": "flow-bottom",
  "activeState": "primary icon+label color only; geometry stays identical",
  "structure": {
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
}
```

The ordered `items`, height, position, icon language, label visibility, and active-state geometry are binding for all ordinary sibling pages. Detail/modal/reward pages may omit this global navigation only when the page record or generation tree explicitly marks them as outside the shared mobile nav shell.

Derive `structure` once from `items.length`, `heightPx`, and `position`; do not hardcode a 5-tab / 60px / fixed-bottom layout unless those values are actually in this project contract. Every generated bottom-tab item must expose `data-nav-key="<item.key>"` using the exact key from `mobileNavigation.items`. `data-dom-id` is only for click wiring and must not be used as the active tab key; the current active tab may omit `data-dom-id` when it has no navigation action. The active state changes only `data-active` / color emphasis, never tab order, height, position, label wrapping, or geometry.

Before page dispatch, `intent-workflows/intent-project-complex-build/02-page-composition.md` generates `dispatchPreflightManifest` with `shared-runtime/deterministic-tooling/build-page-dispatch-manifest.mjs --mode=complex`. This phase only prepares the fields required by that script: `pages[]`, `designSource.cssFilePath`, brand prefix, `mobileNavigation`, `pages[].mobileNavigationActiveKey`, `cssPreflightEvidence`, `contextRequirementsLoaded[]`, `validationRunDiscipline`, `lowValueCallWatchdog`, `visualQualityCheckpoints[]` when required, and related packet fields. Do not hand-write `dispatchPreflightManifest` here.

Create a `project-shell` generation-tree node only when the shared region includes a header, sidebar, root body frame, shared body content, shared modal shell, or other shared structure beyond mobile bottom navigation. If the only shared region is bottom navigation, keep the generation tree leaf-only and use `mobileNavigation.structure.canonicalHtmlByKey`.

Before writing the summary, read `{SKILL_DIR}/skill-release-manifest.json` and write top-level `skillProvenance` exactly as defined in `shared-runtime/orchestration-summary-contract/orchestration-summary-contract.md`. If the version file is unavailable, set `version: null`, `version_source: "unknown"`, and `read_status: "missing"`.

Field schema and per-field requirements for `project` (including `designRead`, `designDials`), `designSource`, `pages[]` (including `visualNorthStar`, `compositionPattern`, `continuityAnchors`, `componentPlan`, `imagePlan`, `chartsRequired`, `miniProgramStyle`), `assets[]`, `wiringPlan[]`, and `hiddenInteractionPlan[]` are defined in `shared-runtime/orchestration-summary-contract/orchestration-summary-contract.md` "Required Schema" + field notes — do not re-derive them here. For this flow, set `project.operation` to `"create"`.

**Context passing rule**: Page Sub-Agents receive `orchestrationSummaryPath` and the current page record. Do not paste the full summary into every subtask when a path + filtered page slice is sufficient.

**Visual execution planning rule**: Before Step 3 dispatch, the Main Agent must ensure `project.designRead` and `project.designDials` exist; every page has `visualNorthStar`; every showcase / brand / landing page has `compositionPattern`; and every multi-page project has at least 2 shared `continuityAnchors` copied into each page record. This converts the broad aesthetic spec into a compact, page-specific execution brief.
