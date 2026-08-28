# 变更日志
## 2026-08-22

- **Initialization**: 将 `book-to-skill-wiki` 目录转换为 OKF v0.2 Bundle。10 个文件按类型映射至根目录、`concepts/` 和 `references/`：`00-overview.md` 转为根 `index.md`，`01`-`08` 映射至 `concepts/`（含 Concept、Reference、Tutorial、Pattern 四种类型），`09-summary-faq.md` 映射至 `references/`（Reference）。添加完整 OKF frontmatter（type、description、generated、verified、status、stale_after）；同 Bundle 裸文件名链接统一为 `/concepts/` 或 `/references/` 绝对路径；根 `index.md` 添加 `okf_version: "0.2"`；子目录索引页无 frontmatter；正文内容保持原样不改写；创建初始化日志。
