# 概念文档

## 核心概念（Concept）

* [01 — Protocol边界与最小生命周期](01-protocol-boundary-lifecycle.md) — 三层概念区分、Runtime Protocol定义、最小生命周期、现有协议收敛对比
* [02 — 执行模型：Agent如何跑起来（Part 1）](02-execution-model.md) — Runtime Loop承载方式、编排协议模式、Agent Harness、跨框架映射、Workspace/Sandbox
* [03 — 状态管理：生产级Agent的分水岭（Part 2）](03-state-management.md) — 持久化光谱、状态五层分层、并发Run策略、Checkpoint模型对比、Schema演进
* [04 — 中断与错误恢复](04-interrupt-error-recovery.md) — Human-in-the-Loop基础设施、Error-as-Data哲学、Checkpoint回滚机制
* [05 — 工具协议与流式输出（Part 3）](05-tools-streaming.md) — MCP详解、工具协议独立分层、可恢复流、任务事件流vs token打字机
* [06 — 多Agent协作：最碎片化，也最不该过早押注（Part 4）](06-multi-agent.md) — 五种编排模式对比、跨框架映射、设计决策分析、"先做好单Agent"建议
* [08 — Protocol对象映射与设计原则](08-protocol-design-principles.md) — 完整对象映射表、九条设计原则、Protocol与Runtime边界划分

## 参考文档（Reference）

* [07 — 可观测性与可评测性：看见问题与评价质量](07-observability-evaluation.md) — Trace最小语义模型、三类观测数据、评测闭环、质量改进链路
* [09 — 跨维度分析与行业趋势](09-cross-dimensional-analysis.md) — 设计决策持久性判断、收敛趋势预测、开发者投入方向建议、从零设计建议
* [09 — 框架对比：九条设计原则遵循度评估](09-framework-comparison.md) — 五大框架星级评分对比、选型决策矩阵、实践启示
* [10 — 内容评估与个人见解](10-content-evaluation.md) — 原文价值评估、Agent基础设施演进趋势思考
* [10 — 企业级Agent Runtime选型指南](10-enterprise-selection-guide.md) — 企业级五大公理、五大扩展维度、分层选型架构、典型场景推荐、可交互决策矩阵
