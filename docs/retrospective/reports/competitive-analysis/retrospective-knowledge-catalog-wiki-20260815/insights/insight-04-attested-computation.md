---
type: Report
id: "kc-insight-04-attested-computation"
title: "洞察4：Attested Computation是知识领域的OpenAPI——从描述到可执行"
source: "../insight-extraction.md#洞察4attested-computation是知识领域的openapi从描述到可执行"
date: "2026-08-15"
archived_pattern: "../../../../patterns/architecture-patterns/verifiable-knowledge-claim.md"
tags:
  - attested-computation
  - openapi
  - verifiable-computation
  - agent-safety
maturity: "L1"
---
# 洞察4：Attested Computation是知识领域的OpenAPI——从描述到可执行

> ✅ **已萃取为模式**：[verifiable-knowledge-claim](../../../../patterns/architecture-patterns/verifiable-knowledge-claim.md)（可验证知识声明模式）

## 陈述（结论）

传统元数据对指标的表示是"自然语言+示例SQL"，OKF引入的`Attested Computation`类型要求**可执行+可验证**——明确runtime、显式声明parameters、提供executor运行说明+attester确定性验证代码。这与OpenAPI从"API文档"演进到"可执行API规范"是同一逻辑，是解决Agent SQL幻觉的可行路径。

## 反常识（挑战默认假设）

- ❌ 默认假设："指标定义清楚了（自然语言描述+例子），Agent就能正确使用"
- ✅ 反常识：自然语言描述永远有歧义。Agent读自然语言生成SQL的幻觉率极高——唯一可靠的方式是**参数化执行+独立验证**：生产者提供executor（Agent只能绑参数不能改逻辑），消费者在自己环境运行attester验证结果，不需要信任生产者。
- ❌ 默认假设："验证就是人看一眼对不对"
- ✅ 反常识：密码学思想在元数据领域同样适用——不需要信任对方，只要验证对方提供的证据。receipt（执行收据）+ attester（验证代码）的组合，让知识验证从"信任人"变成"验证代码"。

## 证据（来源）

Attested Computation核心要求：
1. 明确`runtime`（bigquery/dbt/python等）
2. 显式声明`parameters`（Agent只能绑定参数，不能修改逻辑）
3. 提供`executor`运行说明+`receipt`格式
4. 必须有确定性`attester`代码验证结果（无LLM调用、纯代码）
5. 业务概念文档通过Markdown链接引用，不直接内联SQL

历史对照：OpenAPI/Swagger的演进路径完全一致——从手写API文档（自然语言，容易过时和不一致）→ 可执行规范（可生成SDK、可验证、可mock）。

## 行动建议

1. **关键业务KPI**：从一开始就按Attested Computation格式定义，不要等出问题再补
2. **attester代码原则**：必须是确定性的、无LLM调用的纯代码，相同输入永远得到相同输出
3. **Agent集成OKF**：涉及数值问题优先找Attested Computation类型条目，而非自然语言描述
4. **扩展到其他知识类型**：同样的思想可扩展到策略验证、配置合规检查、数据质量校验等领域

## 关联模式

- **✅ 本洞察已萃取为**：[verifiable-knowledge-claim](../../../../patterns/architecture-patterns/verifiable-knowledge-claim.md)（可验证知识声明法）
- [可信度双轨制](../../../../patterns/methodology-patterns/research-knowledge/credibility-dual-track.md)
- [信任优先元数据法](../../../../patterns/architecture-patterns/trust-first-metadata.md)
