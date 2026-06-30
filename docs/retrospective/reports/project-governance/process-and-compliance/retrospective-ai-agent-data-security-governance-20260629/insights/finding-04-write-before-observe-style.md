+++
id = "finding-write-before-observe-style"
date = "2026-06-29"
type = "insight"
scope = "anti-pattern,execution,process,convention"
source = "../insight-extraction.md#反模式3先写文档后查风格"
archived_to = "已落地修正：Task第一步强制读取现有文档"
+++

# 发现4（反模式3）：先写文档后查风格

→ 已落地修正：每个文档编写Task第一步为"读取3份同类文档确认风格"

## 表现

按照spec描述直接开始编写文档，未先读取现有同类文档确认风格，等写完2-3个文档后才发现frontmatter问题，需要回退修正。

## 根因分析

1. **"完成焦虑"**：急于开始"真正的工作"（写内容），将"读现有文档"视为非必要的准备工作
2. **过度自信**：认为自己已经了解项目风格（毕竟之前做过阶段守卫复盘），不需要再确认
3. **Spec描述的"权威光环"**：认为spec中写了的就一定是对的，不需要与现实对齐验证

## 与finding-02的区别

- **finding-02（frontmatter错误）**：是结果——具体是什么问题
- **finding-04（先写后查）**：是过程——为什么会发生这个问题（执行顺序错误）

## 改进方向

1. 将"读取3份同类文档确认风格"作为每个文档编写Task的第一个子步骤，写入Task描述中，强制执行
2. 写完第一个文档后立即进行风格验证，而非等全部写完再检查
3. 保持"spec是参考而非教条"的认知，发现不一致时及时修正spec
4. 将风格确认时间计入估算——读3份文档约2-3分钟，但可以避免30+分钟的返工

## 关联洞察

- [meta-01-convention-over-configuration-docs.md](meta-01-convention-over-configuration-docs.md) — "约定优于配置"元原则
- [finding-02-rules-doc-frontmatter-mismatch.md](finding-02-rules-doc-frontmatter-mismatch.md) — 先写后查导致的具体问题
- [meta-02-context-compression-governance-domain-validation.md](meta-02-context-compression-governance-domain-validation.md) — 上下文压缩是深层根因
- [law-05-governance-building-five-steps.md](law-05-governance-building-five-steps.md) — 步骤③风格确认是正确流程

---
*来源：[AI智能体数据安全治理复盘](../README.md)*
