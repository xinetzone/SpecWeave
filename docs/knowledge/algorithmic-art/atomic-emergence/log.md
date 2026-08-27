# 变更日志

## 2026-08-22

- 初始转换为 OKF v0.2 Bundle
- 将 `philosophy.md` 移动到 `concepts/philosophy.md`（Concept）
- 新建根 `index.md`（frontmatter 仅 `okf_version: "0.2"`，正文导航链接到 `concepts/philosophy.md`）
- 内容文件添加 `type`、`description`、`generated`、`verified`、`status`、`stale_after` 字段
- `generated`/`verified` 使用嵌套格式
- `index.html` 保持原位不移动
- 子目录：concepts
- 正文内容不改写
