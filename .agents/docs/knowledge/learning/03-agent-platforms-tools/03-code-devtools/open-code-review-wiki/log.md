---
id: "open-code-review-wiki-log"
title: "Open Code Review 完全指南 — 变更日志"
source: "https://github.com/snyk/open-code-review"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/03-code-devtools/open-code-review-wiki/log.toml"
---
# Changelog

## 2026-08-22

- **Initialization**: 将 open-code-review-wiki 转换为 OKF v0.2 Bundle。创建 concepts/ 与 references/ 子目录，将 11 个源文件按映射迁移（7 篇归入 concepts/，3 篇归入 references/，00-overview 转为根 index.md）。为所有内容文件添加 OKF frontmatter（type、description、generated、verified、status、stale_after），source 字段转换为 OKF sources 格式（id/resource/title）。根 index.md 仅保留 okf_version: "0.2"。所有同 Bundle 内裸文件名链接修正为 /concepts/ 或 /references/ 绝对路径。创建 concepts/index.md 与 references/index.md 导航页。正文内容未改写。
