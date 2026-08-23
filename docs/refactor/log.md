# 变更日志

## 2026-08-22

- 初始转换为 OKF v0.2 Bundle
- 将 `refactor-concurrent-safety-checker-20260812.md` 移动到 `concepts/refactor-concurrent-safety-checker.md`（Report）
- 新建根 `index.md`（frontmatter 仅 `okf_version: "0.2"`，正文导航链接到 concepts/ 中的文件）
- 创建 `concepts/index.md`（无 frontmatter）
- 内容文件添加 `type`、`description`、`generated`、`verified`、`status`、`stale_after` 字段，原有冲突的 `type: "refactor"` 重命名为 `original_type`
- `generated`/`verified` 使用嵌套格式
- 子目录：concepts
- 正文内容不改写
- 原 `refactor-concurrent-safety-checker-20260812.md` 已删除
