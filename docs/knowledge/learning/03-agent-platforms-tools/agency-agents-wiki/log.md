# 变更日志

## 2026-08-22

**Initialization**

- 从现有教程文档（12 个 Markdown 文件）初始化为 OKF v0.2 Bundle
- 文件映射：
  - `00-overview.md` → 根 `index.md`
  - `01-architecture.md` → `concepts/01-architecture.md` (Concept)
  - `02-agent-format.md` → `concepts/02-agent-format.md` (Concept)
  - `03-roster-divisions.md` → `concepts/03-roster-divisions.md` (Concept)
  - `04-scripts-tooling.md` → `concepts/04-scripts-tooling.md` (Reference)
  - `05-integrations.md` → `concepts/05-integrations.md` (Reference)
  - `06-usage-examples.md` → `examples/06-usage-examples.md` (Example)
  - `07-strategy-playbooks.md` → `concepts/07-strategy-playbooks.md` (Pattern)
  - `08-faq-troubleshooting.md` → `references/08-faq-troubleshooting.md` (Reference)
  - `09-best-practices.md` → `concepts/09-best-practices.md` (Pattern)
  - `10-summary-resources.md` → `references/10-summary-resources.md` (Reference)
  - `quickstart-demo-guide.md` → `concepts/quickstart-demo-guide.md` (Tutorial)
- 根 `index.md` frontmatter 仅保留 `okf_version: "0.2"`
- 内容文件添加 `type`、`description`、`generated`、`verified`、`status`、`stale_after` 字段
- `source` 字段转换为 OKF `sources` 列表格式
- 同 Bundle 内裸文件名链接改为 `/` 开头的 bundle-relative 绝对路径
- 跨 Bundle 的 `../` 链接增加一层 `../`
- 正文内容不改写
