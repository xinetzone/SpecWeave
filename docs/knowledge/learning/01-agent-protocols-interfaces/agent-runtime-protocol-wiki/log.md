# 变更日志

## 2026-08-22

- 初始转换为 OKF v0.2 Bundle
- 将平铺的 14 个 Markdown 文件重组为 OKF 标准目录结构：
  - `00-overview.md` → 根 `index.md`（含 `okf_version: "0.2"` frontmatter）
  - 7 个 Concept 文档移入 `concepts/`（01-06、08）
  - 5 个 Reference 文档移入 `concepts/`（07、09-cross-dimensional、09-framework-comparison、10-content-evaluation、10-enterprise-selection-guide）
  - 1 个 Reference 文档移入 `references/`（11-summary-faq-resources）
- 为所有 13 个内容文件补全 OKF frontmatter：
  - `type`（Concept/Reference）
  - `title`（从 H1 提取）
  - `description`（30-80 字内容摘要）
  - `generated`（by: process:docs-to-okf-conversion, at: 2026-08-22T00:00:00Z）
  - `verified`（by: process:seven-concepts-v, at: 2026-08-22T00:00:00Z）
  - `status: "stable"`
  - `stale_after: "2027-08-22"`
  - `sources`（微信公众号原文登记）
- 链接转换：
  - 同 Bundle 裸文件名链接改为 `/concepts/` 或 `/references/` 绝对路径
  - `00-overview.md` 链接改为 `/index.md`
  - HTML 文件引用（`interactive-selection-matrix.html`）保持原样
- 创建 `concepts/index.md`（无 frontmatter，导航索引）
- 创建 `references/index.md`（无 frontmatter，导航索引）
- `interactive-selection-matrix.html` 保持根目录原位不移动、不修改
- 正文内容不改写，仅添加 frontmatter 并调整内部链接路径
