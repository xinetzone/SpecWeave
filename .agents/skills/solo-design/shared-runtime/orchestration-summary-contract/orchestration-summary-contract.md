# Orchestration Summary Contract

`runtime-orchestration-summary.json` is the single runtime summary. This file owns shared schema only; lane details live in `intent-workflows/**/orchestration-summary-fields.md`.

## Required Top-Level Shape

Required roots: `schemaVersion`, `skillProvenance`, `project`, `designSource`, and `pages`.

Core `project` fields: `resolvedLane`, `intentProfile`, `selectedIntentWorkflowRead`, `contextRequirementsLoaded[]`, `contextReadScope`, `readScopeLedger[]`, `dispatchPreflightManifest[]`, `expectedDispatches[]`, `validationRunDiscipline`, `validationHistory[]`, `validationRepairLedger[]`, `validationSnapshot`, and `artifactReadinessEvidence`.

Flow-control fields added in `2026.07.11.0`: `lowValueCallWatchdog`, `sourceAuthorityLock`, and `visualQualityCheckpoints[]`.

`skillProvenance` is copied from `skill-release-manifest.json`: required `name/version/version_source`, optional `schema_version/release/read_status`. Manifest-read failure must be explicit: `{ "name": "solo-design", "version": null, "version_source": "unknown", "read_status": "missing" }`. Only provenance absence or version `<2026.07.08.0` may downgrade new lane-isolation fields to warnings; render and `.design` integrity remain hard failures.

## Lane Field Index

| Lane | Required owner file | Key fields |
| --- | --- | --- |
| `free_exploration` | `intent-workflows/intent-page-free-exploration/orchestration-summary-fields.md` | `resolvedLane`, `contextReadScope`, free packet evidence |
| `library_bound` | `intent-workflows/intent-page-library-bound/orchestration-summary-fields.md` | `libraryIdentity`, `actualTokenNameReference`, `tokenFidelity` |
| `restore_1to1` | `intent-workflows/intent-page-restore-1to1/orchestration-summary-fields.md` | `restoreVisualCheckpoints`, `referenceCaptureEvidence`, `expectedDispatches[]` |
| `graphic_bitmap_first` | `intent-workflows/intent-graphic-asset-generation/orchestration-summary-fields.md` | `graphicStrategyGate`, image asset records, image-node registration proof |
| `graphic_layout_static` | `intent-workflows/intent-project-complex-build/orchestration-summary-fields.md` | `graphicStrategyGate`, `layoutStaticRequired`, layout-static dispatch proof |
| `complex_html_page` | `intent-workflows/intent-project-complex-build/orchestration-summary-fields.md` | `generationTree`, `cssPreflightEvidence`, `mobileNavigation`, phase readiness |
| `existing_edit_add_comparison` | `intent-workflows/intent-project-mutation/orchestration-summary-fields.md` | `sourcePageId`, `derivationType`, `inPlaceEditAllowed`, `sourceProjectLaneHeritage` |
| `redesign_duplicate_project` | `intent-workflows/intent-project-mutation/orchestration-summary-fields.md` | `duplicateProjectPath`, redesign audit snapshot |
| `variants_multi_scheme` | `intent-workflows/intent-project-mutation/orchestration-summary-fields.md` | `variantAxis`, `expectedCount`, comparison grouping |
| `theme_customize` | `intent-workflows/intent-project-mutation/orchestration-summary-fields.md` | `changedDimensions`, `affectedPageRefreshList`, `noNewPageAssertion` |
| `image_asset_append` | `intent-workflows/intent-graphic-asset-generation/orchestration-summary-fields.md` | append mode, asset inventory, image-node registration proof |

## Dispatch Preflight Manifest

Page-dispatch lanes write `project.dispatchPreflightManifest[]` with one record per page task. Required row fields: `nodeId`, `htmlSrc`, `laneContract`, `sharedTemplate`, `supplementaryReads[]`, `allowedWritePaths[]`, and `forbiddenWriteRoots[]`.

Pure `graphic_bitmap_first`, pure `theme_customize`, and pure `image_asset_append` do not write page dispatch manifests unless their workflow explicitly converts to a page lane.

