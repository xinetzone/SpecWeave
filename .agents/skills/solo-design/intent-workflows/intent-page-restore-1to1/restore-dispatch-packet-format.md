---
lane: restore_1to1
contract: dispatch-packet-format
---

# Restore 1:1 Dispatch Packet Format

This file owns serialization and Task-delivery details for `RestorePagePacket`. Behavioral validity rules remain in `dispatch-contract.md`.

## Packet File Delivery

Write the complete packet to `{designProjectPath}/dispatch-packet-{nodeId}.json` before dispatch. The Sub-Agent reads this file in Phase 1 instead of relying on Task description text for structured data.

Required fields:

- Manifest entry: `nodeId`, `htmlSrc`, `cssPath`, `htmlFilePath`, `brandPrefix`, `restoreContractStatus`, `fillHtmlHeadCommand`.
- Compact packet: `sourceType`, `sourceIdentity`, `pageStateLock`, `sourceDocumentProfile`, `measuredSourceFacts`, `restoreVisualCheckpoints`, `sourceRegionCoverage`, `contentToPreserve`.
- Summary slice: `referenceCaptureEvidence`, `sourceAuthorityLock`, `restorationContractLite`, `visualSpecExcerpt`.

Forbidden:

- Inlining the full packet in Task text.
- Writing only `restoreCompactPacket` without the outer manifest fields.
- Compressing structured fields into natural-language summaries.

The packet is invalid when:

- `dispatch-packet-{nodeId}.json` is missing.
- Any Phase 1 required field is missing.
- `measuredSourceFacts` has fewer than 8 rows.
- `restoreVisualCheckpoints` has fewer than 8 rows.
- `visualSpecExcerpt` is empty or only contains a file path.

## Structured Visual Spec

The Task description must include categorized numeric values:

```text
=== VISUAL SPEC ===

[LAYOUT]
viewport: {width}x{height}, {shell-type}

[SPACING]
{element}: {px-values}

[TYPOGRAPHY]
{element}: {size}/{line-height} {weight}

[COLORS]
{surface}: {hex-value}

[SHADOWS & DEPTH]
{element}: {css-shadow-shorthand}

[RADII]
{element}: {px}

=== END SPEC ===
```

Do not replace this block with prose.

## Output Strategy

- `sourceDocumentProfile.documentLengthClass === "single-screen"`: write complete page HTML in one `apply_patch`.
- `sourceDocumentProfile.documentLengthClass === "medium" | "long"`: use at most three `apply_patch` operations, each covering a complete `regionGroup` from `sourceRegionCoverage`.
