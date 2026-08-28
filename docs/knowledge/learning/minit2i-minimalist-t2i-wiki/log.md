# 变更日志
## 2026-08-22

- Source: minit2i-minimalist-t2i-wiki (8 files)
- Target: OKF v0.2 Bundle
- Converted at: 2026-08-22T00:00:00Z
- OKF version: 0.2

## File Mapping

| Source | Destination | Type |
|--------|-------------|------|
| 00-overview.md | /index.md | (root index) |
| 01-design-philosophy.md | /concepts/01-design-philosophy.md | Concept |
| 02-three-subtractions.md | /concepts/02-three-subtractions.md | Concept |
| 03-mm-jit-architecture.md | /concepts/03-mm-jit-architecture.md | Concept |
| 04-experiments-performance.md | /references/04-experiments-performance.md | Reference |
| 05-limitations-open-problems.md | /references/05-limitations-open-problems.md | Reference |
| 06-paradigm-shift-insights.md | /concepts/06-paradigm-shift-insights.md | Concept |
| 07-summary-faq-resources.md | /references/07-summary-faq-resources.md | Reference |

## Changes Applied

1. Restructured flat files into concepts/ and references/ directories
2. Root index.md frontmatter reduced to okf_version only
3. Subdirectory index.md files have no frontmatter
4. Content files: added type, description, generated, verified, status, stale_after fields
5. source field converted to sources array
6. Internal bare-filename links converted to absolute /concepts/ or /references/ paths
7. log.md created
