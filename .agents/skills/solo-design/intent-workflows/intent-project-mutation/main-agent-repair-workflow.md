# Main Agent Repair Flow

> **Audience**: Main Agent ONLY. This file is read by the Main Agent during the post-generation validation/repair phase when a Quality Gate fails. Sub-Agents must NOT read, interpret, or execute anything in this file.

---

---

## [MANDATORY] Batch Repair Protocol — Anti Repair Loop

> This rule takes priority over all individual repair strategies below. Violating this rule causes repeated repair loops and unstable artifacts.

### Step 0: Readiness and Stop Condition

If you are about to repair a validation error, `record-validation-repair-entry.mjs` must already have been run on the failed `validation-report.json`, and this file must already have been read. Do not start by editing files, reading validator source, `apply-html-head-contract.mjs` source, or full HTML files.

```bash
node {SKILL_DIR}/shared-runtime/deterministic-tooling/record-validation-repair-entry.mjs \
  {designProjectPath} \
  --phase=start \
  --failed-report={designProjectPath}/validation-report.json
```

Before any repair action, record this evidence checklist in the Main Agent's working notes and append it to `runtime-orchestration-summary.json.project.repairEntryEvidence[]` when the summary exists:

```json
{
  "repairPolicyRead": true,
  "renderBlockingErrorPresent": true,
  "softWarningOnly": false,
  "ownerClassified": true,
  "postValidationMutationDetected": false,
  "validationErrorClasses": [],
  "repairStopCondition": {
    "validationRunsSoFar": 1,
      "maxValidationRuns": 2
  },
  "recorded_at": "ISO-8601 timestamp"
}
```

Before editing any file, answer these four questions from the validation report, not from broad source exploration:

1. Is there a render-blocking error, or are these only soft warnings?
2. Is the owner Main Agent (`.design`, wiring, head infrastructure) or Sub-Agent (`<main>` content only)?
3. If `apply-html-head-contract.mjs --replace-head` is needed, will it preserve `<main>` and avoid body regeneration?
4. Has the same error key already failed twice after targeted repair? If yes, stop and report the blocking errors instead of continuing.

Repair prompts and repair reasoning may include only:

- validator/report summary
- affected file paths
- owner classification
- at most 80 lines of targeted excerpt per affected file

[FORBIDDEN] Re-reading complete HTML files, full validator scripts, or full `apply-html-head-contract.mjs` source repeatedly to fix the same class of error.

If `validation-report.json.repairActionTable[]` exists, select the row matching the current blocking error and follow its `action` and `sourceReadPolicy` before any file read. Record the selected row through the repair ledger script before editing:

```bash
node {SKILL_DIR}/shared-runtime/deterministic-tooling/record-validation-repair-entry.mjs \
  {designProjectPath} \
  --phase=action \
  --failed-report={designProjectPath}/validation-report.json \
  --owner=main-agent \
  --error-class=<repairActionTable.errorClass> \
  --action=<deterministic-action-name> \
  --affected-files=<comma-separated-relative-paths>
```

When the action is `return_to_dispatch_preflight_gate`, stop page repair and rerun the owning preflight phase; do not patch generated files to compensate for a skipped preflight.

If the summary cannot be updated before repair, stop and report the blocker. Missing repair entry evidence is a process violation even when the repair succeeds.

### Low-Value Call Watchdog

During repair and finish phases, if a reasoning span produces no tool call, no artifact diff, and no structured decision, follow `runtime-orchestration-summary.json.project.lowValueCallWatchdog.noProgressNextAction`.

Default action: enter Design artifact readiness if validation is already successful; otherwise stop with the smallest blocking summary from the latest validation report. Do not continue a thinking loop to look for additional optional improvements.

### Step 1: Infrastructure First

When `validate-design-workspace.mjs` reports infrastructure failures (theme-vars / Tailwind CDN / @theme / @layer base / html class), **immediately batch-run `apply-html-head-contract.mjs --replace-head`** on ALL failed HTML files in a single RunCommand:

```bash
# Fix all pages at once (not one by one)
for file in {designProjectPath}/pages/*.html; do
  node {SKILL_DIR}/shared-runtime/deterministic-tooling/apply-html-head-contract.mjs {designProjectPath}/colors_and_type.css "$file" --replace-head --lang={lang} --prefix={prefix}
done
```

