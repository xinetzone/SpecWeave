# Create Project — Complex HTML/Page Path

Use this workflow only after `SKILL.md route priority` routes the request to the complex HTML/page path.

This file is an execution manifest, not the full runbook. Before executing any phase, MUST read the corresponding phase runbook listed in the Phase Read Manifest below. Do not execute a phase from this manifest alone. Do not pre-read all phase runbooks unless the current request actually reaches those phases.

## Scope Guard

- If `intentProfile.caseFamily === "restore_1to1"` or `replicationMode === "high-fidelity"`, stop and use `intent-workflows/intent-page-restore-1to1/start-restore-1to1-project.md`.
- If active Design Library identity exists, stop and use `intent-workflows/intent-page-library-bound/start-library-bound-project.md`.
- If `intentProfile.caseFamily === "graphic_design"` with `graphicStrategy === "bitmap-first"`, invoke the `Skill` tool with `name: "solo-graphic-generation"` and stop this workflow.
- If the free-fast guard passes, stop and use `intent-workflows/intent-page-free-exploration/start-free-exploration-project.md`.
- Do not inherit restore, Library-bound, image-only, or free-fast shortcuts in this file.

Use this workflow when the user's intent is not associated with any existing design project and the request needs the full HTML/page pipeline: layout-static graphic design, multi-device split, long PRD parsing, fragment mode, multi-style exploration from scratch, complex interaction-state expansion, or generation-tree orchestration.

## Read Scope Contract

- `start-complex-project-build.md` is the route-locked entry manifest.
- Phase runbooks under `intent-workflows/intent-project-complex-build/*.md` are mandatory execution inputs for their phase.
- Read only the phase runbook needed for the current phase; do not pre-read all phase runbooks.
- `offset` / `limit` reads are exception recovery only, not the default execution strategy.
- If a future phase runbook exceeds the file-size gate, split that phase further instead of relying on segmented reads.

## Phase Read Manifest

| Phase | Must Read Before Executing | Execution Boundary |
| --- | --- | --- |
| Step 0.5-2.2 | `intent-workflows/intent-project-complex-build/00-requirement-and-style-intake.md` | Until project skeleton, `runtime-orchestration-summary.json`, `cssPreflightEvidence`, mobile navigation contract, and `generation-tree.json` are ready |
| Step 2.5 | `intent-workflows/intent-project-complex-build/01-graphic-asset-preparation.md` | Until image assets are generated/degraded and every asset file is registered as a `.design` image node |
| Step 3-3.1 | `intent-workflows/intent-project-complex-build/02-page-composition.md` | Until `dispatchPreflightManifest` is generated, Page Sub-Agents finish, and all page/shared-fragment reports are collected |
| Step 3.5-5 | `intent-workflows/intent-project-complex-build/03-interaction-validation-delivery.md` | Until wiring is registered, validation passes, and Design artifact readiness passes |

If a phase is skipped by the actual request, its runbook does not need to be read. If execution reaches a phase, reading that phase runbook is mandatory and is not an optional reference.

## Step Map

| Step | Owner | User-facing title | Runbook |
| --- | --- | --- | --- |
| Step 0.5 — Reference Material & Requirement Analysis | Main Agent | Understanding your requirements | `00-requirement-and-style-intake.md` |
| Step 0.7 — Style Discovery & Definition | Main Agent | Confirming creative direction | `00-requirement-and-style-intake.md` |
| Step 1 — Style Selection | Main Agent | Confirming design style | `00-requirement-and-style-intake.md` |
| Step 2 — Project Initialization + Canvas Entry | Main Agent | Preparing design project | `00-requirement-and-style-intake.md` |
| Step 2.2 — Orchestration Summary | Main Agent | Silent background | `00-requirement-and-style-intake.md` |
| Step 2.5 — Image Pre-generation | Main Agent + image subtasks | Preparing image assets for pages | `01-graphic-asset-preparation.md` |
| Step 3 — Page Generation | Main Agent + page subtasks | Designing pages | `02-page-composition.md` |
| Step 3.1 — Sub-Agent Failure Fallback | Main Agent | Silent background | `02-page-composition.md` |
| Step 3.5 — Page Reordering + Wiring Registration | Main Agent | Configuring page navigation | `03-interaction-validation-delivery.md` |
| Step 4 — One-pass Complete Validation | Main Agent | Silent background | `03-interaction-validation-delivery.md` |
| Step 5 — Guide Preview | Main Agent | Done, ready to preview | `03-interaction-validation-delivery.md` |

## Non-Negotiable Gates

- Canvas first: the Main Agent exclusively manages `.design` files.
- Page skeleton nodes are pre-registered before Page Sub-Agent dispatch.
- Sub-Agents do not write, append, reorder, or validate `.design`.
- Generated/kept image files under `assets/` must be registered as `.design` `type: "image"` nodes.
- Multi-page / multi-state work must materialize `generation-tree.json` before HTML generation.
- For mobile projects with shared bottom navigation, `sharedProjectShellContract.mobileNavigation.structure.canonicalHtmlByKey` must be prepared before Page dispatch.
- Before any Page Sub-Agent dispatch, `intent-workflows/intent-project-complex-build/02-page-composition.md` must run `shared-runtime/deterministic-tooling/build-page-dispatch-manifest.mjs --mode=complex`; `dispatchPreflightManifest` must prove required fields, including `mobileNavigation.canonicalHtmlIncluded` for ordinary mobile pages.
- Page dispatch packets must be assembled per `shared-runtime/agent-dispatch-runtime/lane-dispatch-index.md`.
- Final validation must write `validation-report.json` with `success: true` before artifact delivery.
- If validation reports `[mobile-navigation-dispatch]`, missing `dispatchPreflightManifest`, or invalid manifest shape, do not patch the summary after generation; return to the Step 3 dispatch-preflight gate and rerun from there.

## TodoWrite Efficiency Rule

- Create initial todo list once at start, max 7 items covering all steps.
- Update status using `merge=true` with only changed fields.
- Calling TodoWrite consecutively without an actual tool operation between them is forbidden.
- Batch status changes when multiple subtasks complete simultaneously.
- Total Main Agent TodoWrite calls must be <= 6. Page Sub-Agents must not call TodoWrite; their completion JSON is the status channel.
