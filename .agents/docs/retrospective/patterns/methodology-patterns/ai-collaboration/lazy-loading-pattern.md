---
id: "lazy-loading-pattern"
title: "按需加载懒加载模式"
type: "methodology"
date: "2026-08-01"
maturity: "L2-validated"
source: "llm-token-optimization-research-cursor-copilot-postman"
related_patterns: ["progressive-optimization-pattern", "layered-caching-pattern", "progressive-context-disclosure"]
tags: ["LLM", "Token", "Lazy-Loading", "MCP", "Agent", "Context-Window"]
validation_count: 4
reuse_count: 0
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/retrospective/patterns/methodology-patterns/ai-collaboration/lazy-loading-pattern.toml"
---
> **来源**：萃取自Cursor、GitHub Copilot、Postman Claude Code插件等案例

# 按需加载懒加载模式（Lazy Loading / On-Demand Loading Pattern）

## 模式类型

方法论模式

## 成熟度

L2 已验证（Cursor、GitHub Copilot、Postman等多个案例验证）

## 适用场景

- 代码助手/IDE插件（MCP工具多，工具定义本身占大量token）
- Agent/智能体（多工具调用，不需要一开始加载所有工具）
- RAG系统（不需要一开始把所有文档都塞进上下文）
- 长上下文场景（大部分上下文信息当前步骤用不到）
- 任何"预加载了大量可能用不到的信息"的场景

**不适用于**：工具少（<5个）、上下文短的简单场景——全量加载更简单，按需加载增加复杂度反而不值。

## 问题背景

传统方式是"预加载所有可能需要的信息"：代码助手每轮发送所有MCP工具定义，Agent每轮加载所有工具schema，结果是工具定义就占55,000 tokens（MindStudio数据），大部分工具当前轮根本用不到。按需加载的核心是"初始只给元数据，真正需要时才加载完整内容"，从"预加载全量"转向"动态发现按需拉取"。

核心优势：这比"加载了再压缩"更高效，因为从源头避免了O(n²)计算——根本就不把没用的token送进来。对比：全量加载O(n) → 按需加载O(k)，k是实际需要的token，k << n。

## 核心规则

### 规则1：元数据与完整内容分离

将资源分为两层：
- **轻量元数据层**：名称、一句话描述、类型、ID——这部分初始加载（约100 token/工具）
- **完整内容层**：参数schema、详细说明、示例、代码——这部分按需加载（约500-2000 token/工具）

代码助手MCP示例：
- 初始发送：工具名称+一句话描述（约100 token/工具）
- 需要调用时：加载完整参数schema（约500-2000 token/工具）

### 规则2：渐进式披露架构

三层渐进式加载：
- Level 0（启动时加载）：核心元数据（名称、描述）
- Level 1（相关时加载）：当前任务可能相关的资源详细信息
- Level 2（需要时加载）：真正要调用/使用时才加载完整内容

Cursor实践："少给前置细节，让Agent按需拉取相关上下文"。

### 规则3：长输出文件化而非截断

- 工具返回、命令输出、历史对话等长内容不要直接截断
- 写入临时文件，给Agent文件引用和读取能力
- Agent可以先看tail/head（末尾/开头），需要时再读取完整内容
- 这保留了完整信息可追溯，又不填满上下文窗口

### 规则4：动态上下文发现

- 不预先决定哪些上下文相关
- 提供搜索/检索能力，让Agent根据当前任务主动拉取相关信息
- 代码助手场景：基于编辑文件、打开标签、轻量嵌入模型自动选择最相关文件

## 效果数据（行业经验估算，实际效果以测量为准）

| 应用场景 | 全量加载token | 按需加载token | 节省比例 | 案例验证 |
|---------|--------------|--------------|---------|---------|
| MCP多工具场景（10+工具） | ~55,000 tokens | ~5,000-15,000 tokens | 46.9%+ | Cursor官方博客 |
| 长工具输出（10K tokens） | 10,000 tokens（截断丢失） | ~200 tokens（文件引用） | 98%+ | Cursor动态上下文 |
| 代码库上下文 | 全量文件加载 | 相关文件按需拉取 | 60-80% | GitHub Copilot |
| Postman技能加载 | 4,760 tokens（全量） | 1,930 tokens（渐进式） | 60% | Postman官方插件 |

**典型案例验证**：
- Cursor：MCP场景总Agent token降低46.9%，统计显著，"MCP数量越多节约越多"
- GitHub Copilot：工具搜索（Tool Search）模式，初始仅发送轻量元数据，参数schema在需要时才加载
- Postman Claude Code插件：渐进式披露，最大技能触发减轻60%（4,760→1,930 tokens）

## 实施检查清单

- [ ] 资源是否已分离为轻量元数据层和完整内容层？
- [ ] 初始加载是否只包含元数据（名称+一句话描述）？
- [ ] 是否实现了三层渐进式加载（L0元数据→L1相关→L2完整）？
- [ ] 长输出是否文件化而非截断，且Agent有文件读取能力？
- [ ] 是否提供了动态搜索/检索能力让Agent主动拉取上下文？
- [ ] 元数据描述是否清晰，Agent能判断什么时候该加载什么？
- [ ] 工具数量<5个时是否避免过度设计（直接全量加载）？

## 反例警示

| 错误做法 | 后果 |
|---------|------|
| 需要时找不到：按需加载机制设计不好 | Agent不知道有这个工具/资源，该用的时候没加载 |
| 加载太频繁：每个小步骤都重新加载 | 来回加载的开销反而更大 |
| 元数据不清晰：元数据描述不清楚 | Agent无法判断什么时候该加载什么 |
| 文件化但不给读取能力：把长内容写文件了 | Agent没有读取文件的工具/权限，等于白做 |
| 简单场景过度设计：工具少（<5个） | 全量加载更简单，按需加载增加复杂度反而不值 |
| 截断长内容而非文件化 | 信息丢失，Agent无法获取完整内容做出正确判断 |

## 与现有模式的关系

- **progressive-context-disclosure**：本模式是该模式在Token优化领域的具体化应用，专注于上下文窗口消耗控制
- **layered-caching-pattern**：本模式解决"加载什么"的问题，分层缓存解决"重复加载"的问题，两者互补

## 迁移验证（跨领域可复用性）

懒加载/按需加载是计算机科学中经典设计模式，可迁移到：

1. **操作系统虚拟内存管理**：虚拟地址空间（元数据）vs 物理页帧（完整内容）→ 按需分页（Demand Paging）→ 工作集模型，原理完全一致
2. **网页前端资源加载**：路由配置/Manifest（元数据）vs JS/CSS代码（完整内容）→ 代码分割+路由懒加载→图片懒加载→动态import()
3. **微服务架构服务发现**：服务注册中心元数据（服务名、地址）→ 调用时才发现和建立连接→按需调用、熔断降级

> **关联模块**：
> - [progressive-optimization-pattern.md](progressive-optimization-pattern.md)
> - [layered-caching-pattern.md](layered-caching-pattern.md)
> - [progressive-context-disclosure.md](progressive-context-disclosure.md)
