# LongCat-2.0 Agent 能力实测 Wiki Spec

## 1. 资源来源
- 原始URL：https://mp.weixin.qq.com/s/ymt9W64FD5IwCDNeQFuheA
- 资源类型：微信公众号文章
- 作者/来源：郭震AI（郭震）
- 提取时间：2026-07-04

## 2. 核心主题与目标
- 一句话总结：美团 LongCat-2.0（1.6T参数MoE模型）接入 Claude Code，从零开发完整 BI 数据看板项目的 Agent 能力实测教程
- 学习目标：
  1. 理解 LongCat-2.0 模型的架构特点（MoE、稀疏注意力、国产算力训练）
  2. 掌握 LongCat-2.0 接入 Claude Code 的完整配置方法
  3. 了解 Agent 编程的 loop engineering 概念与实践
  4. 对比 LongCat-2.0 与其他模型（DeepSeek-V4、GPT-5.5）的 token 效率差异
  5. 理解 AI 模型从"写代码片段"到"项目级开发"的能力演进
- 目标读者：对 AI Agent 编程感兴趣的中高级开发者，特别是关注国产大模型实际编程能力的用户
- 前置知识：了解 Claude Code 基本用法、Python/Flask 基础、前端开发基础

## 3. 信息架构设计
### 章节划分
| 文件 | 章节标题 | 核心内容 |
|------|---------|---------|
| 00-overview.md | 概述 | 背景、学习目标、导航 |
| 01-core-concepts.md | LongCat-2.0 核心概念 | MoE架构、稀疏注意力、1.6T参数、国产算力训练、Agent原生设计 |
| 02-claude-code-integration.md | Claude Code 接入指南 | API Key获取、环境变量配置、模型切换步骤 |
| 03-bi-dashboard-demo.md | BI数据看板实战 | 项目需求、开发流程、任务拆解、报错修复、最终成果 |
| 04-token-efficiency.md | Token效率对比 | LongCat-2.0 vs Codex+GPT-5.5 消耗对比、缓存机制 |
| 05-loop-engineering.md | Loop Engineering 方法论 | 概念解析、迭代修复流程、与传统编程的对比 |
| 06-summary.md | 总结 | 核心要点回顾、takeaway、下一步建议 |
| 07-faq.md | FAQ | 常见问题与解答 |
| 08-resources.md | 资源链接 | 原文、LongCat平台、相关资源 |

### 逻辑组织方式
- [x] 线性递进（适合教程类）：从概念→配置→实战→效率分析→方法论总结

### 原子化决策（必须明确选择）

**判断标准**（满足任一条件即建议拆分）：

| 判断维度 | 拆分阈值 | 本wiki预估 |
|---------|---------|-----------|
| 内容长度 | 预计>300行建议拆分，<200行可保持单文件 | 预计约400-500行（9个章节，内容丰富） |
| 章节独立性 | 各章节是否可单独阅读/引用？ | 是（概念、配置、实战、效率对比均可独立阅读） |
| 未来扩展 | 是否预期会持续新增章节/内容？ | 是（LongCat后续版本更新、更多模型对比可追加） |
| 复用需求 | 单个章节是否会被其他文档引用？ | 是（loop engineering 方法论、Claude Code配置技巧可被其他wiki引用） |

**决策结果**：
- [x] **需要原子化拆分**：采用"索引页(longcat-agent-learning-wiki.md) + 目录(longcat-agent-learning-wiki/) + 数字前缀原子文件"结构，进入L5原子化拆分阶段