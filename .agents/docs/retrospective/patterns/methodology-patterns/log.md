# OKF Bundle 转换日志

## 2026-08-22


- **Bundle 名称**：methodology-patterns
- **Bundle ID**：B29
- **OKF 版本**：0.2
- **转换日期**：2026-08-22
- **转换过程**：`process:docs-to-okf-conversion`
- **验证过程**：`process:seven-concepts-v`

## 文件映射

| 原始路径 | 目标路径 | 类型 | 处理说明 |
|---|---|---|---|
| `README.md` | `index.md` | Bundle 根 | frontmatter 精简为仅 `okf_version: "0.2"`；模式文件链接添加 `concepts/` 前缀 |
| `content-funnel-analysis.md` | `concepts/content-funnel-analysis.md` | Pattern | 保留原有 frontmatter 字段；type 改为 Pattern；移除 x-toml-ref；添加 OKF 字段；修正外部相对链接 |
| `cross-framework-atomic-analysis.md` | `concepts/cross-framework-atomic-analysis.md` | Pattern | 同上 |
| `dual-engine-uncertainty-certainty.md` | `concepts/dual-engine-uncertainty-certainty.md` | Pattern | 同上 |
| `dual-layer-analysis-report.md` | `concepts/dual-layer-analysis-report.md` | Pattern | 同上 |
| `error-blacklist-monotonic-evolution.md` | `concepts/error-blacklist-monotonic-evolution.md` | Pattern | 同上 |
| `evaluation-driven-self-evolution.md` | `concepts/evaluation-driven-self-evolution.md` | Pattern | 同上 |
| `integration-over-invention.md` | `concepts/integration-over-invention.md` | Pattern | 同上 |
| `knowledge-compilation.md` | `concepts/knowledge-compilation.md` | Pattern | 同上 |
| `layered-chained-spec.md` | `concepts/layered-chained-spec.md` | Pattern | 同上 |
| `lowering-barriers-creates-markets.md` | `concepts/lowering-barriers-creates-markets.md` | Pattern | 同上 |
| `offline-first-architecture.md` | `concepts/offline-first-architecture.md` | Pattern | 同上 |
| `responsibility-transfer-governance.md` | `concepts/responsibility-transfer-governance.md` | Pattern | 同上 |
| `subagent-standardized-instruction.md` | `concepts/subagent-standardized-instruction.md` | Pattern | 同上 |
| `tech-article-to-wiki-batch-generation.md` | `concepts/tech-article-to-wiki-batch-generation.md` | Pattern | 同上 |
| `three-layer-repair-closure.md` | `concepts/three-layer-repair-closure.md` | Pattern | 同上 |
| — | `concepts/index.md` | 目录索引 | 新建，无 frontmatter |
| — | `log.md` | 变更日志 | 新建 |

## Frontmatter 规范

所有内容文件（不含根 index.md 与子目录 index.md）均保留原有 frontmatter 字段（id/title/date/maturity/source/related_patterns/tags/validation_count/reuse_count/documentation_level 等），并进行以下变更：

- `type` 字段统一改为 `"Pattern"`
- 移除 `x-toml-ref` 字段（OKF 使用 YAML frontmatter，无需 TOML sidecar）
- 追加以下 OKF 字段：

```yaml
description: "<内容摘要>"
generated:
  by: "process:docs-to-okf-conversion"
  at: "2026-08-22T00:00:00Z"
verified:
  by: "process:seven-concepts-v"
  at: "2026-08-22T00:00:00Z"
status: "stable"
stale_after: "2027-08-22"
```

## 链接修正汇总

模式文件从 Bundle 根目录移动到 `concepts/` 子目录，目录深度增加一层，以下相对链接已修正：

| 链接模式 | 修正前 | 修正后 | 涉及文件 |
|---|---|---|---|
| reports 目录 | `../../reports/` | `../../../reports/` | content-funnel-analysis, cross-framework-atomic-analysis, dual-layer-analysis-report, integration-over-invention, lowering-barriers-creates-markets, offline-first-architecture, subagent-standardized-instruction, tech-article-to-wiki-batch-generation |
| knowledge 目录 | `../../../knowledge/` | `../../../../knowledge/` | cross-framework-atomic-analysis |
| playground 目录 | `../../../playground/` | `../../../../playground/` | three-layer-repair-closure |
| .agents 目录 | `../../../../.agents/` | `../../../../../.agents/` | knowledge-compilation, subagent-standardized-instruction, tech-article-to-wiki-batch-generation, three-layer-repair-closure |
| learning 目录 | `../learning/` | `../../learning/` | knowledge-compilation |
| 同 Bundle 模式文件 | `filename.md` | 不变（同目录移动） | 所有含模式间互链的文件 |

根 `index.md`（原 README.md）中模式文件链接从裸文件名改为 `concepts/filename.md`。

## 最终目录结构

```
methodology-patterns/
├── index.md
├── log.md
└── concepts/
    ├── index.md
    ├── content-funnel-analysis.md
    ├── cross-framework-atomic-analysis.md
    ├── dual-engine-uncertainty-certainty.md
    ├── dual-layer-analysis-report.md
    ├── error-blacklist-monotonic-evolution.md
    ├── evaluation-driven-self-evolution.md
    ├── integration-over-invention.md
    ├── knowledge-compilation.md
    ├── layered-chained-spec.md
    ├── lowering-barriers-creates-markets.md
    ├── offline-first-architecture.md
    ├── responsibility-transfer-governance.md
    ├── subagent-standardized-instruction.md
    ├── tech-article-to-wiki-batch-generation.md
    └── three-layer-repair-closure.md
```

## 备注

- 所有正文内容保持原样，未做改写
- `generated` 与 `verified` 字段均采用嵌套 YAML 格式，未使用 inline 花括号
- 同 Bundle 内 15 个模式文件间的互链无需修正（整体移动至 `concepts/`，相对位置不变）
- README 表格中引用的 `plugin-bridge-standard-integration.md` 与 `automation-idempotent-four-elements.md` 为原始文档中已有的悬空引用，按"正文不改写"原则保留
