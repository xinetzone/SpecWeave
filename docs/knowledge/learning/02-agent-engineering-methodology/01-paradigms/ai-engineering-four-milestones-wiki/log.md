# Changelog

## 2026-08-22

- **Atomic Wiki Migration**: 将 ai-engineering-four-milestones-wiki 从 `docs/knowledge/learning/ai-engineering-four-milestones-wiki/` 迁移至 `.agents/docs/knowledge/learning/02-agent-engineering-methodology/01-paradigms/ai-engineering-four-milestones-wiki/`，创建原子化 Wiki 目录。扁平化所有编号章节（00-07）至 Wiki 根目录，移除 concepts/ 与 references/ 子目录结构。为所有章节文件替换为四字段 frontmatter（id/title/source/x-toml-ref），id 格式统一为 `ai-engineering-four-milestones-wiki-NN`。x-toml-ref 使用 7 层 `../` 指向 `.meta/toml/.agents/docs/knowledge/learning/02-agent-engineering-methodology/01-paradigms/ai-engineering-four-milestones-wiki/`。创建 README.md 文档索引，合并 concepts/index.md 与 references/index.md 导航内容及单文件版阅读建议。单文件版 `references/ai-engineering-four-milestones-wiki.md` 含独特内容（引用式简介、带"核心问题"列的导航表、阅读建议），作为补充文件 `ai-engineering-four-milestones-wiki.md` 迁移。所有内部链接移除 concepts/ 与 references/ 前缀，`/index.md` 改为 `00-overview.md`，索引页链接改为 `README.md`。根目录旧版单文件不存在，无需处理。

## 2026-08-22

- **Initialization**: 将 ai-engineering-four-milestones-wiki 转换为 OKF v0.2 Bundle。创建 concepts/ 与 references/ 子目录，将 8 个源文件按映射迁移（00-overview 转为根 index.md，01-05 归入 concepts/ 为 Concept 类型，06 归入 concepts/ 为 Pattern 类型，07 归入 references/ 为 Reference 类型）。将 Bundle 目录外的散文件 ai-engineering-four-milestones-wiki.md 移入 references/ 为 Reference 类型。为所有内容文件添加 OKF frontmatter（type、description、generated、verified、status、stale_after），source 字段转换为 sources 列表。根 index.md 仅含 okf_version: "0.2"。子目录 index.md 无 frontmatter。所有同 Bundle 内裸文件名链接修正为 /concepts/ 或 /references/ 绝对路径，散文件中指向 Bundle 内文件的链接同步调整。正文内容未改写。
