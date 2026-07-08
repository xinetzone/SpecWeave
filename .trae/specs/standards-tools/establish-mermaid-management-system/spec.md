---
version: "1.0"
last_updated: "2026-06-30"
theme: "standards-tools"
spec_type: "feature-addition"
x-toml-ref: "../../../../.meta/toml/.trae/specs/standards-tools/establish-mermaid-management-system/spec.toml"
---
# Mermaid 图表管理体系 - Product Requirement Document

## Overview
- **Summary**: 在 `.agents/` 目录中建立完整的 Mermaid 图表管理体系，涵盖指令集（commands/）、命令门面 Skill（skills/）、现有角色能力增强、专项协作团队（teams/）四大模块，并配套测试用例与索引更新。体系遵循项目现有渐进式披露三层架构（L0-L1-L2）和角色最小化原则，通过 RACI 扩展而非新增独立角色来配置 Mermaid 专业能力。
- **Purpose**: 当前项目虽已有 Mermaid 检查脚本（check-mermaid.py）和安全编码模板（templates/mermaid-templates/），但缺乏标准化的操作指令、可发现的 Skill 入口、明确的角色职责分配和复杂图表协作机制。新建体系将使 Agent 在处理 Mermaid 相关任务时有规范可依、有 Skill 可用、有团队可协作，从"凭经验写 Mermaid"升级为"按规范生成-检查-修复-交付"的标准化流程。
- **Target Users**: SpecWeave 项目中所有需要创建、审查、维护 Mermaid 图表的 AI Agent 角色（orchestrator、architect、developer、reviewer、tester）。

## Goals
- 建立 `mermaid` 指令集（commands/mermaid.md），定义 Mermaid 图表生成、检查、修复、模板选择、质量验收的标准化流程，包含完整 RACI 矩阵和 CMD-LOG 规范
- 创建 `mermaid-cmd` 命令门面 Skill（skills/mermaid-cmd/SKILL.md），提供触发词、方案决策树、核心步骤、安全检查清单，遵循五要素模型和渐进式披露三层架构
- 增强现有角色的 Mermaid 能力绑定：在 architect.md、developer.md、reviewer.md、tester.md 的 `[bindings].skills` 中添加 mermaid-cmd，明确各角色在 Mermaid 任务中的专业职责
- 组建 `team-mermaid` 专项协作团队（teams/），由现有4个工程角色组成，包含团队定义文件、YAML 数据文件和标准工作流，负责复杂 Mermaid 图表的协作创建
- 增强 Mermaid 检查脚本能力：为 check-mermaid.py 补充 classDiagram、erDiagram 两种常用图表类型的检查与自动修复，并新增单元测试覆盖
- 更新所有相关索引（AGENTS.md、.agents/README.md、commands/README.md、skills/README.md、roles/README.md、teams/README.md、capability-registry.md、ONBOARDING.md）
- 提供必要的测试用例（pytest），覆盖指令集流程逻辑、Skill 门面完整性、Mermaid 检查脚本增强功能、团队配置正确性

## Non-Goals (Out of Scope)
- 不新增独立的 Mermaid 专职角色（遵循角色最小化原则，通过 RACI 扩展 + 专项团队满足角色专业能力需求）
- 不实现 Mermaid 图表的服务端渲染或图片导出（超出工具链范围，渲染由 IDE/GitHub/飞书等宿主环境负责）
- 不重写现有 check-mermaid.py 的核心检查逻辑，仅做增量增强（新增 classDiagram/erDiagram 支持）
- 不创建新的 Mermaid 模板（现有 8 个模板已覆盖常用场景，新模板需求由用户另行提出）
- 不修改 vendor/ 目录下任何文件（遵循 vendor 边界约束）
- 不建立 Mermaid 图表的版本管理或 diff 工具（属于长期演进方向，不在本次范围内）

## Background & Context

