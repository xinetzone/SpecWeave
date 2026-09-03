## Step 3 — Page Generation → Plan tree, generate shared fragments, then dispatch leaf sub-tasks

Before any `pages/*.html` file is generated, the Main Agent must build a
tree-shaped execution plan in `runtime-orchestration-summary.json.project.generationTree`.
The purpose is to prevent sibling pages from independently recreating the same
header/sidebar/body shell and drifting in color, radius, spacing, or content.

### Dispatch Preflight Gate (Main Agent, blocking)

Before any Page Sub-Agent dispatch, run the deterministic manifest builder:

```bash
node {SKILL_DIR}/shared-runtime/deterministic-tooling/build-page-dispatch-manifest.mjs {designProjectPath} --mode=complex
```

If the command exits non-zero, stop before Task dispatch and fix the missing `runtime-orchestration-summary.json` fields. Do not dispatch pages and do not ask Sub-Agents to infer missing fields.

After the command succeeds, read the updated `runtime-orchestration-summary.json` and verify `project.dispatchPreflightManifest[]` covers every planned page Task. For ordinary mobile pages with `sharedProjectShellContract.mobileNavigation.applies === true`, the corresponding manifest entry must prove `mobileNavigation.canonicalHtmlIncluded === true`.

Every manifest entry must include `allowedWritePaths[]`. Copy those paths into the Page Packet and require the Page Sub-Agent to return `changedFiles[]`. Do not mark a page dispatch completed until every changed file is inside the matching `allowedWritePaths[]`.

The current page's exact canonical nav block must come from `sharedProjectShellContract.mobileNavigation.structure.canonicalHtmlByKey[mobileNavigationActiveKey]` and be included in the Page Packet under `## Mobile Navigation Contract (MANDATORY)`. Do not ask Sub-Agents to invent or assemble bottom navigation.

[FORBIDDEN] Hand-writing or SearchReplace-patching `dispatchPreflightManifest` after validation. If validation later reports `[mobile-navigation-dispatch]`, missing `dispatchPreflightManifest`, or invalid manifest shape, the page dispatch already violated preflight; return to this gate and rerun from here.

### Step 3.0 — Generation Tree Planning (Main Agent, blocking)

Classify the requested pages/states into shared and private regions:

1. **Project shell**: regions shared by all pages, usually app frame, header,
   sidebar/top nav, footer, global background, brand CSS usage, type scale,
   radius scale, shadow model, and CTA treatment.
   For mobile visual mockups, the shared project shell may include visual app
   chrome (status bar, page header, bottom tab, safe-area spacers), but the shell
   root must remain vertically expandable on the canvas. Do not create a root
   `h-screen overflow-hidden` phone frame as the shared parent.
2. **Shared branches**: regions shared by a subset of pages. Examples: two tab
   states sharing an order summary and table frame; modal-open and base state
   sharing the whole underlying page; A/B pages sharing all content except one
   tab panel while C has a different body.
3. **Leaves**: final page/state files that only fill private regions or mutable
   slots declared by ancestors.

Write the complete tree before dispatch in two places:

1. `runtime-orchestration-summary.json.project.generationTree`
2. `{designProjectPath}/generation-tree.json`

`generation-tree.json` is the dispatch SSOT and must be an actual file, not
only agent memory or a completion report. It must be a nested tree with a
top-level `root` node and recursive `children[]` arrays. Do not use a flat
top-level `nodes[]` array as the SSOT. Each node must define `nodeId`, `kind`
(`project-shell` | `shared-branch` | `page-leaf`), `pageIds`, `output`,
`sharedRegions`, `privateRegions`, `mutableSlots`, `status` (`planned` |
`generated` | `blocked`), and `children`. Shared nodes output reusable
fragments under `{designProjectPath}/partials/`; leaves output
`{designProjectPath}/pages/*.html`. The exact JSON shape is defined in
`shared-runtime/orchestration-summary-contract/orchestration-summary-contract.md` "Required Schema" (`generationTree`).

