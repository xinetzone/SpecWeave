---
lane: restore_1to1
contract: dispatch
---

# Restore 1:1 Dispatch Contract

Required fields: `intentProfile.caseFamily=restore_1to1`, `replicationMode=high-fidelity`, `sourceType`, `sourceIdentity`, `pageStateLock`, `sourceDocumentProfile`, `visualSpecExcerpt`, `measuredSourceFacts`, `restoreVisualCheckpoints`, `sourceRegionCoverage`, `referenceCaptureEvidence`, `sourceAuthorityLock`, `restoreContractStatus`, `restoreCompactPacket`, `allowedWritePaths[]`, `toolPolicy`, `fillHtmlHeadCommand`, and page slice fields from `shared-runtime/agent-dispatch-runtime/lane-dispatch-index.md`. Packet serialization and Task text format are defined in `restore-dispatch-packet-format.md`.

Forbidden fields: free creative recipes, generic visual reinterpretation, and visual-experience files as source authority.

`sourceType` must match the available source evidence:

- `image`: only user-provided image/screenshot evidence is used as visual authority.
- `url`: browser full-page screenshot evidence is required.
- `image+url`: both provided image/screenshot evidence and URL evidence are required; the provided image/screenshot remains visual authority and URL evidence is secondary.

Dispatch is invalid if both provided image/screenshot and URL are present but `sourceType` is not `image+url`.

Dispatch is invalid unless `sourceAuthorityLock` is copied exactly from `runtime-orchestration-summary.json.project.sourceAuthorityLock`; do not send `{}`. It must include `visualAuthority`, `contentSupplement`, `browserObservationRole`, `mayOverrideVisualAuthority:false`, and `lockedBeforeDispatch:true`.

Dispatch is invalid unless `restoreContractStatus.success === true` and `restoreContractStatus.reportPath === "restore-contract-report.json"`.

`restoreCompactPacket` is the only visual/context packet sent to the Sub-Agent. Do not paste full `runtime-orchestration-summary.json`, full workflow files, or generic `visual-experience/` guidance into a restore page task.

`sourceIdentity` and `pageStateLock` are state locks, not suggestions. Sub-Agent output is invalid if it changes the business/page type or current visible state.

`measuredSourceFacts` must contain at least 8 rows, including at least 5 high-priority rows with `measurementBasis`. Required categories are `viewport`, `layout-region`, `color-surface`, `component-proportion`, and `density-spacing`. Each row must include `id`, `category`, `sourceRegion`, `fact`, `measurementBasis`, `priority`, and `usedByCheckpointIds[]`.

`restoreVisualCheckpoints` must contain at least 8 rows, including at least 5 high-priority rows. Each high-priority row must include executable visual facts:

```json
{
  "id": "vc-01",
  "priority": "high",
  "sourceRegion": "header",
  "sourceFact": "logo at top-left, nav aligned right",
  "expected": "same header geometry and spacing",
  "allowedDeviationRef": "copy-localization",
  "implementationEvidence": "pages/index.html header block",
  "status": "matched | partial | missing"
}
```

Do not replace checkpoint facts with taste language such as "modern", "beautiful", or "premium". Dispatch is invalid when high-priority rows lack `sourceFact` or `expected`. When the row is still a pre-dispatch plan, `status` may be omitted; persisted completion/review rows must use `matched`, `partial`, or `missing`. If a checkpoint may pass with a controlled deviation, its `allowedDeviationRef` must map to the packet's `restorationContractLite.allowedDeviationList`.

`sourceRegionCoverage[]` must include `regionGroup` and `status` / `mappedStatus`. URL long-page restore must cover `first-screen`, `middle-section`, and `footer-bottom`; device-frame image restore must cover `outer-frame`, `device-shell`, `inner-screen`, and `primary-object`.

`allowedWritePaths[]` is a hard ownership boundary. Restore Sub-Agents may only write exact files or directory prefixes listed there. They must return `changedFiles[]` and `toolCallLedger`; the Main Agent must persist both into `project.expectedDispatches[]` before final validation.

Restore uses persisted pre-dispatch source facts and checkpoints; do not request a pixel-level validator or a browser preview just to satisfy this dispatch contract.

## Image Reference Delivery

For `sourceType: "image"` or `sourceType: "image+url"`:
- The dispatch Task description must include the reference image workspace path in a dedicated line: `Reference image: {designProjectPath}/assets/source-screenshot.png`
- The Sub-Agent execution environment must receive this image path so it can Read the file for visual calibration.
- Before dispatch, if the screenshot resides in `.uploads/` (outside the design project directory), Main Agent must copy it into `{designProjectPath}/assets/` to ensure Sub-Agent file access.
- Dispatch is invalid if the Sub-Agent cannot access the reference image file.

For `sourceType: "url"`:
- The dispatch Task description must include the full-page screenshot path captured during source authority step.

## Packet Format

Before dispatch, apply every requirement in `restore-dispatch-packet-format.md`. Missing packet files, required fields, numeric Visual Spec values, or output-strategy constraints block dispatch.