### 现有 Mermaid 资产盘点
| 资产 | 位置 | 状态 | 说明 |
|------|------|------|------|
| Mermaid 语法检查脚本 | [.agents/scripts/lib/checks/mermaid.py](../../../../.agents/scripts/lib/checks/mermaid.py) | 已有 | 支持 flowchart/stateDiagram/sequenceDiagram/pie/gantt/mindmap/timeline/xychart-beta/quadrantChart，含--fix自动修复 |
| Mermaid 检查入口 | check-mermaid.py | 已有 | 薄包装，转发到 repo-check.py mermaid |
| Mermaid 安全编码模板 | [.agents/templates/mermaid-templates/](../../../../.agents/templates/mermaid-templates/) | 已有 | 8个模板（safe-starter/flowchart variants/sequence/state/mindmap） |
| Mermaid 安全编码规则 | docs/retrospective/patterns/code-patterns/mermaid-safe-coding-rules.md | 已有 | 六规则完整文档 |
| AGENTS.md 中 Mermaid 使用 | 全局 | 已有 | 全局规则要求"流程、架构等可视化逻辑优先使用 Mermaid" |
| cmd-log-specification.md | .agents/rules/ | 已有 | CMD-LOG 格式规范，新指令集需遵循 |

### 现有架构约束
1. **渐进式披露三层架构**：L0 ONBOARDING.md（<100行速查）→ L1 capability-registry.md（全量索引）→ L2 详细规范文档
2. **角色最小化原则**：RACI 扩展优先于角色新增（见 commands/README.md 和 role-auto-creation.md）
3. **Skill 五要素模型**：Trigger-Ready Description、Decision Tree、Progressive Disclosure、Why-Explanation、Safety Checklist
4. **CMD-LOG 规范**：所有命令集门面必须输出结构化日志，遵循 cmd-log-specification.md
5. **专项团队先例**：flexloop-team 已示范"现有角色组成专项团队"模式，有完整 .md + .yaml 双文件结构
6. **测试要求**：新增脚本功能必须有 pytest 单元测试，覆盖率不低于80%

### 角色决策：为什么不新增独立角色？
用户要求"设计具备 mermaid 专业知识的角色配置"。经分析：
- 现有6+1角色已覆盖 Mermaid 全流程职责（architect 设计→developer 编码→reviewer 审查→tester 验证）
- Mermaid 是跨领域通用工具，不是独立职责领域
- role-auto-creation.md 规定的4个触发条件（职责空白/能力缺失/负载溢出/架构演进）均不满足——Mermaid 相关工作频率不足以造成负载溢出，也不存在职责空白
- flexloop-team 先例证明"专项团队+RACI矩阵"是比新增角色更轻量、更符合项目规范的方案

因此**采用"现有角色能力增强 + Mermaid 专项团队"方案**：在角色 bindings.skills 中添加 mermaid-cmd 以绑定专业能力，通过 team-mermaid 定义复杂图表协作流程。

## Functional Requirements

### FR-1: Mermaid 指令集（commands/mermaid.md）
- 系统 SHALL 提供 mermaid 指令集文档，定义以下6个标准化操作子流程：
  - 图表生成（create）：需求分析→类型选择→模板起步→代码生成
  - 语法检查（check）：调用 check-mermaid.py 扫描问题
  - 自动修复（fix）：使用 --fix 参数修复可自动修复的问题
  - 模板选择（template）：从8个现有模板中推荐合适模板
  - 质量验收（verify）：可读性、准确性、一致性检查
  - 归档交付（deliver）：插入目标文档、更新索引
- 指令集 SHALL 包含完整 RACI 责任分配矩阵，遵循三大强制规则（A唯一性、R≠A分离、双列设计）
- 指令集 SHALL 定义 CMD-LOG 日志规范：cmd标识为 `mermaid`，session前缀 `merm-`，步骤S0-S6，特有事件枚举
- 指令集 SHALL 包含输入规范（参数表）、输出规范（产出物表）、质量验收标准、约束条件
- 指令集 SHALL 包含 TOML frontmatter（id、category、source）

### FR-2: Mermaid 命令门面 Skill（skills/mermaid-cmd/）
- 系统 SHALL 提供 mermaid-cmd Skill，作为 mermaid 指令集的L1入口门面
- Skill SHALL 遵循五要素模型：
  - **Trigger-Ready Description**：包含完整触发词列表（mermaid、流程图、时序图、状态图、画个图、图表、架构图、思维导图、ER图、类图、甘特图、饼图、UML图、可视化流程、画流程图、mermaid图）
  - **Decision Tree**：提供3种方案选择（快速生成/检查修复/复杂图表协作）及明确的选型条件
  - **Progressive Disclosure**：SKILL.md 控制在500行以内，详细CMD-LOG事件表引用L2 cmd-log-specification.md
  - **Why-Explanation**：关键规则后包含 `> **为什么？**` 解释
  - **Safety Checklist**：包含 dry-run/预览、检查验证、幂等操作等安全项
