---
id: "agents-readme-subdirs"
title: ".agents 各子目录职责说明"
source: "README.md#各子目录职责说明"
x-toml-ref: "../.meta/toml/.agents/subdirectory-responsibilities.toml"
---
# .agents 各子目录职责说明

> 本文件为 [README.md](README.md) 的子模块，承载详细的子目录职责表。

| 目录 | 分层 | 职责 | 内容 |
|---|---|---|---|
| capabilities/ | Core | 渐进式披露三层架构规范与模板 | ARCHITECTURE.md(L2规范)、ONBOARDING-TEMPLATE.md、REGISTRY-TEMPLATE.md |
| capability-registry/ | Core | L1能力注册中心详细索引 | scripts/skills/commands/workflows/protocols/rules/knowledge 分类索引 |
| roles/ | Core | 智能体角色定义与协作场景 | 7个核心角色定义（orchestrator/architect/developer/reviewer/tester/co-founder/team-admin），及协作场景 |
| modules/ | Core | 自我演进模块定义 | 8个自我演进子智能体（感知/认知/执行/治理四层闭环） |
| prompts/ | Core | 系统提示词与 few-shot | 按角色分子目录，每个含 system-prompt.md 与 few-shot.md |
| tools/ | Core | 工具调用规范（规范层） | 文件操作、代码执行、搜索、通信四类工具的使用规范（不是工具实现） |
| protocols/ | Core | 协作协议 | 会话启动、任务交接、消息传递、冲突解决、PDR前置阅读、三层路由、应用生命周期、临时依赖、onboarding |
| rules/ | Core | 规则体系 | 阶段守卫（含运行时）、硬编码治理、数据安全、内容敏感度预检、RACI规范、AI编码准则、元文档优先、三阶段递进、修复闭环、frontmatter标准、CMD-LOG规范等133+原子化规则文件 |
| workflows/ | Core | 标准工作流 | 功能开发、代码审查、测试流程（含 Mermaid 流程图） |
| templates/ | Core | 模板资产 | 任务模板、交接模板、Mermaid模板 |
| teams/ | Core | 团队管理功能模块 | 团队管理员角色、团队生命周期、权限系统、4个专项团队（flexloop/mermaid/home-assistant/trae-edge-case） |
| systems/ | Core | 系统级架构定义 | 提示词萃取系统等架构文档 |
| cases/ | Core | 项目复用案例 | agentforge-adoption.md 等案例文档 |
| commands/ | Core | 标准化指令集（规范层） | 13个指令集：复盘、洞察、第一性原理、萃取、导出报告、原子化、原子提交、Mermaid管理、文件创建、Home Assistant、对抗性评审、方法论编排、知识沉淀 |
| worlds/ | Core | 团队协作执行与环境管理（规范层） | 多用户权限管理、协作编辑、变更追踪、版本控制、多环境配置、环境变量管理、资源隔离、环境状态监控 |
| checklists/ | Core | 标准化检查清单 | 风险评分检查清单等可复用检查项 |
| scripts/ | Tools | 自动化脚本（实现层） | 341+Python脚本：check-*.py验证脚本、生成脚本、CI脚本、一次性修复工具；含tests/测试目录、lib/共享库（15+子模块）、mdi/（Markdown Interface解析/生成/验证）、sg_dashboard/（阶段守卫仪表盘）、forum_bot/（论坛自动化） |
| skills/ | Tools | Skill 技能门面（L1索引层） | 19个SKILL.md：ci-check/docgen/insight/mermaid/forum-posting/link-check/atomization/atomic-commit/retrospective/extraction/export-report/seven-concepts/check-duplication等，遵循五要素模型（<500行） |
| config/ | Tools | 工具配置文件 | discourse/agent-browser.json 等外部工具配置 |
