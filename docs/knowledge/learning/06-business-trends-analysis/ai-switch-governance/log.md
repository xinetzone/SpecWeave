# 变更日志

## 2026-08-22

- 初始转换为 OKF v0.2 Bundle
- 从平铺的 4 个 Markdown 文件重组为 OKF 标准目录结构
- 根 `index.md` frontmatter 仅保留 `okf_version: "0.2"`
- 内容文件添加 `type`、`description`、`generated`、`verified`、`status`、`stale_after` 字段
- `source` 字段转换为 OKF `sources` 列表格式
- 同 Bundle 内裸文件名链接改为 `/` 开头的 bundle-relative 绝对路径
- 子目录：concepts, references
- 正文内容不改写