The tree must be complete before any Task is dispatched: it must include every
planned page/state leaf, every shared branch, and every parent-child edge. A
tree with only `gen-project-shell` is incomplete for multi-page work and must
not proceed to page generation.

Example plan for pages A/B/C where A, B, and C share header/sidebar, while A
and B differ only in one tab panel:

```text
gen-project-shell (partials/project-shell.html: header + sidebar + root frame)
├── gen-ab-common (partials/ab-common.html: shared body except tab panel)
│   ├── gen-page-a (pages/a.html: tab A private panel)
│   └── gen-page-b (pages/b.html: tab B private panel)
└── gen-page-c (pages/c.html: C private body)
```

Dispatch order is dependency-based, not flat parallel:

1. Generate root `project-shell` fragment.
2. Generate each `shared-branch` fragment after its parent exists.
3. Generate leaf pages only after every ancestor fragment is complete.
4. Leaf siblings under the same completed parent may run in parallel.

[FORBIDDEN] Dispatching A/B/C page Sub-Agents independently when they share a
project shell or branch body. [FORBIDDEN] Allowing each leaf to invent its own
header/sidebar, card radius, brand color, shadow model, or shared body copy.

**Task batching rule (blocking)**: A parent generation-tree node and any of its
children must never be dispatched in the same assistant response / same
tool-call batch. Parent completion / subtree wait gates: see SKILL.md
§Architecture. Operationally, the Main Agent must:

1. Read `{designProjectPath}/generation-tree.json`, traverse from `root`, and
   dispatch only currently-ready child nodes whose parent path already has
   existing `output` files.
2. Wait for the Task result of every dispatched shared node.
3. Verify the declared `partials/*.html` file exists and update the node to
   `status: "generated"` in both `generation-tree.json` and
   `runtime-orchestration-summary.json.project.generationTree`.
4. Only then dispatch child shared nodes or leaf page nodes.

[FORBIDDEN] Passing `partials/project-shell.html` or any other inherited
fragment path to a leaf task before that file has been created. [FORBIDDEN]
Emitting a batch like `Task(project-shell), Task(page-a), Task(page-b)` in one
model turn. The correct sequence is `Task(project-shell)` → receive result →
verify file → read the nested tree → `Task(page-a), Task(page-b)` if both are
leaf siblings under the completed parent.

Shared fragments may include explicit mutable slots, for example `<!-- SLOT: activeNavItem -->`, `<!-- SLOT: pageTitle -->`, or `<!-- SLOT: tabPanel -->`. Leaves may fill only those slots and their own `privateRegions`. If a common region needs page-specific active styling, make that styling a slot; do not duplicate the whole common region.

**Active nav/tab protocol**: Parent fragments own the full header/sidebar/tab-bar
structure and active styling; leaf pages only fill the `activeNavItem` /
`activeTab` slot. Full slot rules (stable `data-nav-key` / `data-tab-key`,
`[data-active="true"]` styling, slot-only substitution): see
`shared-page-rendering-kernel.md` "Shared Input Data" Active nav/tab slot rule.

For Interaction-State Expansion pages, the state group must also appear in the
generation tree. Generate the base/common state as a shared parent, then derive
tab, loading, empty, error, modal, drawer, popover, and overlay leaves from it.

**Sub-Agents only generate HTML fragment/page files and do not write to
`.design`** — page nodes were pre-registered by the Main Agent in Step 2. Once
Sub-Agents complete HTML, they report back with `changedFiles[]`. If a Sub-Agent needs a Main-Agent-owned file (`.design`, runtime summary, validation report, or readiness evidence), it must return a blocked ownership request instead of writing the file.

> **Constraint Reading (Sub-Agent Direct Mode)**: Sub-Agents read constraint files directly per `shared-page-rendering-kernel.md` Phase 0 + Phase 1 protocol. Main Agent does NOT pre-read or digest these files — this complies with SKILL.md "Main Agent only reads orchestration-scope files" invariant.