- Skill SHALL 包含方案选择决策树：
  - 快速生成：简单图表（<10节点、单图层），直接基于模板生成
  - 检查修复：已有 Mermaid 代码需要校验和修复
  - 复杂图表协作：大型架构图（>20节点、多subgraph、跨文档引用），触发 mermaid 团队协作
- Skill SHALL 引用L2文档（commands/mermaid.md、cmd-log-specification.md、mermaid-safe-coding-rules.md）
- Skill SHALL 包含 assets/ 目录存放快速参考卡片（可选）

### FR-3: 现有角色 Mermaid 能力增强
- 系统 SHALL 更新以下4个角色的 TOML frontmatter，在 `[bindings].skills` 数组中添加 `"mermaid-cmd"`：
  - architect.md：架构师在方案设计阶段需创建架构图、流程图
  - developer.md：开发者在实现阶段需编写/修改 Mermaid 代码
  - reviewer.md：审查者在质量验收阶段需检查 Mermaid 语法和规范
  - tester.md：测试工程师需验证 Mermaid 图表渲染正确性
- orchestrator 和 co-founder 不需要在 bindings.skills 中绑定 mermaid-cmd（orchestrator 负责任务分配不直接创建图表，co-founder 不干预日常技术操作）
- 角色的 Responsibilities 和 Non-Goals 部分 SHALL 根据需要补充 Mermaid 相关职责说明（少量增量，不重构现有内容）

### FR-4: Mermaid 专项团队（team-mermaid）
- 系统 SHALL 创建 team-mermaid 专项团队，参照 flexloop-team 的双文件结构：
  - teams/mermaid-team.md：团队定义文档（TOML frontmatter + Markdown）
  - teams/data/team-mermaid.yaml：团队配置数据文件
- 团队成员 SHALL 由现有4个工程角色组成：architect、developer、reviewer、tester（不新增角色）
- 团队 SHALL 定义治理范围：
  - `.agents/templates/mermaid-templates/`（模板维护）
  - `.agents/scripts/lib/checks/mermaid.py`（检查脚本维护）
  - `docs/retrospective/patterns/code-patterns/mermaid-safe-coding-rules.md`（安全规则维护）
  - 全项目 Mermaid 图表质量标准
- 团队 SHALL 定义3个标准工作流：
  - 简单图表生成（单角色快速交付）
  - 复杂图表协作（多角色协作流程）
  - 批量检查修复（全项目Mermaid质量扫描）
- 团队 YAML 文件 SHALL 遵循 team-flexloop.yaml 的结构规范（members、scope、governance_rules、permissions、workflows、config）
- 团队 SHALL 定义成员职责矩阵，明确每个角色在 Mermaid 任务中的具体职责

### FR-5: Mermaid 检查脚本增强
- 系统 SHALL 为 check-mermaid.py（mermaid.py）新增以下两种图表类型的支持：
  - **classDiagram**（类图）：空行检测、类名引号检查、关系标签引号检查、方法/属性格式检查
  - **erDiagram**（ER图）：空行检测、实体名引号检查、关系基数格式检查、属性定义检查
- 新增检查器（_check_classDiagram、_check_erDiagram）和修复器（_fix_classDiagram、_fix_erDiagram）
- 在 DIAGRAM_CHECKERS 和 DIAGRAM_FIXERS 字典中注册新类型
- 扩展 _detect_diagram_type 函数识别 classDiagram 和 erDiagram 声明
- 新增图表类型必须遵循现有检查器的代码风格和错误消息格式

### FR-6: 测试用例
- 系统 SHALL 为新增/修改的功能提供 pytest 单元测试：
  - Mermaid 检查脚本新增功能测试（test_checks_mermaid.py）：覆盖 classDiagram/erDiagram 的空行检测、引号检查、自动修复
  - 团队配置验证：YAML 文件结构正确性、成员角色有效性、权限配置合理性（可加在现有测试体系中或新建 test_team_mermaid.py）
  - Skill 门面质量验证：运行 check-skill-quality.py 验证 mermaid-cmd 通过五要素检查
  - 指令集链接验证：运行 check-links.py 验证新文档中所有链接有效
