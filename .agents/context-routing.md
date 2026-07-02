---
id: "context-routing"
source: "AGENTS.md#上下文路由表"
x-toml-ref: "../.meta/toml/.agents/context-routing.toml"
---
# 上下文路由表

本文件是智能体启动协议步骤 2 的核心依据，定义任务类型与必读规范入口的映射关系。所有智能体在执行任务前必须查阅本表，确定需要加载的规范文件。

## 🧭 vendor 方法论资产（任务类型预检·必查）

> 以下资产位于 vendor 子模块中，是对应任务类型最权威的方法论来源。**无论当前工作目录是否在 vendor/ 内，只要任务类型命中就必须读取。** 这防范了"就近直觉"偏差——只看工作目录附近文件而忽略 vendor 中更成熟的方法论资产。

| 任务类型 | 必读入口 | 为什么必须读 |
|---|---|---|
| Skill 创建/优化/调试 | [vendor/flexloop/apps/chaos/.agents/skills/skill-creator/SKILL.md](../vendor/flexloop/apps/chaos/.agents/skills/skill-creator/SKILL.md) + [rules/skill-development.md](rules/skill-development.md)（SpecWeave补充规范） | Skill 开发方法论权威来源：description触发词优化、渐进式披露、长度控制、Why解释原则；补充规范增加三层路由合规、五要素模型、双方案模式、资产盘点、验证清单等SpecWeave特有要求 |
| Skill 目录结构与规范 | [vendor/flexloop/apps/chaos/.agents/rules/skills.md](../vendor/flexloop/apps/chaos/.agents/rules/skills.md) | Skill 的SKILL.md格式、目录组织、验证机制等规范定义 |
| 跨项目子模块协同 | [VENDOR-INTEGRATION.md](VENDOR-INTEGRATION.md)（边界划分/版本控制/更新同步/测试隔离/模式萃取）+ [vendor/AGENTS.md](../vendor/AGENTS.md) | 三层路由体系与 vendor 子模块协作规范 |

## 📋 常规任务路由