> **Aesthetics Read (Direct Mode)**: Sub-Agents read `visual-experience/visual-experience-guidelines.md` directly during Phase 1a of `shared-page-rendering-kernel.md`. No pre-injection is needed — all aesthetic rules (tokens, typography, color, layout, imagery, accessibility, animation, state coverage, form validation) are consolidated in a single file (~634 lines, ~2500 tokens).

> **Restore out of scope**: high-fidelity / 1:1 restoration uses `intent-workflows/intent-page-restore-1to1/start-restore-1to1-project.md` and `intent-workflows/intent-page-restore-1to1/restore-1to1-page-runtime.md`. Do not assemble restore packets or restore evidence in this file.

> **Page Logical Order**: The Main Agent determined logical order when pre-assigning nodeIds in Step 2. When dispatching in Step 3, pass `nodeId` and `pageIndex` to the corresponding Sub-Agent — Sub-Agents do not need to generate IDs themselves.

> **Inter-page Navigation Wiring**: Before dispatching sub-tasks, the Main Agent must plan the **business flow path** between pages (i.e., the user's core browsing path), then pass both the "visible wiring mapping table" and the "hidden interaction table" to each Sub-Agent. **Default visible topology is linear single-chain** — pages connected head-to-tail in logical order (e.g., A→B→C→D), each page has exactly 1 visible exit. Only when the business flow itself branches is a page allowed 2 visible exits. [FORBIDDEN] Cycles in visible wiring topology — full DAG constraint, exit limits, hidden interaction rules, and topology rules in `intent-workflows/intent-project-complex-build/interaction-wiring-plan.md` "Map Principles". Sub-Agents, when generating HTML, must add `data-dom-id` attributes to all visible wiring controls and all hidden interaction controls. Full rules in `intent-workflows/intent-project-complex-build/interaction-wiring-plan.md`.

Sub-tasks are based on the shared template `{SKILL_DIR}/shared-runtime/agent-dispatch-runtime/shared-page-rendering-kernel.md`. **All shared dispatch fields are assembled per `shared-runtime/agent-dispatch-runtime/lane-dispatch-index.md`** (aesthetics mode selection, Library constraints block, free-explore color/shadow/typography policies, shared project shell contract, design read/dials, continuity anchors, generation tree contract, state group contract, comparison context, wiring/hidden interaction tables, image resources table, P0 alignment + heading/CTA checklists). Only **create-specific differentiated parameters** are listed below:

```
Task: Generate HTML page or shared fragment "{generation node name}"

Tool discipline:
  - Do not call TodoWrite. Sub-Agent completion JSON is the only status channel.
  - Do not create helper scripts. Write final artifact files or direct HTML patches only.
  - Do not start preview servers or browser sessions.
  - Do not run project validation scripts. The Main Agent runs validate-design-workspace.mjs after Sub-Agents complete.
  - Do not write or modify .design. Page nodes and interactions are owned by the Main Agent.

(Aesthetics mode note: select and include per lane-dispatch-index.md §1 based on operatingMode/replicationMode)

Output:
  - Leaf page task: {designProjectPath}/pages/{page-name}.html
  - Shared generation-tree node task: {designProjectPath}/partials/{fragment-name}.html
  ([FORBIDDEN] Do not write to .design file — page nodes were pre-registered by Main Agent in Step 2)
After completion, must report to Main Agent in JSON code block format (bare file paths or Markdown links are forbidden). Required fields: "nodeId", "page", "title", "domIds", "componentsRead", "extraComponentsRead", "aestheticsRead", "aestheticsSkipped", "nestingDepthCheck", plus every shared evidence field defined in shared-page-rendering-kernel.md "Completion Report Fields" ("designIntentEvidence", "interactionStates", "alignmentEvidence", "headingCtaEvidence", "motionEvidence", "sourceContextPreserved", "stateGroupId", "sharedShellPreserved", "generationNodeId", "inheritedFragmentsUsed", "privateRegionsGenerated", "sharedFragmentsPreserved", "htmlWriteMode", "headManagementEvidence", "headInfrastructureStatus", "fileMutationEvidence", "animationLibrariesUsed", "qualityGate").
Shared template: {SKILL_DIR}/shared-runtime/agent-dispatch-runtime/shared-page-rendering-kernel.md (pre-steps, constraint files, shared rules all in this file)
All shared dispatch fields: assemble per {SKILL_DIR}/shared-runtime/agent-dispatch-runtime/lane-dispatch-index.md, populated with this project's concrete values (never bare references like "keep same style")
Differentiated input (create-specific):
  - Node ID (nodeId): {ID pre-assigned in Step 2, e.g., page-pricing}
  - Page logical index (pageIndex): {sequence number starting from 1}
  - Page requirements: {user's description for this page}
  - Generation tree context: {current node plus ancestors; concrete values in the format of lane-dispatch-index.md §6}
  - State group contract: {concrete values in the format of lane-dispatch-index.md §7; only when this page belongs to Interaction-State Expansion, otherwise omit}
  - Visual north star / Composition pattern / Continuity anchors: {this page's values from orchestration-summary; composition pattern required for showcase / brand / landing pages; at least 2 shared anchors for multi-page projects}
  - Icon plan: {map every UI icon or visual marker to an image asset, Design Library SVG, Lucide icon name, inline SVG description, or emoji only when explicitly requested by the user; include whether emoji usage is explicit user intent}
  - Visible wiring mapping table + Hidden interaction table: {this page's rows only; format per lane-dispatch-index.md §10; omit empty tables}
  - Available image resources: {this page's rows plus shared assets only; format per lane-dispatch-index.md §11}
  - Reference Material Context / Long Requirement Context: {non-restore reference or long requirement context when applicable; restore-specific fields are out of scope for this file}
Additional notes:
  - [CRITICAL] Dispatch Format is Non-Negotiable: full assembly structure and prohibitions per lane-dispatch-index.md "Dispatch Assembly Checklist" + §12. If the full dispatch cannot be constructed (e.g., missing component plan), fall back to in-context generation (Main Agent generates HTML directly) rather than dispatching an unconstrained Sub-Agent.
  - [CRITICAL] Head write mode is mutually exclusive per page: SkeletonMainOnly (run apply-html-head-contract.mjs first, then edit only inside <main>) or FullHtmlReplaceHead (write full HTML first, then run apply-html-head-contract.mjs --replace-head). [FORBIDDEN] apply-html-head-contract.mjs skeleton → full-file Write. Derived state pages never run apply-html-head-contract.mjs — they poll-and-copy the base HTML per shared-page-rendering-kernel.md Pre-step. Full execution rules + CLI flag format + theme auto-inference: shared-page-rendering-kernel.md Pre-step.
  - Wiring rules detailed in intent-workflows/intent-project-complex-build/interaction-wiring-plan.md. Add data-dom-id in HTML for all entries in the visible wiring mapping table and hidden interaction table. Do not leave visible cross-page controls unregistered.
```

### Step 3.1 — Sub-Agent Failure Fallback

Follow `shared-page-rendering-kernel.md` "Sub-Agent Failure Fallback (Universal)" — retry once with the `[RETRY]` note; if the retry also fails (including no response or invalid/incomplete completion JSON), fall back to **in-context generation**: the Main Agent reads the 4 constraint files (`shared-runtime/agent-dispatch-runtime/sub-agent-runtime-boundaries.md`, `delivery-quality/page-rendering-quality-gate.md`, `shared-runtime/html-rendering-primitives/shared-html-rendering-primitives.md`, `{device}-html-rendering-primitives.md`) directly and generates the page HTML itself.
