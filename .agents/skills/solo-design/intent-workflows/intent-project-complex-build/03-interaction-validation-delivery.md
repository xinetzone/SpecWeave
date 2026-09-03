## Step 3.5 — Consolidate Reports + Page Reordering + Wiring Registration + Persistence Confirmation (Main Agent, after all sub-tasks complete)

After all Sub-Agents complete, the Main Agent must execute the following operations in order:

For any project with more than one page, Step 3.5 is mandatory even for PPT, one-pager variants, reports, or static layout pages. Empty interaction arrays are allowed only when the page has no planned visible or hidden controls and this reason is explicitly recorded in the expected interaction checklist. Do not skip Step 3.5 merely because the pages are static.

### 3.5a — Consolidate domId lists reported by Sub-Agents

Collect information reported by all Sub-Agents and build an **expected interaction checklist** — one line per planned interaction in the form `{source page (htmlSrc)} → {domId} → {target page}`, with `[hideEdge=true]` appended for hidden entries (e.g., `Home (pages/index.html) → cta-products → Products page`; `Products (pages/product.html) → back-home → Home page [hideEdge=true]`).

This interaction checklist will be used for Step 3.5b persistence confirmation and passed to Step 4 script's `--require-interactions` parameter. If a Sub-Agent's reported domId list is inconsistent with the visible wiring map or hidden interaction plan (e.g., a page should have `cta-pricing` or `shortcut-blog` but Sub-Agent reported empty), the corresponding HTML must be fixed before proceeding.

### 3.5a-1 — Consolidate design intent and motion evidence

Collect all evidence fields defined in `shared-page-rendering-kernel.md` "Completion Report Fields" from every Sub-Agent completion JSON before writing final wiring, and verify them against that section's gate conditions. Create-flow emphasis:

1. Every page: non-empty `designIntentEvidence.visualNorthStarApplied`, `interactionStates`, `alignmentEvidence`, `headingCtaEvidence`, `motionEvidence`, and explicit `animationLibrariesUsed` (`[]` unless the Animation Library Exception in `shared-runtime/html-rendering-primitives/shared-html-rendering-primitives.md` applies).
2. Showcase / brand / landing pages: `compositionPatternUsed` non-empty and matching the page's `compositionPattern` unless the report explains a concrete business reason for deviation.
3. Multi-page projects: at least 2 `continuityAnchorsApplied` recur across pages (e.g., Header/Footer treatment, CTA style, surface layering, type rhythm).
4. `sourceContextPreserved`: `"not applicable"` is valid for ordinary new-project pages; comparison pages derived from an existing source page must name at least 3 preserved source-page elements.
5. `headInfrastructureStatus` and `fileMutationEvidence`: if any page reports missing head infrastructure, collect it for one Main Agent batch repair; if any page reports helper scripts created, treat that page as failed and retry or block per Step 3.1.
6. If any evidence is missing/generic, an unjustified animation library appears, or a page visibly falls back to an unplanned generic card wall → perform one targeted repair/regeneration with the missing visual fields emphasized. [FORBIDDEN] proceeding to Step 4 with missing completion evidence.

### 3.5a-2 — Batch head infrastructure repair before full validation

After all Sub-Agent completion JSON blocks return, collect pages where `headInfrastructureStatus.needsMainAgentReplaceHead === true`. Split them into chart pages and non-chart pages:

- Non-chart batch: `node {SKILL_DIR}/shared-runtime/deterministic-tooling/apply-html-head-contract.mjs <css-path> <page1.html> <page2.html> --replace-head --prefix=<brandPrefix>`
- Chart batch: `node {SKILL_DIR}/shared-runtime/deterministic-tooling/apply-html-head-contract.mjs <css-path> <chart-page1.html> <chart-page2.html> --replace-head --prefix=<brandPrefix> --charts`

