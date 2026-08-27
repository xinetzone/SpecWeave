# Conversion Log

## 2026-08-22

- Source: baidu-unlimited-ocr-wiki (9 files)
- Target: OKF v0.2 Bundle
- Converted at: 2026-08-22T00:00:00Z
- OKF version: 0.2

## File Mapping

| Source | Destination | Type |
|--------|-------------|------|
| 00-overview.md | /index.md | (root index) |
| 01-core-architecture.md | /concepts/01-core-architecture.md | Concept |
| 02-performance-data.md | /references/02-performance-data.md | Reference |
| 03-quick-start.md | /concepts/03-quick-start.md | Tutorial |
| 04-limitations-risks.md | /references/04-limitations-risks.md | Reference |
| 05-architecture-insights.md | /concepts/05-architecture-insights.md | Concept |
| 06-transferable-patterns.md | /concepts/06-transferable-patterns.md | Pattern |
| 07-specweave-implications.md | /concepts/07-specweave-implications.md | Reference |
| 08-summary-faq.md | /references/08-summary-faq.md | Reference |

## Changes Applied

1. Restructured flat files into concepts/ and references/ directories
2. Root index.md frontmatter reduced to okf_version only
3. Subdirectory index.md files have no frontmatter
4. Content files: added type, description, generated (by + at), verified (by + at), status, stale_after fields
5. source field converted to sources array
6. Internal bare-filename links converted to absolute /concepts/ or /references/ paths
7. log.md created
8. Body content preserved without rewriting
