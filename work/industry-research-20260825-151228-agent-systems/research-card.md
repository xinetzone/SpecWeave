# 研究参数卡

## 研究范围
- 用户原始请求：调研当下最好的 agent 系统
- 行业定义：AI Agent 系统行业——以 LLM 为核心、能自主调用工具完成任务的软件系统，包括开源框架、商业平台、编码 Agent、浏览器 Agent 及相关基础设施
- 地域：全球（重点关注美国、欧洲、中国市场）
- 资料截止日：2026-08-25
- 时间范围：以资料截止日可确认的最新完整年度（2025）及最新部分年度（2026年1-8月）为准
- 指定企业或焦点：用户未指定具体企业；选样原则为选择代表不同架构路线和市场定位的厂商

## 研究问题与章节
| 研究维度 | 核心问题 | 重要问题 |
|---|---|---|
| 宏观与政策 | 全球主要市场对 AI Agent 的监管政策框架走向 | MCP 治理变化对行业标准化的影响 |
| 市场规模 | 全球 AI Agent 系统市场规模和增长率 | 三大细分市场（编码/企业/浏览器）规模占比 |
| 产业链 | 产业链上下游结构如何划分 | MCP/A2A 协议在产业链中的角色 |
| 竞争格局 | 开源框架与商业平台竞争演变 | 厂商生态 Agent 战略差异 |
| 重点企业 | 五大厂商 Agent 战略差异化定位 | 编码 Agent 领域竞争差异 |

## 规划前行业发现线索（尚未核实）
- 状态：已跳过
- 原因：已有前序调研的279条事实数据作为充分当前变化线索，无需行业发现搜索

## 企业选择要求
- 选样原则：选择代表不同架构路线（图驱动/对话驱动/角色驱动/厂商原生）和市场定位（开源/商业/企业级）的厂商，覆盖开源框架生态和商业平台生态
- 当前竞争结构（待核实）：前序调研显示市场按厂商生态整合——LangChain/LangSmith（图驱动+可观测性）、OpenAI（Handoff+沙箱）、Google（ADK+Vertex AI）、Anthropic（Claude Code+MCP发起者）、Microsoft（MAF+Copilot Studio）
- 候选池状态：充足
- 待核实候选：
  1. LangChain（LangGraph+LangSmith）——图驱动框架+可观测性生态，主流结构锚点
  2. OpenAI（Agents SDK+Codex）——厂商原生+编码Agent，Handoff模型路线
  3. Anthropic（Claude Agent SDK+Claude Code+MCP发起者）——MCP生态+终端Agent路线
  4. Google（ADK+Vertex AI Agent Builder+A2A发起者）——多语言+图基工作流+A2A协议路线
  5. Microsoft（MAF+Copilot Studio+Semantic Kernel）——企业级+低代码路线

## 来源线索
- 宏观与政策：Linux Foundation Agentic AI Foundation 公告、MCP 一周年规范更新、各主要市场监管机构公开文件
- 市场规模：Gartner/McKinsey/IDC 等 analyst 报告、上市公司财报、融资记录
- 产业链：各框架官方文档、MCP/A2A 协议规范、可观测性工具文档
- 竞争格局：GitHub 仓库数据、产品定价页、行业对比报告
- 重点企业：企业官方博客、GitHub releases、产品文档、融资新闻

## 需要在报告中保留的限制
- GitHub Stars 数据在不同来源和时间点存在差异
- 基准测试（SWE-Bench 等）存在数据污染风险，生产环境表现可能低于基准分数
- Agent 市场规模数据来源分散，口径不一致
- 编码 Agent 领域的快速提升部分得益于代码领域的客观正确性信号，不代表通用 Agent 能力同等提升
