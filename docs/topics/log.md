# 变更日志

## 2026-10-23

- `references/readme.md` 重命名为 `references/README.md`（规范命名，与全库其余索引页一致）
- 同步修正 `references/index.md` 的入站引用
- 原因：小写文件名导致 `generate-readme.py` 在 Windows（大小写不敏感）与 Linux CI（大小写敏感）行为分叉，`--check` 门禁在 Linux 上误报目录缺失 README
- 历史转换记录（2026-08-22 的 `references/readme.md`）保持原样，不改写

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
