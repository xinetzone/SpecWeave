+++
id = "meta-convention-over-configuration-docs"
date = "2026-06-29"
type = "insight"
scope = "meta,documentation,convention-over-configuration,style"
source = "../insight-extraction.md#洞察6约定优于配置先观察再编写"
archived_to = "待沉淀至AGENTS.md启动协议文档编写规范"
+++

# Meta洞察1："约定优于配置"——先观察再编写

→ 待沉淀：AGENTS.md启动协议/文档编写规范

## 事件事实

初期按照spec中的NFR-1描述为规则文档添加了TOML frontmatter，后来发现`.agents/rules/`下所有现有文档均不使用frontmatter，不得不回退修正。

## 文档风格冲突分析

这个问题的本质是"文档描述vs代码库现实"的冲突。Spec中的NFR描述了"TOML frontmatter"，但这是从spec模板继承的惯性描述，实际代码库的约定是：

| 文档类型 | 目录 | frontmatter | 其他特征 |
|---------|------|------------|---------|
| 治理规则文档 | `.agents/rules/` | 无frontmatter | 纯Markdown，直接以#标题开头 |
| Spec文档 | `.trae/specs/` | 有YAML/TOML frontmatter | 包含metadata字段 |
| 复盘报告/洞察 | `docs/retrospective/` | 有TOML frontmatter | id/date/type/source字段 |

## 洞察：约定优于配置原则

在编写新文档时，"观察现有文档风格"应该是第一步，而不是依赖需求文档中的格式描述。这是"约定优于配置"（Convention over Configuration）原则在文档规范中的体现——**项目代码库中已形成的约定，其优先级高于任何文档中描述的规范要求**。

## 实践四步骤

1. **先读3-5份同类现有文档**：不是随便读，而是读同目录、同类型的文档
2. **总结其格式模式**：frontmatter有无、标题层级、表格风格、Mermaid使用、链接风格等
3. **按照已有模式编写新文档**：严格匹配现有风格，即使你认为有"更好"的方式
4. **如果发现spec描述与实际不一致**：以实际为准并修正spec，不要让spec与代码库脱节

## 关联到AGENTS.md启动协议

这一原则应整合进AGENTS.md的启动协议中，作为"文档编写前检查"步骤：
- 接到文档编写任务后，先定位目标目录
- 读取该目录下3-5份现有文档
- 总结风格模式
- 再开始编写

"读3份文档"的成本约2-3分钟，但可以避免数十个文档的批量返工。

## 关联洞察

- [finding-02-rules-doc-frontmatter-mismatch.md](finding-02-rules-doc-frontmatter-mismatch.md) — 违反此原则导致的具体问题
- [finding-04-write-before-observe-style.md](finding-04-write-before-observe-style.md) — 执行顺序错误的反模式
- [meta-02-context-compression-governance-domain-validation.md](meta-02-context-compression-governance-domain-validation.md) — 上下文压缩是忽略此步骤的认知根因
- [law-05-governance-building-five-steps.md](law-05-governance-building-five-steps.md) — 步骤③风格确认即此原则

---
*来源：[AI智能体数据安全治理复盘](../README.md)*
