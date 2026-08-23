# 变更日志

## 2026-08-22

- 初始转换为 OKF v0.2 Bundle
- 将 `three-ai-tools-wiki.md` 从上级散文件移动到 `concepts/three-ai-tools-wiki.md`（Concept）
- 将 `article-content.md` 移动到 `references/article-content.md`（Reference）
- 将 `seven-concepts-report.md` 移动到 `references/seven-concepts-report.md`（Report）
- 新建根 `index.md`（frontmatter 仅 `okf_version: "0.2"`，正文为 Bundle 导航）
- 内容文件添加 `type`、`description`、`generated`、`verified`、`status`、`stale_after` 字段
- `generated`/`verified` 使用嵌套格式
- 同 Bundle 内裸文件名链接改为 `/` 开头的 bundle-relative 绝对路径
- 子目录：concepts, references
- 正文内容不改写
- 散文件移动后删除原位置
