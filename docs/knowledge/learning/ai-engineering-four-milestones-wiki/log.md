# 变更日志
## 2026-08-22

- **Initialization**: 将 ai-engineering-four-milestones-wiki 转换为 OKF v0.2 Bundle。创建 concepts/ 与 references/ 子目录，将 8 个源文件按映射迁移（00-overview 转为根 index.md，01-05 归入 concepts/ 为 Concept 类型，06 归入 concepts/ 为 Pattern 类型，07 归入 references/ 为 Reference 类型）。将 Bundle 目录外的散文件 ai-engineering-four-milestones-wiki.md 移入 references/ 为 Reference 类型。为所有内容文件添加 OKF frontmatter（type、description、generated、verified、status、stale_after），source 字段转换为 sources 列表。根 index.md 仅含 okf_version: "0.2"。子目录 index.md 无 frontmatter。所有同 Bundle 内裸文件名链接修正为 /concepts/ 或 /references/ 绝对路径，散文件中指向 Bundle 内文件的链接同步调整。正文内容未改写。
