# Lane Dispatch Index

This file is the shared dispatch index for `solo-design`. It defines how Main Agent chooses a lane-owned dispatch contract and the common fields that every Page Sub-Agent packet may share.

It is not a workflow and must not duplicate lane-owned dispatch schemas. Detailed required/forbidden fields live in `intent-workflows/**/**/*dispatch-contract*.md`.

## Dispatch Contract Selection

| `resolvedLane` / mode | Packet | Page runtime guide | Contract |
| --- | --- | --- | --- |
| `free_exploration` | `FreePagePacket` | `intent-workflows/intent-page-free-exploration/free-exploration-page-runtime.md` | `intent-workflows/intent-page-free-exploration/dispatch-contract.md` |
| `restore_1to1` | `RestorePagePacket` | `intent-workflows/intent-page-restore-1to1/restore-1to1-page-runtime.md` | `intent-workflows/intent-page-restore-1to1/dispatch-contract.md` |
| `library_bound` | `LibraryBoundPagePacket` | `intent-workflows/intent-page-library-bound/library-bound-page-runtime.md` | `intent-workflows/intent-page-library-bound/dispatch-contract.md` |
| `graphic_layout_static` | `GraphicLayoutPagePacket` | `intent-workflows/intent-project-complex-build/graphic-layout-page-runtime.md` | `intent-workflows/intent-project-complex-build/graphic-layout-dispatch-contract.md` |
| `complex_html_page` | `ComplexPagePacket` | `intent-workflows/intent-project-complex-build/complex-page-runtime.md` | `intent-workflows/intent-project-complex-build/complex-page-dispatch-contract.md` |
| `existing_edit_add_comparison` | `ExistingEditPagePacket` | `intent-workflows/intent-project-mutation/existing-edit-page-runtime.md` | `intent-workflows/intent-project-mutation/existing-edit-dispatch-contract.md` |
| `redesign_duplicate_project` | `RedesignPagePacket` | `intent-workflows/intent-project-mutation/redesign-page-runtime.md` | `intent-workflows/intent-project-mutation/redesign-dispatch-contract.md` |
| `variants_multi_scheme` | `VariantPagePacket` | `intent-workflows/intent-project-mutation/variant-page-runtime.md` | `intent-workflows/intent-project-mutation/variant-dispatch-contract.md` |

Pure `graphic_bitmap_first` work is owned by `Skill: solo-graphic-generation` and must not enter this page-dispatch runtime. The `theme_customize` lane may not build page dispatch manifests unless its owning workflow explicitly converts into a page-dispatch lane.

## Common Packet Fields

Every page packet may include:

```json
{
  "laneContract": {
    "resolvedLane": "free_exploration",
    "packetType": "FreePagePacket",
    "pageRuntimeGuide": "intent-workflows/intent-page-free-exploration/free-exploration-page-runtime.md",
    "dispatchContract": "intent-workflows/intent-page-free-exploration/dispatch-contract.md"
  },
  "nodeId": "page-index",
  "htmlSrc": "pages/index.html",
  "title": "Home",
  "deviceType": "web|mobile|tablet",
  "viewportMode": "document-scroll|app-shell",
  "cssPath": "colors_and_type.css",
  "brandPrefix": "brand",
  "fillHtmlHeadCommand": "node {SKILL_DIR}/shared-runtime/deterministic-tooling/apply-html-head-contract.mjs ...",
  "pageType": "showcase|information-dense|task-driven|fragment",
  "qualityRisks": [],
  "assets": [],
  "domIdsRequired": [],
  "supplementaryReads": [],
  "allowedWritePaths": ["pages/index.html"],
  "forbiddenWriteRoots": [
    "*.design",
    "runtime-orchestration-summary.json",
    "validation-report.json",
    "finish-readiness-report.json"
  ]
}
```

Lane contracts add their own required fields and forbidden fields. Main Agent must validate the selected contract before dispatch.