**[FORBIDDEN]** Manually fixing infrastructure issues with Read/Grep/sed/Write without running apply-html-head-contract.mjs first.

If `apply-html-head-contract.mjs` fails with `CSS semantic theme mapping failed`, or if the command exits `0` but validation still reports missing `@theme inline` / `semantic-token-fallback`, the broken input is `colors_and_type.css`, not the individual page HTML. Add the missing semantic aliases to `colors_and_type.css` once, then rerun the same batch once. In free-explore mode, the aliases must map to the existing primary/neutral/state tokens and must not introduce `secondary` or `accent` brand hues. Do not inspect or rewrite pages one by one for this failure class.

`apply-html-head-contract.mjs` argument contract:

| Allowed | Forbidden |
| --- | --- |
| Positional `<css-path> <html-file...>` | `--css`, `--brand-css`, `--device`, `--output` |
| `--replace-head` | swapping CSS and HTML arguments |
| `--prefix=<brandPrefix>` | running `--help` as a repair strategy |
| `--lang=<language>` |  |
| `--charts` only for chart pages | editing generated `<head>` manually before script repair |

The script replaces `<head>` only. It must preserve the current `<main>` body; if the body is missing after repair, treat that as a repair failure and stop rather than regenerating repeatedly.

### Step 2: Re-validate Once

Run `validate-design-workspace.mjs` once with `--report-json` to verify, then record the revalidation report:

```bash
node {SKILL_DIR}/shared-runtime/deterministic-tooling/record-validation-repair-entry.mjs \
  {designProjectPath} \
  --phase=revalidate \
  --revalidation-report={designProjectPath}/validation-report.json
```

If revalidation still fails, or if `validation-report.json.terminalState` is present, rerun the same command with `--blocked-reason=<short reason>` and stop. Do not start a second repair batch.

### Step 3: Warning-Only = Done

If Step 2 results contain only warnings (0 errors), **complete the task immediately**. Do NOT start repair loops for warnings. Warnings are aesthetic suggestions, not blocking issues.

### Step 4: Remaining Errors = Batch Fix

If errors remain after the initial validation and before the single allowed repair batch, **read all affected files at once**, **batch-fix all issues in a single response**, then **run one revalidation**.

**[FORBIDDEN]** Serial "fix one → validate → fix next" loops.
**[FORBIDDEN]** More than 2 total validation runs. If errors persist after the second validation, keep the current version, inform the user of the remaining blocking errors, and do not claim the task is complete.

### Dispatch Evidence Failures Are Not Post-Generation Repairable

If validation reports `[mobile-navigation-dispatch]`, missing `dispatchPreflightManifest`, or an invalid `dispatchPreflightManifest` shape, do not patch `runtime-orchestration-summary.json` after page generation with Grep/SearchReplace. This means the pre-dispatch manifest script was skipped or failed.

Dispatch completion evidence and post-dispatch mutation evidence are process-owned JSON fields. Do not hand-edit `project.expectedDispatches[]`, `project.mainAgentPostDispatchMutations[]`, `toolCallLedger`, or `changedFiles[]` with Grep/SearchReplace/sed. Use the deterministic recorder only:

```bash
node {SKILL_DIR}/shared-runtime/deterministic-tooling/record-dispatch-completion.mjs {designProjectPath} --node-id=<page-id> --status=completed --changed-files=<comma-separated-files> --trace-digest=<trace-digest> --tool-ledger-json='<json>'
```

If the real completion JSON or trace digest is missing, stop and report the process error. Do not invent dispatch evidence to make validation pass.

Correct action: stop and report the process error. The next run must execute:

```bash
node {SKILL_DIR}/shared-runtime/deterministic-tooling/build-page-dispatch-manifest.mjs {designProjectPath} --mode=free-fast
```

or, for complex create flows:

```bash
node {SKILL_DIR}/shared-runtime/deterministic-tooling/build-page-dispatch-manifest.mjs {designProjectPath} --mode=complex
```

before dispatching Page Sub-Agents. Do not repair this error class after pages have already been generated.

### Mobile Navigation Consistency Repair

If remaining errors include `[mobile-navigation-consistency]`, do not repair with Grep/SearchReplace and do not patch individual `span`, `data-dom-id`, `svg`, or class fragments.

Run the deterministic script exactly once:

```bash
node {SKILL_DIR}/shared-runtime/deterministic-tooling/repair-mobile-navigation-flow.mjs {designProjectPath} --report-json={designProjectPath}/mobile-nav-repair-report.json
```