Page-dispatch lanes also write `project.expectedDispatches[]` before final lane validation. It must have the same length as `project.dispatchPreflightManifest[]`; each row requires `nodeId`, `packetType`, and `status`. Completed rows also require `changedFiles[]` and `toolCallLedger`. Allowed statuses are `completed` and `not_required`. Legacy `pageId` / `targetPageId` may be read by validators for compatibility, but new rows must use `nodeId`.

The Main Agent must compare `expectedDispatches[].changedFiles[]` against the matching `dispatchPreflightManifest[].allowedWritePaths[]`. Page Sub-Agents must never report or modify `.design`, runtime summary, validation report, readiness evidence, or final delivery files.

## Generalized Flow Control Fields

Field details for `contextRequirementsLoaded[]`, `sourceAuthorityLock`, `visualQualityCheckpoints[]`, and `lowValueCallWatchdog` live in `shared-runtime/orchestration-summary-contract/generalized-flow-control-fields.md`.

These fields are model-agnostic execution controls. They define preflight, source authority, visual checkpoints, and no-progress stop action; they must not encode model-specific behavior.

## Repair Evidence

When the repair stop condition is reached, record bounded incomplete evidence: `repairStopConditionMet`, `repairStopReason`, `remainingBlockingIssues[]`, and `lastValidationReportPath`.

## Write Rules

1. Main Agent writes the Step 0 lane gate after workflow start and before first Sub-Agent dispatch: `project.resolvedLane`, `project.selectedIntentWorkflowRead=true`, `project.contextRequirementsLoaded[]`, `project.contextReadScope`, `project.validationRunDiscipline`, and `project.lowValueCallWatchdog`.
2. Main Agent writes `.design` node registrations before page/image Sub-Agents can rely on them.
3. Page Sub-Agents return completion JSON only; they do not write this summary.
4. Summary fields must not copy full HTML, full task query, or full Design Library payloads. Store bounded evidence paths, hashes, or excerpts.
5. A lane may read another lane's result only through explicit fields such as `sourceProjectLaneHeritage`; it must not read the other lane's runbook.

## Audit Field Retention

Keep active gates compact; heavy audit material belongs in `validation-report.json` or script-owned reports.

Resident fields:

- `project.selectedIntentWorkflowRead` and `project.contextRequirementsLoaded[]`: pre-dispatch context proof.
- `project.validationHistory[]`: compact report summaries only.
- `project.validationRepairLedger[]`: compact repair proof only when a failed validation occurred.
- `project.ledgerDiagnosticReports[]`: keep the last three script-owned repair-ledger diagnostics; they are not validation attempts.
- `project.expectedDispatches[]`: compact page-dispatch completion ledger.
- `project.deliverableCompletenessChecklist`: graphic layout-static only.
- `project.sourceAuthorityLock`: restore/reference-driven visual authority split.
- `project.visualQualityCheckpoints`: layout-static and visually critical checkpoint ledger.
- `project.lowValueCallWatchdog`: no-progress stop action for page-dispatch workflows.

Archivable or report-owned fields:

- `project.validationSnapshot.hashes`: prefer `validation-report.json.projectFileHashes`; do not duplicate full hash maps in summary unless a runtime step explicitly needs them.
- completed historical `readScopeLedger[]` entries can be compacted after manifest build and validation. It records declared read scope only, not actual tool-call behavior.
- old `validationHistory[]` entries beyond the current failure/revalidation chain can be compacted to `{count, lastFailedAt, lastSuccessAt}`.

Any summary field intended for Sub-Agent consumption must remain bounded. Do not pass full `runtime-orchestration-summary.json` to Page Sub-Agents; pass the current Page Packet plus declared slices.

## Validation Ownership

- `validate-lane-runtime-contract.mjs` checks lane-level summary completeness and resolved lane normalization.
- `build-page-dispatch-manifest.mjs` creates page dispatch preflight records only after lane preflight succeeds.
- `validate-design-workspace.mjs` and `validate-graphic-asset-design.mjs` check artifact/render validity and apply severity policy from `delivery-quality/lane-severity-matrix.md`.
