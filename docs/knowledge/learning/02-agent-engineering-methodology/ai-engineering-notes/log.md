---
id: "ai-engineering-notes-log"
title: "AI Engineering 知识库变更日志"
source: "docs/knowledge/ai-engineering/log.md"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/02-agent-engineering-methodology/ai-engineering-notes/log.toml"
---
# 变更日志

## 2026-08-22

- 初始转换为 OKF v0.2 Bundle
- 将 `README.md` 转换为根 `index.md`（frontmatter 仅 `okf_version: "0.2"`，保留正文）
- 将 `karpathy-llm-wiki-analysis-20260707.md` 移动到 `concepts/karpathy-llm-wiki-analysis.md`（Report）
- 将 `loop-engineering-knowledge-base.md` 移动到 `concepts/loop-engineering-knowledge-base.md`（Reference）
- 将 `anthropic-financial-services-wiki.md` 从 `learning/` 散文件移动到 `concepts/anthropic-financial-services-wiki.md`（Reference）
- 将 `octo-platform-wiki.md` 从 `learning/` 散文件移动到 `concepts/octo-platform-wiki.md`（Reference）
- 内容文件添加 `type`、`description`、`generated`、`verified`、`status`、`stale_after` 字段，保留原有字段（冲突的 `type`/`status` 重命名为 `original_type`/`original_status`）
- `generated`/`verified` 使用嵌套格式
- 同 Bundle 内裸文件名链接改为 `/` 开头的 bundle-relative 绝对路径
- 子目录：concepts
- 正文内容不改写
- 散文件移动后删除原位置
