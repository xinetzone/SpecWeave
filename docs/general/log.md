# 变更日志

## 2026-08-22

- 初始转换为 OKF v0.2 Bundle
- 将 `index.md` 转换为根 `index.md`（frontmatter 仅 `okf_version: "0.2"`，保留正文）
- 将 `README.md` 移动到 `references/readme.md`（Reference）
- 内容文件添加 `type`、`description`、`generated`、`verified`、`status`、`stale_after` 字段
- `generated`/`verified` 使用嵌套格式
- 同 Bundle 内裸文件名链接改为 `/` 开头的 bundle-relative 绝对路径
- 子目录：references
- 正文内容不改写
- 原 `README.md` 已删除
