# 变更日志
## 2026-08-22


- Source: okf-kit-wiki (13 files)
- Target: OKF v0.2 Bundle
- Converted at: 2026-08-22T00:00:00Z
- OKF version: 0.2

## File Mapping

| Source | Destination | Type |
|--------|-------------|------|
| 00-overview.md | /index.md | (root index) |
| 01-installation.md | /concepts/01-installation.md | Tutorial |
| 02-cli-reference.md | /references/02-cli-reference.md | Reference |
| 03-okf-format.md | /concepts/03-okf-format.md | Concept |
| 04-core-architecture.md | /concepts/04-core-architecture.md | Concept |
| 05-sync-mechanism.md | /concepts/05-sync-mechanism.md | Concept |
| 06-chat-system.md | /concepts/06-chat-system.md | Concept |
| 07-mcp-serve.md | /concepts/07-mcp-serve.md | Reference |
| 08-registry-visualize.md | /concepts/08-registry-visualize.md | Reference |
| 09-extension-development.md | /concepts/09-extension-development.md | Tutorial |
| 10-faq-troubleshooting.md | /references/10-faq-troubleshooting.md | Reference |
| 11-summary-resources.md | /references/11-summary-resources.md | Reference |
| seven-concepts-report.md | /references/seven-concepts-report.md | Report |

## Changes Applied

1. Restructured flat files into concepts/ and references/ directories
2. Root index.md frontmatter reduced to okf_version only
3. Subdirectory index.md files have no frontmatter
4. Content files: added type, description, generated, verified, status, stale_after fields
5. source field converted to sources array
6. Internal bare-filename links converted to absolute /concepts/ or /references/ paths
7. Cross-bundle ../ links prefixed with additional ../
8. log.md created