| 任务类型 | 必读入口 |
|---|---|
| Skill 创建/优化/调试（SpecWeave 主权区补充规范） | [rules/skill-development.md](rules/skill-development.md)（五要素模型、双方案模式、资产盘点、验证清单） |
| 能力注册与发现中心（渐进式披露三层架构规范与模板） | [capabilities/](capabilities/)（L0 ONBOARDING <100行 / L1 SKILL+REGISTRY <500行 / L2 深度文档不限） |
| 角色定义、职责分工 | [roles/](roles/) |
| 角色协作场景、触发条件 | [roles/collaboration-scenarios.md](roles/collaboration-scenarios.md) |
| 自我演进模块定义 | [modules/](modules/) |
| 系统提示词、few-shot | [prompts/](prompts/) |
| 工具调用规范 | [tools/](tools/) |
| 协作协议、通信机制 | [protocols/](protocols/) |
| 标准工作流 | [workflows/](workflows/) |
| 任务与交接模板 | [templates/](templates/) |
| 团队管理、权限系统、角色创建 | [teams/](teams/) |
| flexloop 子模块治理团队（版本管理/边界合规/沙箱安全/模式萃取） | [teams/flexloop-team.md](teams/flexloop-team.md) |
| flexloop 团队工作流操作手册（详细步骤/验证清单/应急处理） | [teams/flexloop-team-operations.md](teams/flexloop-team-operations.md) |
| Trae 边界情况处理（IDE集成/论坛操作/工具链/Work） | [teams/trae-edge-case-handler.md](teams/trae-edge-case-handler.md) |
| Mermaid图表专项团队（模板/检查/协作/质量扫描） | [teams/mermaid-team.md](teams/mermaid-team.md) |
| 团队协作执行、环境管理 | [worlds/](worlds/) |
| Git 忽略规则验证 | [scripts/check-gitignore.py](scripts/check-gitignore.py) |
| vendor 目录合规性验证 | [scripts/check-vendor.py](scripts/check-vendor.py)（`--deep` 执行 submodule 深度集成验证：初始化状态、工作树清洁度、元数据一致性、非法引用、测试隔离） |
| 链接有效性验证与自动修复 | [skills/link-check-cmd/](skills/link-check-cmd/) → [scripts/check-links.py](scripts/check-links.py)（`--fix` 自动修复相对路径层级错误、绝对路径转换；`--check-external` 检查外部 URL 可达性，结果缓存7天） |
| 文件路径迁移 | [scripts/check-move.py](scripts/check-move.py) |
| 角色权限验证 | [scripts/check-role-permissions.py](scripts/check-role-permissions.py) |
| 派生产物溯源 | [scripts/check-source-traceability.py](scripts/check-source-traceability.py) |
| 阶段守卫日志分析 | [scripts/check-stage-guardrails.py](scripts/check-stage-guardrails.py)（`--log-file <path>` 分析SG-LOG/PDR-LOG，检测拦截/跳转/缺失异常；`--demo` 演示） |
| 阶段守卫日志可视化仪表盘 | [scripts/generate-sg-dashboard.py](scripts/generate-sg-dashboard.py)（`--demo` 生成8会话示例仪表盘；默认扫描 `.agents/logs/` 聚合多会话日志输出HTML到 `.agents/reports/sg-dashboard.html`；`--json` 输出JSON数据） |
| 规格一致性验证 | [scripts/check-spec-consistency.py](scripts/check-spec-consistency.py) |
| Spec 全局看板与7主题分类体系 | [.trae/specs/README.md](../.trae/specs/README.md)（创建新 spec 前必读：归类决策树、主题边界定义、命名规范） |
| Spec 主题目录看板 | [.trae/specs/](../.trae/specs/)（core-foundation/roles-governance/standards-tools/readme-branding/docs-restructure/retrospectives-insights/migration-archival 各主题 README.md） |
| 文档索引与看板生成（导航/看板/应用清单） | [skills/docgen-cmd/](skills/docgen-cmd/) → [scripts/docgen.py](scripts/docgen.py)（nav/dashboard/apps/all 子命令，标记区域幂等覆盖；旧脚本 generate-nav.py/generate-dashboard.py/generate-apps-index.py 均为向后兼容包装） |
| 原子化操作一键收尾 | [skills/atomization-finalize-cmd/](skills/atomization-finalize-cmd/) → [scripts/finalize-atomization.py](scripts/finalize-atomization.py)（原子化/文件移动后自动断链修复、导航更新、看板刷新，支持dry-run） |
| 文件引用反向索引 | [scripts/build-ref-index.py](scripts/build-ref-index.py)（构建 `{目标:[引用方]}` 索引，移动/删除文件前查询受影响范围） |
| 测试骨架生成 | [scripts/generate-tests.py](scripts/generate-tests.py) |
| 项目脚手架初始化 | [scripts/agents.py](scripts/agents.py) init |
| 共享工具库 | [scripts/lib/](scripts/lib/) |
| CI 综合检查（8步流水线） | [skills/ci-check-cmd/](skills/ci-check-cmd/) → [scripts/ci-check.ps1](scripts/ci-check.ps1) / [scripts/ci-check.sh](scripts/ci-check.sh)（提交前必跑，跨平台双版本） |
| 跨文件重复代码检测 | [skills/check-duplication-cmd/](skills/check-duplication-cmd/) → [scripts/check-duplication.py](scripts/check-duplication.py)（N元语法指纹检测≥10行重复，新增脚本前必跑） |
| 原子化覆盖率预检 | [scripts/check-atomization-coverage.py](scripts/check-atomization-coverage.py) |
| 原子化内容一致性 | [scripts/check-atomization-duplication.py](scripts/check-atomization-duplication.py) |
| 复盘报告归类验证 | [scripts/check-report-categorization.py](scripts/check-report-categorization.py) |
| 技术知识库查阅 | [docs/knowledge/README.md](../docs/knowledge/README.md) |
| 复盘体系与可复用模式 | [docs/retrospective/README.md](../docs/retrospective/README.md) |
| 可复用模式库（架构/代码/方法论） | [docs/retrospective/patterns/](../docs/retrospective/patterns/) |
| 资产清单与复用指南 | [docs/retrospective/assets/asset-inventory.md](../docs/retrospective/assets/asset-inventory.md) |
| 任务执行总结 | [docs/task-summaries/](../docs/task-summaries/) |
| 提示词工程模式 | [docs/retrospective/prompt-extraction.md](../docs/retrospective/prompt-extraction.md) |
| 提示词萃取系统 | [prompt_extraction/](../prompt_extraction/) |
| 提示词萃取系统架构 | [systems/prompt-extraction.md](systems/prompt-extraction.md) |
| 项目复用案例 | [cases/agentforge-adoption.md](cases/agentforge-adoption.md) |
| 指令集（复盘/洞察/导出报告/原子化/原子提交/Mermaid图表管理） | [commands/](commands/) |
| 硬编码治理规则体系 | [rules/](rules/) |
| 硬编码识别与判断 | [rules/identification-standards.md](rules/identification-standards.md) |
| 硬编码替代方案查找 | [rules/alternatives-guide.md](rules/alternatives-guide.md) |
| 硬编码例外申请与审批 | [rules/allowable-scenarios.md](rules/allowable-scenarios.md) |
| 硬编码检测与报告 | [rules/detection-and-reporting.md](rules/detection-and-reporting.md) |
| 硬编码治理规则执行 | [rules/enforcement-guidelines.md](rules/enforcement-guidelines.md) |
| AI编码行为准则（歧义澄清/简约设计/精确编辑/目标驱动） | [rules/ai-coding-guidelines.md](rules/ai-coding-guidelines.md)（一分钟速查表+正反例+工作流整合） |
| AI智能体互联数据安全治理体系 | [rules/data-security/README.md](rules/data-security/README.md)（分类分级/出境评估/脱敏加密/供应商管理/监控应急/角色职责） |
| 开发流程阶段守卫（阶段边界/拦截/审批/结构化日志SG-LOG） | [rules/stage-guardrails.md](rules/stage-guardrails.md) |
| 前置文档强制读取协议（必读清单/确认机制/结构化日志PDR-LOG） | [protocols/pre-document-reading.md](protocols/pre-document-reading.md) |
| 阶段守卫日志分析工具（SG-LOG/PDR-LOG离线检测拦截/跳转/缺失异常） | [scripts/check-stage-guardrails.py](scripts/check-stage-guardrails.py) |
| 阶段守卫运行时强制执行（状态管理/边界校验/拦截格式化/运行时门面） | [scripts/check-stage-guardrail-runtime.py](scripts/check-stage-guardrail-runtime.py) |
| 阶段守卫日志聚合可视化仪表盘 | [scripts/generate-sg-dashboard.py](scripts/generate-sg-dashboard.py) |
| 功能演进分类（新功能/扩展/重构三路径） | [workflows/feature-development.md](workflows/feature-development.md) |
| 应用开发生命周期（.temp/ → apps/ 迁移） | [protocols/app-development-workflow.md](protocols/app-development-workflow.md) |
| vendor 区域入口路由（三层路由中间层） | [vendor/AGENTS.md](../vendor/AGENTS.md)（子模块路由表、可用资产索引、跨边界调用规范、边界声明） |
| 外部子模块协同集成方案（git submodule） | [VENDOR-INTEGRATION.md](VENDOR-INTEGRATION.md)（边界划分、版本控制、更新同步、测试隔离、模式萃取） |
| 阶段守卫运行时使用指南（8阶段权限矩阵/CLI工具/SG-LOG示例） | [rules/stage-guardrails-guide.md](rules/stage-guardrails-guide.md) |
| 三层路由协议（SpecWeave→vendor→flexloop嵌套路由与异常分支） | [protocols/three-layer-routing.md](protocols/three-layer-routing.md) |
| CMD-LOG命令集执行日志规范（5大命令集结构化日志/事件枚举/解析正则） | [rules/cmd-log-specification.md](rules/cmd-log-specification.md) |
| 能力边界声明 | [capability-boundaries.md](capability-boundaries.md) |
| 完整开发规范 | [docs/development-standards.md](../docs/development-standards.md) |

## 关联入口

- [AGENTS.md](../AGENTS.md) - 智能体全局契约入口（含启动协议）
- [global-core-rules.md](global-core-rules.md) - 全局核心规则
- [.agents/README.md](README.md) - .agents 规范容器总览
