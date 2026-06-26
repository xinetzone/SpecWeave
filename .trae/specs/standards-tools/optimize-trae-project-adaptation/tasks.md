# Tasks

- [x] Task 1: 梳理 Trae 在本项目中的当前使用场景
  - [x] SubTask 1.1: 阅读 AGENTS.md、`.agents/` 索引、`.trae/specs/` 目录结构、知识库和复盘体系，提取 Trae 已承载的工作流
  - [x] SubTask 1.2: 按规格驱动开发、规则路由、文件编辑、知识检索、复盘萃取、验证脚本、MCP/Skill、子代理协作八类场景归纳现状
  - [x] SubTask 1.3: 区分 Trae 原生能力、项目自建规范和可通过配置增强的能力

- [x] Task 2: 分析 Trae 当前应用局限性
  - [x] SubTask 2.1: 结合知识库中“跳过 AGENTS.md 启动协议”故障案例，分析上下文优先级、Skill 竞争和输出偏移问题
  - [x] SubTask 2.2: 分析规则分散、规格与实现脱节、验证人工化、历史经验复用成本、子代理边界和 Windows 终端约束
  - [x] SubTask 2.3: 为每项局限性建立“表现—影响—根因—优化方向”四列表

- [x] Task 3: 设计 Trae 配置优化方案
  - [x] SubTask 3.1: 设计 Rules 分层方案，覆盖全局强约束、任务路由、角色规则、工具规则和验证规则
  - [x] SubTask 3.2: 设计 Spec 模式模板与 `.trae/specs/` 使用规范，确保规格、任务与检查清单闭环
  - [x] SubTask 3.3: 设计 Skill、Slash 命令、MCP、子代理和终端使用配置建议
  - [x] SubTask 3.4: 设计任务完成后的验证门禁，包括规格一致性、链接、路径、Git 忽略规则和测试检查

- [x] Task 4: 设计 Trae 功能扩展建议
  - [x] SubTask 4.1: 提出项目专属 Skill 设计，包括触发条件、输入、输出、依赖规范和验证方式
  - [x] SubTask 4.2: 提出短指令库设计，映射 `/复盘`、`/洞察`、`/萃取`、`/验证`、`/同步规格` 等高频流程
  - [x] SubTask 4.3: 提出知识库检索入口、复盘生成工作流、任务总结沉淀和 Trae 使用指标统计方案
  - [x] SubTask 4.4: 提出多代理协作模板，明确何时使用主代理、搜索子代理、实现子代理和验证子代理

- [x] Task 5: 编写最佳实践指南与实施路线
  - [x] SubTask 5.1: 编写 Trae 端到端最佳实践，覆盖任务开始、规格设计、上下文读取、工具选择、文件编辑、实现、验证、复盘和知识沉淀
  - [x] SubTask 5.2: 编写常见错误规避清单，覆盖启动协议、文件读取、工具使用、临时依赖、规格阶段边界等
  - [x] SubTask 5.3: 按立即可做、短期配置、中期扩展、长期度量组织落地路线
  - [x] SubTask 5.4: 为每项建议补充目标、操作步骤、涉及文件、验证方式和预期收益

- [x] Task 6: 验证优化方案质量
  - [x] SubTask 6.1: 对照 checklist.md 检查覆盖范围、可操作性、项目资产对齐和风险约束
  - [x] SubTask 6.2: 检查方案中所有文件路径与项目实际结构一致
  - [x] SubTask 6.3: 检查文档是否明确区分 Trae 原生能力与项目自建能力
  - [x] SubTask 6.4: 若后续生成正式方案文档，确认其不与 README.md、AGENTS.md 和 `.agents/` 职责边界冲突

# Task Dependencies

- Task 2 依赖 Task 1
- Task 3 依赖 Task 1、Task 2
- Task 4 依赖 Task 1、Task 2
- Task 5 依赖 Task 3、Task 4
- Task 6 依赖 Task 5
- Task 3 与 Task 4 可在 Task 2 完成后并行推进
