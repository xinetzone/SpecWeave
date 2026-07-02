---
id: "architecture-priority-insight-c"
title: "洞察 C：架构重构应该从\"瓶颈层\"开始，而非\"最容易改的层\""
source: "insight-extraction.md#洞察-c"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/insight-extraction/retrospective-architecture-priority-20260629/insights/insight-c-bottleneck-first-refactoring.toml"
---
# 洞察 C：架构重构应该从"瓶颈层"开始，而非"最容易改的层"

**现象**：当前架构成熟度评估显示能力发现层是 L0（唯一完全缺失的层），是全局瓶颈。

**深层洞察**：
- 架构成熟度呈"倒瓶颈"分布：上层（规范/角色）很成熟，底层（能力发现）完全缺失
- 这意味着即使其他层做得再好，Agent 仍然无法高效使用系统能力
- 重构优先级应该严格按「瓶颈优先级」而非「实施难度」排序：
  - ❌ 错误做法：先做最容易的（比如给脚本加SKILL），因为见效快
  - ✅ 正确做法：先建注册中心（基础设施），再封装能力到注册中心
- Firecrawl 的产品演进也印证了这一点：先有 API（Keyless入口），再做 Scrape/Crawl/Map/Extract 等能力

**可复用模式**：**瓶颈优先重构法（Bottleneck-First Refactoring）**
> 1. 用成熟度分层模型（L0-L4）评估各架构层
> 2. 找到最低成熟度的层（全局瓶颈）
> 3. 所有重构围绕解除这个瓶颈展开
> 4. 瓶颈解除后重新评估，找下一个瓶颈
> 5. 非瓶颈层的优化推迟到瓶颈解除后