## Expected Dispatches

For every page-dispatch lane, Main Agent must write `runtime-orchestration-summary.json.project.expectedDispatches[]` before final lane validation. Its length must match `project.dispatchPreflightManifest[]`.

Minimum row shape:

```json
{
  "nodeId": "page-index",
  "packetType": "FreePagePacket",
  "status": "completed",
  "changedFiles": ["pages/index.html"],
  "toolCallLedger": {"todoWriteCalls": 0, "previewCalls": 0, "validationScriptCalls": 0, "helperScriptWrites": 0}
}
```

Allowed `status` values are `completed` and `not_required`. Use `not_required` only when a manifest row is intentionally skipped with a recorded reason. Non-page lanes should not write `expectedDispatches[]` unless they explicitly convert into a page-dispatch lane.

`nodeId` is the canonical page identifier and must match the corresponding `dispatchPreflightManifest[].nodeId`. Legacy `pageId` / `targetPageId` may be read by validators for compatibility, but new completion rows must use `nodeId`.

`changedFiles[]` and `toolCallLedger` are required for completed dispatches. Every changed file must be present in the matching `dispatchPreflightManifest[].allowedWritePaths[]`. Page Sub-Agents must report ownership violations instead of writing Main-Agent-owned files.

`dispatchPreflightManifest[]` must also record `toolPolicy`:

```json
{
  "todoWriteAllowed": false,
  "validationScriptsAllowed": false,
  "previewAllowed": false,
  "helperScriptsAllowed": false,
  "designFileWriteAllowed": false,
  "allowedWritePaths": ["pages/index.html", "assets/"]
}
```

`toolDisciplineEvidence` is secondary. Final validation trusts `expectedDispatches[].changedFiles[]` crossed with `dispatchPreflightManifest[].allowedWritePaths[]`, `toolPolicy`, and `expectedDispatches[].toolCallLedger`.

## Supplementary Reads

Use supplementary reads only for declared, bounded context:

```json
{ "path": "delivery-quality/page-density-guidelines.md", "reason": "pageType=information-dense", "ownerLane": "complex_html_page" }
```

Rules:

- `path` must be under `shared-runtime/`, `delivery-quality/`, `visual-experience/`, or the current lane directory.
- A workflow must not use `supplementaryReads[]` to load another intent workflow's runbook.
- Free lane may preserve `implementationEscalationReason` as a compatibility alias, but new packets should use `supplementaryReads[]`.

## Tool Discipline

Sub-Agent packet must repeat these constraints:

- Do not write `.design`.
- Do not run `validate-design-workspace.mjs`, `validate-design-file-format.mjs`, or `validate-graphic-asset-design.mjs`.
- Do not start preview servers or browser sessions.
- Do not create helper scripts.
- Do not generate images.
- Write only files listed in `allowedWritePaths[]`.
- Return completion JSON with `qualityGate`, `nodeId`, `page`, `changedFiles`, `domIds`, `headInfrastructureStatus`, and `toolDisciplineEvidence`.

The completion JSON is the only status channel. `toolDisciplineEvidence` is required and must explicitly report:

```json
{
  "todoWriteUsed": false,
  "previewStarted": false,
  "validationScriptsRunBySubAgent": false,
  "helperScriptsCreated": false,
  "imagesGeneratedBySubAgent": false,
  "wroteOnlyAllowedPaths": true
}
```

If any required field is missing or `true`, Main Agent must treat the result as `dispatch failure`, record the violation in the page dispatch record, and must not count that page as complete until repaired or reduced in scope.

## Blocked Targets

Files under `shared-runtime/blocked-legacy-entrypoints/` are not runtime guides. They must never appear as `pageRuntimeGuide`, `sharedTemplate`, or task-query runtime guide.

If a packet contains a blocked legacy entrypoint, dispatch is invalid and Main Agent must re-route using `SKILL.md` route priority.
