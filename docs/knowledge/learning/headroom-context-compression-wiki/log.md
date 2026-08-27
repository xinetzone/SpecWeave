# 变更日志

## 2026-08-22

- 初始转换为 OKF v0.2 Bundle
- 将平铺的 11 个 Markdown 文件重组为 OKF 标准目录结构：
  - `00-overview.md` → 根 `index.md`（含 `okf_version: "0.2"` frontmatter）
  - 4 个 Concept 文档移入 `concepts/`（01、02、03、06）
  - 2 个 Tutorial 文档移入 `concepts/`（04、07）
  - 1 个 Pattern 文档移入 `concepts/`（08）
  - 3 个 Reference 文档移入 `references/`（05、09、10）
- 为所有 10 个内容文件补全 OKF frontmatter：
  - `type`（Concept/Tutorial/Pattern/Reference）
  - `description`（内容摘要）
  - `generated`（by: process:docs-to-okf-conversion, at: 2026-08-22T00:00:00Z，嵌套 YAML 格式）
  - `verified`（by: process:seven-concepts-v, at: 2026-08-22T00:00:00Z，嵌套 YAML 格式）
  - `status: "stable"`
  - `stale_after: "2027-08-22"`
  - 保留原有字段（id、title、date、category、tags、x-toml-ref）
  - `source` 转换为 `sources` 列表
- 链接转换：
  - 同 Bundle 裸文件名链接改为 `/concepts/` 或 `/references/` 绝对路径
  - `00-overview.md` 链接改为 `/index.md`
  - 锚点链接（如 `#q2-...`）保留不变
  - 指向 Bundle 外部模式库的相对路径链接保持原样
- 创建 `concepts/index.md`（无 frontmatter，目录导航）
- 创建 `references/index.md`（无 frontmatter，目录导航）
- 正文内容不改写，仅添加 frontmatter 并调整内部链接路径