Then run one final `validate-design-workspace.mjs`. If the script fails, if `mobile-nav-repair-report.json.success === true` already existed before the attempt, or if validation still reports `mobile-navigation-consistency`, stop and report the remaining blocking errors. Do not run the script again and do not fall back to manual per-page nav edits.

Optional browser preview or screenshot-based visual repair must follow the same stop condition. Do not start an open-ended visual polishing loop; state the exit condition before using browser preview for repair.

## Restore 1:1 Repair Policy

When `runtime-orchestration-summary.json.project.intentProfile.caseFamily === "restore_1to1"`, repair must preserve `restoreVisualCheckpoints`.

Allowed repair:

- Missing file or invalid `.design` JSON
- Missing head infrastructure
- Render-blocking CSS/JS error
- Missing persisted restore evidence copied from a valid Sub-Agent completion

Forbidden repair:

- Broad redesign
- Style polishing after validation has passed
- Replacing the page with a generic app/site layout
- Changing checkpoint-covered layout, color, density, typography, or component proportions without a recorded `allowedDeviationList`
- Re-running source capture only to populate evidence fields

Before any restore repair, map the failed validation item to exactly one render-blocking invariant or one restore checkpoint. If the repair would alter a high-priority checkpoint, stop and report the blocking reason instead of silently changing the visual contract.

## Visual Preview / Screenshot Repair Stop Condition

After `validate-design-workspace.mjs` passes with 0 render-blocking errors:

- Do not start browser preview or screenshot-based visual polishing by default.
- Browser preview is allowed only when:
  1. the user explicitly requests direct browser preview, or
  2. there is a concrete render-blocking visual suspicion that cannot be resolved from validation output, such as blank page, severe overflow, missing critical image, or runtime style collapse.
- At most 1 preview pass and 1 screenshot set are allowed per task.
- If preview reveals only subjective style preferences or soft warnings, stop and complete.
- Do not run screenshot → edit → screenshot loops for polish.
- Do not use TodoWrite for visual preview micro-steps.

If visual repair is performed, state the exit condition before starting and record:

- `previewReason`
- `previewPassCount`
- `visualIssueClass`
- `repairAction`

## Repair vs Regenerate Decision

> When Step 3/4 Validation detects Quality Gate failures, the Main Agent uses this decision table to choose between repair (cheap) and regeneration (expensive). This operates at the Main Agent level and does NOT change Sub-Agent self-check behavior.

