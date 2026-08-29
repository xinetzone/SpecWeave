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

## 2026-08-23

- 原子化迁移：从 `docs/knowledge/learning/three-ai-tools-learning-wiki/` 迁移至 `.agents/docs/knowledge/learning/06-business-trends-analysis/three-ai-tools-wiki/`
- 扁平化目录结构：移除 `concepts/`、`references/` 子目录，所有内容文件置于 wiki 根目录
- 文件重命名：
  - `index.md` → `00-overview.md`
  - `concepts/three-ai-tools-wiki.md` → `01-three-ai-tools.md`（合并目标位置已有单文件的详细内容）
  - `references/article-content.md` → `02-article-content.md`
  - `references/seven-concepts-report.md` → `03-seven-concepts-report.md`
- 合并节索引文件（`concepts/index.md`、`references/index.md`）至 `README.md`
- 统一 frontmatter：添加 `id`（格式 `three-ai-tools-wiki-NN`）、`x-toml-ref`（6 级 `../` 深度）、`source`（原文 URL）
- 生成 TOML 元数据文件至 `.meta/toml/.agents/docs/knowledge/learning/06-business-trends-analysis/three-ai-tools-wiki/`
- 修复内部链接：bundle-relative 绝对路径改为同目录扁平链接
- 旧单文件 `three-ai-tools-wiki.md` 更新为重定向，指向新 wiki 目录