Run at most these two batches before the first full scan. Do not add Chart.js to pages that do not use charts. If a page's chart requirement is unclear, use `runtime-orchestration-summary.json.pages[].chartsRequired` first; fall back to checking for `<canvas>` + `new Chart(` in the HTML only when summary data is missing.

If either batch fails with `CSS semantic theme mapping failed`, do not repair pages one by one. Repair `colors_and_type.css` once using the missing semantic mappings named by `apply-html-head-contract.mjs`, rerun the same batch once, and stop if it still fails.

### 3.5b — Atomic Reorder + Wiring Registration + Persistence Confirmation

> **All operations below are performed in a single pass to minimize context overhead and reduce the window for overwrites.**

1. **Read** the `.design` file **once**
2. **Reorder** page nodes by logical page order (homepage first, core business pages in the middle, contact/support pages last):
   - Follow common-sense page type ordering: Home/Landing → Core products/services showcase → Brand/About/Team → Contact/Support/FAQ
   - Only adjust positions in the `data` array; do not modify any field content of nodes (except interactions below)
   - `canvasData` x/y keep default value 0; the canvas SDK's `autoLayout` automatically calculates layout positions based on array order
3. **Register interactions** — traverse all page nodes, build a **page title → node ID** mapping, then populate `devMetadata.interactions` for each source page node based on the visible wiring map and hidden interaction plan:
   - Each wiring entry contains `domId` (corresponding to `data-dom-id` in HTML) and `targetPageId` (target page's node ID)
   - Hidden interaction entries must include `hideEdge: true`; they remain clickable in preview but do not draw visible canvas edges
   - Full rules in `intent-workflows/intent-project-complex-build/interaction-wiring-plan.md`
4. **Self-check before writing**: Verify each source page has ≤ 2 visible exits, total visible wiring count ≤ page count. Hidden interactions with `hideEdge: true` do not count as visible exits. If a source page has multiple visible entries pointing to the same target, merge into one (keep the most semantically strong domId). Do not merge away hidden interactions that correspond to distinct visible controls.
5. **Write back** to `.design` **once**
6. **Re-read once** to confirm ALL of the following:
   - Page node count in `data` array = expected page count (number of sub-tasks dispatched in Step 3)
   - Each domId in the expected interaction checklist exists in the corresponding page node's `devMetadata.interactions`
   - Each interaction's `targetPageId` points to an existing page node
7. Persist `runtime-orchestration-summary.json.project.wiringRegistrationEvidence` when a summary exists:
   ```json
   {
     "expectedDomIds": ["cta-products:index.html"],
     "allExpectedDomIdsRegistered": true,
     "missingDomIds": []
   }
   ```
8. **If any check fails** → the write was overwritten or did not take effect. Re-execute from step 1 of this sub-step once, then re-read once. If checks still fail, report the remaining errors and stop. [FORBIDDEN] to proceed to Step 4 without passing. Do not use full validation as the first way to discover expected interaction registration gaps.


## Step 4 — One-pass Complete Validation (Main Agent, Blocking — must not skip)

> **This step is blocking. After all Sub-Agents complete and before guiding the user to preview, the Main Agent must personally execute this validation. [FORBIDDEN] to proceed to Step 5 without passing validation.**

`runtime-orchestration-summary.json.project.validationRunDiscipline` must already exist before dispatch preflight. Before running validation, re-check that it still exists:

```json
{
  "maxFullValidationRuns": 2,
  "softWarningsTriggerRepair": false,
  "blockingRepairMode": "targeted-once",
  "forbiddenRepairTriggers": ["soft-warning-only", "provenance-warning-only", "style-warning-only"]
}
```

Use `validate-design-workspace.mjs` for one-pass complete validation, avoiding multiple tool calls:

```bash
node {SKILL_DIR}/shared-runtime/deterministic-tooling/validate-design-workspace.mjs <design-project-path> \
  --expected-pages=<N> \
  --require-interactions=<domId1>:<pageFile1>,<domId2>:<pageFile2>,... \
  --report-json=<design-project-path>/validation-report.json
```

- `<design-project-path>`: Design project root directory path
- `--expected-pages=<N>`: Total number of pages expected for this run (i.e., number of sub-tasks dispatched in Step 3)
- `--require-interactions`: Expected wiring checklist consolidated in Step 3.5a, formatted as comma-separated `domId:owningHTMLfilename` list, e.g., `cta-products:index.html,cta-pricing:product.html,cta-contact:pricing.html`; the script will simultaneously verify: whether the domId exists in the corresponding HTML file, and whether it has been registered in `.design`'s interactions
- `--report-json`: Required validation evidence file. Step 5 may proceed only when this file exists and contains `success: true`.

Manual Grep/Read checks, browser screenshots, or stdout-only validation are not substitutes for the report JSON. If any file is modified after a successful validation report, run this final scan again and overwrite the report JSON with the latest result.

**Mode-specific validation semantics**:

- Complex no-Library / layout-static path: repair only render-blocking errors from the report (`renderBlockingErrorCount > 0`). Soft warnings such as radius, shadow, secondary/accent, named colors, hardcoded colors, missing provenance, or missing generation tree must not trigger repair loops unless the selected workflow explicitly marks them blocking.

When exit code is 1, first check `validation-report.json.terminalState`. If it is present, report the blocking summary and stop. Otherwise follow the repair state machine in `delivery-quality/design-artifact-validation.md`: read `validation-report.json.repairActionTable[]` / `repairPlanHints[]`, read the selected repair workflow, record one lightweight repair entry, apply one owner-scoped batch repair, and run one revalidation. If revalidation still fails, report the remaining errors or reduced-scope decision and stop. Do not run a third full validation in this workflow.

If validation reports `[mobile-navigation-dispatch]`, missing `dispatchPreflightManifest`, or an invalid `dispatchPreflightManifest` shape, do not patch `runtime-orchestration-summary.json` after page generation. This means the Step 3 dispatch preflight was skipped or stale. Return to `intent-workflows/intent-project-complex-build/02-page-composition.md`, rerun `build-page-dispatch-manifest.mjs --mode=complex`, rebuild the affected Page Packet with the Mobile Navigation Contract, and dispatch again.

If the report contains 0 errors and only soft warnings in free-explore or layout-static mode, stop repairing and proceed. Do not chase warnings.

## Step 5 — Guide Preview (Main Agent)

### Finish Gate

Before producing the final response, all of the following must already be true. This gate must not trigger extra preview/browser work or an extra validation run by itself; it only blocks completion when required evidence is missing or stale.

- `validation-report.json` exists and records `success: true`.
- No page HTML, `.design`, CSS, or asset file was modified after the validation report was produced. Summary-only readiness evidence may be appended, but page content is frozen after successful validation. If a page/artifact file was modified, return to Step 4 and run the final scan once.
- `validate-finish-readiness.mjs <design-project-path> --check=all` passes. This checks `.design` page/image registration, page and asset paths, interaction targets, validation success, and post-validation mutation only.

Keep the textual summary link-free and rely on the host-rendered artifact entry for the `.design` file. Do not start a local preview server, browser session, or screenshot loop by default. Start preview only when the user explicitly asks, or when a blocking validation/repair decision genuinely requires visual evidence; if started, state the exit condition and keep it within the repair stop condition.

Since the canvas entry was already created in Step 2, the user can actually open the canvas at any time during page generation to view completed pages.

**Finish summary must not include manual links**, format specified in `delivery-quality/delivery-evidence-contract.md` "Artifact Declaration" section.

> **[NOTE] Preview screenshot is optional.** If using browser tools to take a screenshot, do NOT attempt to `Read` the screenshot PNG file (binary files cannot be read as text). The DOM snapshot from `browser_navigate` is sufficient for verification purposes.