| Failure Type | Detection Method | Strategy | Executor |
|-------------|-----------------|----------|----------|
| Gate 1: Hardcoded colors | Search for `#[0-9a-fA-F]{3,8}` or `rgb(` within `<main>` element's style/class attributes | **Auto-repair**: batch-replace with nearest `var(--{prefix}-xxx)` | Main Agent |
| Gate 2: Head structure broken | `<style id="theme-vars">` or Tailwind CDN missing | **Script repair**: re-run `apply-html-head-contract.mjs <css-path> <html-file> --replace-head` | Main Agent |
| Gate 2: Mixed head write mode | Completion lacks `htmlWriteMode` / `headManagementEvidence`, or page ran skeleton then full-file Write | **Mode repair**: preserve current `<main>`, run `apply-html-head-contract.mjs --replace-head`, then report `htmlWriteMode: "FullHtmlReplaceHead"`; future edits must use `<main>`-only edits | Main Agent |
| Gate 4: Responsive missing | Entire page has no `sm:`/`md:`/`lg:` breakpoint classes | **Regenerate**: re-dispatch Sub-Agent with emphasized "Responsive Layout is mandatory" | Sub-Agent |
| Gate 5: Image path error | `src` does not start with `../assets/` | **Auto-repair**: fix path prefix via Edit tool | Main Agent |
| Gate 7: AI Slop visuals | Blue-purple neon gradients, rainbow effects detected | **Regenerate**: re-dispatch + explicitly forbid the detected pattern in soulElement | Sub-Agent |
| Gate 7.5: Bilingual title mixing | Both Chinese and English phrases (> 2 words) used as headings/labels on same page | **Auto-repair**: replace all foreign-language headings/labels with primary language equivalents | Main Agent |
| Gate 7.5: Component overlap | Absolutely positioned elements lacking explicit non-overlapping offsets, or positioned badge sharing space with text per `delivery-quality/visual-blocker-rules.md` ❷ | **Auto-repair**: add `gap-*` spacing or adjust positioned element offsets | Main Agent |
| Gate 7.5: Oversized heading | Heading with > 8 CJK chars / > 6 English words at any size ≥ `text-xl`, or heading wrapping 2+ lines | **Auto-repair**: reduce heading font-size class to `text-2xl` or `text-xl`, or extract a shorter noun phrase | Main Agent |
| Gate 7.5: Button text wrapping | Button text lacks `whitespace-nowrap` or renders multi-line | **Auto-repair**: add `whitespace-nowrap` + reduce font-size if needed | Main Agent |
| Gate 7.6: Visual primitive violation | Divider, border, outline, stroke, separator, or static shadow uses `currentColor`, hardcoded high-contrast colors, browser-default high-contrast strokes, or lacks an explicit token/semantic-variable source | **Targeted repair**: change only the primitive source to a Design Library token, semantic CSS variable, or approved semantic border/divider token; do not rewrite unrelated layout, content, imagery, or component structure | Main Agent |
| Gate 7.6: Layout geometry violation | Buttons, tags, form controls, card titles, list rows, table/toolbars, or nav items lack a shared left/right/center/baseline alignment; primary rows/lists/cards/forms rely on `absolute` positioning; a tiny element floats alone in a full-width row with arbitrary padding/margin | **Targeted repair**: choose one layout mode and alignment axis per region, normalize gaps, remove arbitrary offsets/primary-layout absolute positioning, and either complete orphan rows with related content or align/collapse them into the neighboring row | Main Agent |
| Gate 7.6: Sentence heading or long CTA | Heading is a full sentence/clause, heading exceeds the limits in `delivery-quality/visual-blocker-rules.md` ❸, or CTA/button/tab/pill contains a long requirement phrase | **Targeted repair**: extract a short noun phrase heading, move explanatory text to body/subtitle, and shorten CTA/button/tab/pill labels to 2-6 CJK chars or 1-3 English words | Main Agent |
| Gate 10: Mini program chrome incomplete | Detect empty right capsule, missing more/close action, invisible spacer, or brand-styled system chrome in miniProgramStyle pages | **Auto-repair**: replace the nav bar with the standard mini program nav snippet from `shared-runtime/html-rendering-primitives/mobile-html-rendering-primitives.md` | Main Agent |
| Gate 11: Composition pattern missing | Missing `designIntentEvidence.compositionPatternUsed`, or showcase page does not name the planned pattern | **Targeted repair**: preserve content, rebuild first-screen composition around the planned pattern | Sub-Agent |
| Gate 11: Default card wall | Manual judgment: generic hero plus repeated feature cards without business-specific composition | **Regenerate**: re-dispatch with explicit `compositionPattern` and anti-card-wall instruction | Sub-Agent |
| Gate 11: Cross-page style drift | Multi-page report shares fewer than 2 continuity anchors | **Targeted repair**: align Header/Footer, CTA style, surface layering, or type rhythm | Main Agent |
| Gate 11: Project shell drift | Pages ignore `sharedProjectShellContract` or diverge in nav/header/sidebar/footer, primary color, font stack, radius scale, shadow model, CTA style, or alignment rhythm | **Targeted repair**: copy the strongest shell implementation to sibling pages, then reapply only page-specific content | Main Agent |
| Gate 11: Active nav/tab drift | Leaf pages rewrite shared header/sidebar/tab DOM or CSS to mark active state, or shared nav/tab items lack stable `data-nav-key` / `data-tab-key` plus a slot-driven active state | **Targeted repair**: move nav/tab structure and active CSS into the parent fragment, add stable keys, expose `activeNavItem` / `activeTab` slot, and make leaves fill only that slot | Main Agent |
| Gate 11: Generation tree violation | Missing `generationTree` for multi-page/state work, missing `generation-tree.json`, flat top-level `nodes[]`, root-only/incomplete tree, parent and child tasks launched in the same batch, child dispatched before parent completion/status update/output file, parent branch summarized before all children finished, Sub-Agent attempted to dispatch child Sub-Agents, leaf task missing inherited fragments, leaf regenerated or duplicated a shared region, or sibling leaves differ outside declared slots/private regions | **Targeted repair**: write/repair complete nested `generation-tree.json`, mirror it into orchestration summary, generate/repair ancestor fragment first, verify the fragment file exists, mark the parent generated, dispatch child nodes from the Main Agent, then wait/poll until every descendant completion and output file exists before consolidation; reapply only declared mutable slots/private regions | Main Agent |
| Gate 11: State shell drift | Pages with the same `stateGroupId` differ outside declared `mutableRegions`, derived page was rebuilt from scratch, outer `<main>` style/class differs, tab/control bar is detached from the panel frame, or panel wrapper padding/background/border drifts | **Targeted repair**: poll for the base page HTML, copy it to the derived target, then reapply only active-control and mutable-region changes; preserve `<main>`, content wrapper, shared header/summary/tab frame byte-for-byte where possible. Do not run `apply-html-head-contract.mjs` for the derived target | Main Agent |
| Gate 11: Derived base copy missing | Derived page report lacks `derivedFromHtmlSrc`, lacks copy evidence, contains `apply-html-head-contract.mjs` execution evidence, or returned `missing base state html after retry` | **Readiness repair**: generate/finish the base state first, verify the base HTML file exists, then re-dispatch the derived task with poll-and-copy as its first step | Main Agent |
| Gate 11: Floating layer missing close wiring | Modal/drawer/popover page lacks backdrop or close/cancel/back `data-dom-id` entries targeting the source/base page with `hideEdge: true` | **Targeted repair**: add hidden interaction entries and matching HTML `data-dom-id` attributes | Main Agent |
| Content mismatch (major deviation from requirements) | Manual judgment | **Regenerate**: re-dispatch with more explicit content specification | Sub-Agent |

