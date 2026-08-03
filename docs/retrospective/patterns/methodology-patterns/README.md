---
id: "methodology-patterns-index"
title: "方法论模式库索引"
date: "2026-07-04"
---
# 方法论模式库索引

> 本目录存放经过七概念方法论编排（R→I→E→V）萃取的可复用方法论模式。每个模式均通过G1-G4质量门与V对抗审查。

## 模式清单

| 模式ID | 模式名称 | 成熟度 | 验证次数 | 复用次数 | 触发场景 |
|--------|---------|--------|---------|---------|---------|
| bp-dual-layer | [双层分析报告结构](dual-layer-analysis-report.md) | L2-validated | 3 | 15 | 需要对网页/文章/技术内容进行"既理解内容又提炼洞察"的双目标分析时 |
| bp-subagent-std | [子代理分析任务标准化指令](subagent-standardized-instruction.md) | L2-validated | 3 | 3 | 需要委派子代理执行复杂多步骤分析任务时 |
| bp-content-funnel | [内容漏斗分析模式](content-funnel-analysis.md) | L1-draft | 1 | 1 | 需要对技术文章/行业报告进行递进式深度分析时 |
| bp-integration-over-invention | [整合优于发明模式](integration-over-invention.md) | L1-draft | 1 | 1 | 存在多个互补开源工具但组合使用门槛高时 |
| bp-offline-first-architecture | [离线优先架构模式](offline-first-architecture.md) | L1-draft | 1 | 1 | 系统需要在离线状态下保证完整功能可用时 |
| bp-lowering-barriers-creates-markets | [降低门槛即创造市场模式](lowering-barriers-creates-markets.md) | L1-draft | 1 | 1 | 技术方案成熟但安装配置复杂度阻碍大规模采用时 |
| bp-tech-article-to-wiki-batch | [技术文章Wiki化批量生成](tech-article-to-wiki-batch-generation.md) | L2-validated | 5 | 5 | 需要将长技术文章/教程转化为原子化Wiki结构时 |
| bp-knowledge-compilation | [知识编译模式](knowledge-compilation.md) | L1-draft | 2 | 1 | 高频深度使用的结构化知识源（技术书籍/手册/规范）需要比RAG更高的token效率时。[案例：七概念方法论编译](../../../.agents/skills/seven-concepts-cmd/references/compiled-methodology.md)（10个源文件→365行~4800token自包含Skill） |

## 成熟度等级说明

| 等级 | 名称 | 标准 |
|------|------|------|
| L1-draft | 假设性模式 | 单案例,待验证 |
| L2-validated | 已验证模式 | ≥2案例,已在本项目验证 |
| L3-mature | 成熟模式 | 跨项目验证,有明确边界条件 |
| L4-optimized | 优化模式 | 经过对抗审查,工具化/自动化支持 |

## 模式入库流程

1. **R阶段（复盘）**:采集案例事实,≥2个独立案例
2. **I阶段（洞察）**:提炼跨案例共性,形成四元组洞察（现象+根因+影响+建议）
3. **E阶段（萃取）**:按标准模板结构化模式（触发场景+核心做法+反模式+检验标准+迁移示例）
4. **V阶段（对抗审查）**:多视角攻击验证,≥5条审查意见,采纳≥2条修正
5. **入库**:创建模式文档+更新本索引+创建TOML元数据

详见 [萃取指令集](../../../../.agents/commands/extraction.md) 与 [七概念方法论编排指令集](../../../../.agents/commands/seven-concepts.md)。

## 关联资源

- 七概念方法论体系索引（如存在，待创建）
- [网页内容→结构化学习笔记 模式库](../../reports/milestone/web-content-learning-notes-patterns-20260801.md)
- [萃取指令集](../../../../.agents/commands/extraction.md)
- [七概念方法论编排指令集](../../../../.agents/commands/seven-concepts.md)
