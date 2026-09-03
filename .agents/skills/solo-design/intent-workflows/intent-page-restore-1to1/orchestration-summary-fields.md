---
lane: restore_1to1
contract: orchestration-summary-fields
---

# Restore 1:1 Summary Fields

Write restore fields in this order to avoid schema chasing:

1. `project.sourceAuthorityLock`
2. `project.sourceIdentity`
3. `project.pageStateLock`
4. `project.sourceDocumentProfile`
5. `project.measuredSourceFacts`
6. `project.restoreVisualCheckpoints`
7. `project.sourceRegionCoverage`
8. `project.dispatchPreflightManifest`

Also write `project.resolvedLane`, `project.intentProfile`, `project.referenceCaptureEvidence`, and `project.visualSpecExcerpt`.

> **Deprecated fields (do NOT write):** `pages[].restoreEvidence`, `project.restoreEvidenceReview`, `project.visualDiffReview`, `project.sourceFactCoverageMap`. These are no longer required for restore_1to1 delivery.

`project.sourceIdentity` must include `businessType`, `coreObjects[]`, `deviceType`, and `pageTitle`.

`project.pageStateLock` must include `currentState` and `forbiddenDeviations[]`.

`project.sourceDocumentProfile` must include `sourceType`, `documentLengthClass`, `requiredRegionGroups[]`, and when applicable `viewportScrollRatio` or `deviceFramePresent`.

At least 8 measured source facts are required, including at least 5 high-priority facts with `measurementBasis`. Required categories are `viewport`, `layout-region`, `color-surface`, `component-proportion`, and `density-spacing`.

`project.sourceRegionCoverage[]` rows must include `regionGroup` and `status` or `mappedStatus`. High/medium rows must be `mapped` or `intentionally-deviated`.

For URL long-page restore, required region groups are `first-screen`, `middle-section`, and `footer-bottom`. For image restore with a visible device frame, required region groups are `outer-frame`, `device-shell`, `inner-screen`, and `primary-object`.

At least 8 visual checkpoints are required, including at least 5 high-priority checkpoints for full-page restore.

Each `project.restoreVisualCheckpoints[]` row must include `sourceFact` and `expected`. If a high-priority checkpoint may pass with a controlled deviation, it must include `allowedDeviationRef` that maps to `restorationContractLite.allowedDeviationList`.

## Field Auto-Fill Matrix

| Field | Written By | LLM Writes Manually? |
|-------|-----------|---------------------|
| `project.sourceAuthorityLock` | Main Agent | ✅ Step 2 |
| `project.sourceIdentity` | Main Agent | ✅ Step 3 |
| `project.pageStateLock` | Main Agent | ✅ Step 3 |
| `project.sourceDocumentProfile` | Main Agent | ✅ Step 4 |
| `project.measuredSourceFacts` | Main Agent | ✅ Step 5 |
| `project.restoreVisualCheckpoints` | Main Agent | ✅ Step 6 |
| `project.sourceRegionCoverage` | Main Agent | ✅ Step 7 |
| `project.expectedDispatches[]` | `record-dispatch-completion.mjs` | ❌ Script auto |

Rules:
- "❌ Script auto" fields MUST NOT be manually constructed by Main Agent via apply_patch.
- `precision` field in measuredSourceFacts is advisory (not yet validated by scripts).
- Do NOT write `pages[].restoreEvidence`, `project.restoreEvidenceReview`, `project.visualDiffReview`, or `project.sourceFactCoverageMap`.