- 测试覆盖率要求：新增代码（mermaid.py增量、新文档）覆盖率不低于80%
- 所有现有测试必须继续通过（不引入回归）

### FR-7: 索引与注册中心更新
- 系统 SHALL 更新以下索引文件以注册新增能力：
  - AGENTS.md：在指令集索引、角色定义索引、团队索引中添加 mermaid 条目
  - .agents/README.md：更新目录结构说明
  - .agents/commands/README.md：在指令集清单和RACI总览表中添加 mermaid
  - .agents/skills/README.md：在 Skill 列表中添加 mermaid-cmd
  - .agents/roles/README.md：在角色职责矩阵中补充 Mermaid 能力列（如需要）
  - .agents/teams/README.md：在现有团队清单中添加 team-mermaid
  - .agents/capability-registry.md：在脚本索引、Skill索引、命令集索引中添加条目，并更新 counts 计数
  - .agents/ONBOARDING.md：在能力速查表和任务路由决策树中添加 Mermaid 相关条目

## Non-Functional Requirements
- **NFR-1 一致性**：所有新增文件必须遵循现有代码风格、命名规范（kebab-case）、TOML frontmatter 格式和文档结构
- **NFR-2 渐进式披露合规**：L0 ONBOARDING.md 保持<100行，L1 SKILL.md/指令集保持<500行，详细内容放L2引用
- **NFR-3 可发现性**：Agent 在新会话中能通过 L0→L1→L2 路径在30秒内发现 Mermaid 相关能力
- **NFR-4 向后兼容**：增强 mermaid.py 不得破坏现有 flowchart/stateDiagram 等图表类型的检查和修复功能
- **NFR-5 文档完整性**：所有新增文档必须有中文注释和 Why 解释，使用相对路径引用，禁止 file:/// 绝对路径
- **NFR-6 测试稳定性**：所有测试必须可重复运行通过，不依赖外部网络或特定环境

## Constraints
- **Technical**:
  - 必须使用 Python 3 编写脚本（与现有脚本一致）
  - 必须遵循现有 lib/checks/ 模块的接口规范（run(project_root, args) -> int 入口函数）
  - TOML frontmatter 格式必须与现有文件一致（+++ 分隔符）
  - 所有路径引用使用相对路径，禁止绝对路径
- **Business**:
  - 必须在当前会话内完成，不依赖跨会话状态
  - 不新增 npm/pip 依赖（使用现有标准库和已安装依赖）
- **Dependencies**:
  - 依赖现有 cmd-log-specification.md 的日志格式
  - 依赖现有 SKILL-TEMPLATE.md 的模板结构
  - 依赖现有 check-mermaid.py 的架构（DIAGRAM_CHECKERS/DIAGRAM_FIXERS 注册模式）
  - 依赖现有 team-flexloop.yaml 的团队YAML结构作为参考

## Assumptions
- classDiagram 和 erDiagram 是最常用的两种尚未支持的 Mermaid 图表类型（基于项目文档中UML类图和数据模型的潜在需求）
- 现有8个 Mermaid 模板能满足绝大多数场景，无需新增模板
- 专项团队模式（team-mermaid）足以处理复杂图表协作需求，无需引入额外的工作流文档
- Agent 在执行 Mermaid 任务时能通过 Skill 门面正确路由到指令集，不需要额外的协议文档

## Acceptance Criteria

### AC-1: Mermaid 指令集文档完整规范
- **Given**: 开发者需要创建/检查 Mermaid 图表
- **When**: 读取 commands/mermaid.md
- **Then**: 文档包含触发条件、输入规范、RACI矩阵、6个执行步骤（S0-S6）、输出规范、质量验收、约束条件、CMD-LOG规范，且 TOML frontmatter 完整
- **Verification**: `programmatic` - 运行文档结构检查脚本验证必需章节存在；`human-judgment` - 审查RACI矩阵是否符合三大强制规则
- **Notes**: RACI矩阵中A角色在每项活动中唯一，L3执行操作层R≠A分离

