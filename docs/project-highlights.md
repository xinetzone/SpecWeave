---
id: "project-highlights"
source: "README.md#项目亮点"
x-toml-ref: "../.meta/toml/docs/project-highlights.toml"
---
# 项目亮点

> **来源**：从 `README.md` "项目亮点"章节拆分

本文件汇总 SpecWeave 规范体系的核心优势、技术创新点与量化成果数据。

## 核心优势

| 优势 | 说明 |
|---|---|
| 单一入口路由 | AGENTS.md 作为最高优先级入口，按需加载 .agents/ 规范，避免上下文爆炸 |
| 7 角色分工体系 | orchestrator/architect/developer/reviewer/tester/co-founder/team-admin，每个角色有明确职责与能力边界（Non-Goals） |
| 机器可读的角色定义 | TOML frontmatter 声明 id/domain/layer/bindings，便于智能体程序化解析与绑定 |
| 完整协作协议 | 覆盖任务交接、消息传递、冲突解决、临时依赖管理与应用开发生命周期五类协议 |
| Mermaid 流程可视化 | 所有工作流、架构、关系均使用 Mermaid 表达，可渲染、可版本化、可审查 |
| 临时依赖治理三重机制 | .gitignore 规则 + Git pre-commit hook + 验证脚本，防止临时依赖误提交 |

## 技术创新点

| 创新 | 说明 | 来源 |
|---|---|---|
| 入口+容器二元架构 | AGENTS.md（路由+约束）+ .agents/（具体规范），分离关注点，可扩展性强 | 架构决策 |
| 三层递进提示词体系 | 全局契约→角色定义→精细化提示词，递进式加载 | [提示词萃取](retrospective/prompt-extraction.md) |
| TOML frontmatter 绑定关系 | 通过 rules/references/skills 声明角色与协议/工作流的绑定 | [角色体系](agent-roles.md) |
| 元工具体系 | 用工具治理工具，每个工具解决上一轮工作的摩擦点 | [优化循环洞察](retrospective/reports/insight-extraction/meta-methodology/retrospective-insight-optimization-cycle/) |
| 三层治理模型 | 原子化→自动化→验证，形成闭环，缺失任何一层都会出现治理漏洞 | [验证与自动化](verification-automation.md) |
| 自指性规范体系 | 规范文档自身遵循所定义的方法论（格式、流程、验证），形成"规范即测试"的自我验证闭环 | [洞察·萃取报告](retrospective/reports/project-governance/comprehensive-reviews/retrospective-comprehensive-20260623/insight-extraction.md#L13-L17) |
| 工具熵减非线性优化曲线 | 揭示工具链规模与收益的非线性关系，发现最优规模阈值（5-6 个脚本），指导工具合并与重构决策 | [工具熵减报告](retrospective/reports/project-governance/tools-and-automation/retrospective-report-tool-entropy-nonlinear-optimization/) |
| 元文档杠杆效应 | 元文档质量×读者接触率远超功能文档，以索引优先、入口递进的设计撬动全局信息可发现性 | [洞察·萃取报告](retrospective/reports/project-governance/comprehensive-reviews/retrospective-comprehensive-20260623/insight-extraction.md#L37-L41) |
| 两栖定位模型 | 通过资产清单+泛化路径图+落地案例三支柱，实现"具体规范"与"元框架"双重定位的共存与互证 | [两栖定位模型](retrospective/patterns/methodology-patterns/governance-strategy/amphibious-positioning-model.md) |

## 量化成果

| 维度 | 数值 |
|---|---|
| 交付物总数 | 70+ 个（规范层 + 工程层 + 治理层 + 知识层 + 子项目） |
| 验证脚本 | 9 个（7 个核心验证 + 2 个原子化预检） |
| 复盘报告 | 16+ 份（含初版、深度版、洞察报告、综合报告、原子化元级复盘） |
| 方法论模式 | 34 个（spec-driven/review-loop/three-tier-governance/critical-mass 等完整闭环） |
| 架构模式 | 6 个（感知→检查→报告/多智能体并行/增量+回归验证 等） |
| 代码模式 | 6 个（上下文感知路径解析/Git忽略验证/元文档识别 等） |
| 决策框架 | 4 个（目录命名/依赖管理/元文档处理/语义匹配阈值） |
| 知识概念 | 10 个（元文档/上下文感知/正交验证/零依赖原则/语义前缀/规范自举性/模式成熟度/自指性/临界质量/元文档杠杆） |
| 工具兼容性 | 基于 AGENTS.md 开放标准，可被支持该标准的工具加载 |

## 与其他文档的关联

- 项目定位与设计理念见 [project-overview.md](project-overview.md)
- 角色体系详细说明见 [agent-roles.md](agent-roles.md)
- 协作协议与工作流见 [collaboration.md](collaboration.md)
- 验证脚本与自动化见 [verification-automation.md](verification-automation.md)
- 可复用模式库见 [retrospective/patterns/](retrospective/patterns/)
