---
id: "finding-rules-doc-frontmatter-mismatch"
source: "../insight-extraction.md#反模式1规则文档加toml-frontmatter"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/process-and-compliance/retrospective-ai-agent-data-security-governance-20260629/insights/finding-02-rules-doc-frontmatter-mismatch.toml"
---
# 发现2（反模式1）：规则文档误加TOML frontmatter

→ 已落地修正：Task描述中增加文档风格确认步骤

## 表现

为`.agents/rules/`下的治理规则文档添加TOML frontmatter（id/date/type/source字段），与现有规则文档风格不一致。初期按照spec中的NFR-1描述添加，后来发现`.agents/rules/`下所有现有文档均不使用frontmatter，不得不回退修正。

## 根因分析

1. **上下文压缩导致认知视野收窄**：编写新文档时注意力集中在"写内容"上，忽略了"看风格"
2. **Spec中的NFR描述产生误导**：NFR-1明确写了"TOML frontmatter"，但该描述未与实际代码库对齐验证
3. **错误假设**：复盘报告和Spec文档都使用frontmatter，形成"所有文档都有frontmatter"的错误假设

## 三类文档frontmatter差异

| 文档类型 | 目录 | frontmatter |
|---------|------|------------|
| 治理规则文档 | `.agents/rules/` | 无frontmatter |
| Spec文档 | `.trae/specs/` | 有YAML/TOML frontmatter |
| 复盘报告 | `docs/retrospective/` | 有TOML frontmatter |

## 改进方向

1. 在spec模板中增加"文档风格确认"检查项，要求在编写任何新文档前先读取3份以上同类文档确认格式规范
2. 将"读取3份同类文档确认风格"作为每个文档编写Task的第一个子步骤
3. 写完第一个文档后立即进行风格验证，而非等全部写完再检查

## 关联洞察

- [meta-01-convention-over-configuration-docs.md](meta-01-convention-over-configuration-docs.md) — "约定优于配置"元原则
- [meta-02-context-compression-governance-domain-validation.md](meta-02-context-compression-governance-domain-validation.md) — 上下文压缩导致认知收窄是根因
- [finding-04-write-before-observe-style.md](finding-04-write-before-observe-style.md) — 先写后查风格的执行问题
- [law-05-governance-building-five-steps.md](law-05-governance-building-five-steps.md) — 步骤③风格确认是防范手段

---
*来源：[AI智能体数据安全治理复盘](../README.md)*