### AC-2: Mermaid-cmd Skill 通过五要素质量检查
- **Given**: mermaid-cmd/SKILL.md 已创建
- **When**: 运行 `python .agents/scripts/check-skill-quality.py mermaid-cmd`
- **Then**: 所有检查项通过（frontmatter完整、description含触发词、有决策树、≤500行、Why解释≥2个、安全清单完整、路径相对）
- **Verification**: `programmatic` - check-skill-quality.py 返回0退出码
- **Notes**: 对比现有5个cmd Skill的质量标准

### AC-3: 角色能力绑定正确更新
- **Given**: 4个角色文件已更新
- **When**: 检查 architect.md、developer.md、reviewer.md、tester.md 的 frontmatter
- **Then**: [bindings].skills 数组中均包含 "mermaid-cmd"，且 orchestrator.md、co-founder.md 未被修改
- **Verification**: `programmatic` - 文本搜索验证 bindings 更新
- **Notes**: 角色职责描述的增量修改需符合 Non-Goals 约束（不重构现有内容）

### AC-4: team-mermaid 团队配置完整有效
- **Given**: mermaid-team.md 和 data/team-mermaid.yaml 已创建
- **When**: 审查团队文件
- **Then**: 团队包含4个成员（architect/developer/reviewer/tester），定义了3个标准工作流，权限配置合理，YAML格式正确可解析
- **Verification**: `programmatic` - YAML语法验证；`human-judgment` - 审查成员职责与RACI一致性
- **Notes**: 参照 team-flexloop.yaml 结构，但治理范围限定为Mermaid相关资产

### AC-5: Mermaid 检查脚本新增功能正确
- **Given**: mermaid.py 已增强支持 classDiagram/erDiagram
- **When**: 使用包含classDiagram/erDiagram语法问题的测试文件运行检查
- **Then**: 脚本能正确检测空行、引号缺失等问题，--fix 能自动修复可修复问题，且不影响现有图表类型
- **Verification**: `programmatic` - pytest 单元测试通过，包括正反例测试
- **Notes**: 新增检查器遵循现有_check_xxx/_fix_xxx函数签名和返回格式

### AC-6: 新增测试覆盖核心功能
- **Given**: 测试文件已创建
- **When**: 运行 `python -m pytest .agents/scripts/tests/ -v`
- **Then**: 所有测试通过（包括新增的classDiagram/erDiagram测试和回归测试），新增代码覆盖率≥80%
- **Verification**: `programmatic` - pytest返回0退出码，覆盖率报告达标
- **Notes**: 现有37个测试必须全部继续通过

### AC-7: 所有索引文件正确更新
- **Given**: 所有新增文件就位
- **When**: 运行链接检查 `python .agents/scripts/check-links.py --path .agents/`
- **Then**: 所有本地链接有效（无断链），AGENTS.md、ONBOARDING.md、capability-registry.md 等索引文件中 mermaid 条目路径正确
- **Verification**: `programmatic` - check-links.py 返回0退出码
- **Notes**: 特别注意L0→L1→L2三层引用链的完整性

### AC-8: 全量CI检查通过
- **Given**: 所有实现完成
- **When**: 运行 `powershell .agents/scripts/ci-check.ps1`
- **Then**: CI综合检查全部通过（filename/gitignore/mermaid/vendor/roles五项检查无错误）
- **Verification**: `programmatic` - ci-check.ps1 返回0退出码
- **Notes**: 包括Mermaid自检查（新增的classDiagram/erDiagram检查器应能正确检查新文档中的Mermaid代码块）

## Open Questions
- [ ] mermaid-cmd Skill 是否需要 assets/ 目录存放快速参考卡片（Mermaid语法速查表）？——建议：作为可选项，如果SKILL.md在500行内能容纳核心速查内容则不需要单独assets文件
- [ ] team-mermaid 是否需要配套的操作手册（类似 flexloop-team-operations.md）？——建议：初期不需要，团队定义文件中已包含3个标准工作流的步骤说明；如果后续复杂图表流程增多再补充
- [ ] 是否需要在 .agents/templates/ 中新增Mermaid指令集专用模板？——建议：不需要，指令集文档遵循现有commands/下其他指令集的结构即可