## Color Hardcode Auto-Repair Strategy

When Gate 1 detects hardcoded colors, the Main Agent repair flow:

1. Read `runtime-orchestration-summary.json` → `designSource.actualTokenNameReference` for the complete HEX→variable mapping
2. For each hardcoded color value, find the nearest token variable:
   - Exact match → direct replacement
   - No exact match → choose the closest hue match among primary/secondary/accent/muted variables
3. Execute batch replacement using Edit tool
4. Re-validate Gate 1 after replacement
5. **Scope limitation**: Only replace within `<main>` content. [FORBIDDEN] touching `<svg>` internal fill/stroke values (these may be intentionally hardcoded for icon rendering)

## Repair Attempt Limits

- Maximum 1 auto-repair attempt + 1 regeneration attempt per page
- If regeneration still fails, keep current version and inform user of remaining issues in progress message
- [FORBIDDEN] Infinite retry loops

## Image Generation Failure Policy

> Executor: Main Agent (images are pre-generated by the Main Agent; Sub-Agents never generate or retry images). Sub-Agents only consume the resulting asset records and render the approved CSS degradation for `degraded` assets — see `shared-runtime/agent-dispatch-runtime/sub-agent-runtime-boundaries.md §Image-Failure-Degradation`.

When image generation encounters errors (504 timeout, service unavailable, rate limiting, etc.):

| Failure Scenario | Required Action |
|------------------|-----------------|
| Single image fails after 1 retry | Abandon that image; mark the asset `degraded` (Sub-Agent renders CSS fallback) |
| ≥ 2 images fail in the same batch | Stop retrying all remaining images; degrade ALL planned images to CSS alternatives |
| Service returns non-200 after retry | Do NOT retry more than once per image; proceed with degradation |

- [FORBIDDEN] Retrying the same image more than once (wastes 30-40s per attempt with high re-failure probability)
- [FORBIDDEN] Blocking page generation while waiting for image retries
- After degradation, keep the asset record with `status: "degraded"` in `runtime-orchestration-summary.json` and the "Available image resources" table so Sub-Agents can render the approved CSS fallback for that slot

## Image Generation Prompt Constraints

> Executor: Main Agent (image pre-generation phase).

- The prompt must include `no text, no typography, no letters, no words, no colorful lights, no neon glow, no blue purple light, no light trails, no holographic effect, no gradient lighting`.
- The prompt must NOT include `no watermark` or `no logo` — these phrases prime the model to hallucinate issues that don't exist.
- After image generation, use directly — **any secondary processing of images is forbidden** (including cropping, watermark removal, resizing, regeneration, deletion, or re-generation). If `GenerateImage` returns success, the image is unconditionally accepted; the Agent cannot "see" image content and must trust the tool's confirmation.
