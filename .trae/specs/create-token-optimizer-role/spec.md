---
id: "spec-create-token-optimizer-role"
title: "创建Token优化专家角色 - 产品需求文档"
date: "2026-08-01"
status: "draft"
---

# 创建Token优化专家（Token Optimizer）角色 - 产品需求文档

## Overview
- **Summary**: 基于已完成系统化整理的LLM Token优化知识库（29个结构化文档，覆盖原理、方法、工具、案例、评估、决策框架六大模块），在 `.agents/roles/` 目录下创建一个专门的 `token-optimizer.md` 角色文件。该角色将完整继承知识库中的理论框架、35种优化方法、5个最佳实践模式、27条分级禁令和三维权衡决策体系，以 `llm-token-optimization` 文件夹作为主要知识库来源，能够为其他角色提供Token使用优化的专业指导、方案评审和最佳实践落地支持。
- **Purpose**: 解决当前多智能体系统中缺乏专门Token优化角色的问题，将Token优化知识转化为可执行的角色能力，确保在LLM应用开发、Prompt设计、系统架构、Agent构建等场景中能够系统性地应用Token优化方法论，实现成本、质量、延迟的三维平衡。
- **Target Users**: 多智能体协作系统中的其他角色（architect、developer、orchestrator等），以及使用该Agent系统进行LLM应用开发的用户。

## Goals
- 创建符合现有角色规范的 `token-optimizer.md` 角色文件
- 完整继承llm-token-optimization知识库的核心理论框架和方法论
- 明确角色职责边界（Responsibilities）和非目标（Non-Goals）
- 配置知识库引用路径，确保角色能够准确查阅相关文档
- 更新 `roles/README.md` 角色索引，将新角色加入职责矩阵
- 确保角色定义符合现有格式规范（YAML frontmatter、三段式结构、链接格式）

## Non-Goals (Out of Scope)
- 不修改现有知识库内容（llm-token-optimization目录保持不变）
- 不创建新的TOML元数据文件（遵循现有角色x-toml-ref引用模式，如无对应TOML则不强制添加）
- 不创建对应的system-prompt.md（本任务仅创建角色定义文件，提示词模板按需后续创建）
- 不修改现有其他角色的职责定义
- 不实现具体的Token优化代码或工具脚本
- 不创建角色对应的Skill或Command

## Background & Context
- 已完成LLM Token优化知识体系的系统化整理，产出29个结构化Markdown文档，位于 `.agents/docs/knowledge/learning/llm-token-optimization/`
- 知识体系包含：01-原理、02-方法（35种技术）、03-工具（24个框架）、04-案例（9个跨行业案例）、05-评估（19项指标）、06-决策框架（决策树+选型矩阵+5模式+反模式+检查清单）、07-审查记录、08-元分析、09-约束清单（27条禁令P0-P3分级）、10-快速参考卡、术语表、参考文献
- 现有7个角色（orchestrator、architect、developer、reviewer、tester、thesis-advisor、co-founder）均采用统一格式：YAML frontmatter（id/title/x-toml-ref/source）+ Description/Responsibilities/Non-Goals三段式结构
- 角色索引在 `roles/README.md` 中维护，包含职责矩阵表格和文件结构说明
- 角色之间通过Non-Goals明确职责边界，避免重叠

## Functional Requirements
- **FR-1**: 创建 `d:\AI\.agents\roles\token-optimizer.md` 文件，包含标准YAML frontmatter
- **FR-2**: 角色Description部分清晰描述角色定位：LLM Token使用优化专家，负责在成本-质量-延迟三维空间中寻找帕累托最优解
- **FR-3**: 角色Responsibilities部分明确列出核心职责，包括但不限于：
  - Token优化方案设计与技术选型指导
  - Prompt结构优化建议（静态前缀+动态后缀、缓存友好设计）
  - 缓存策略设计（三层缓存架构：前缀/会话/语义）
  - 上下文压缩与对话管理策略
  - 模型路由与分级策略建议
  - Token优化方案评审与风险识别
  - 优化效果评估与指标体系建立
  - 27条禁令合规性检查
  - 按需查阅知识库提供决策支持
- **FR-4**: 角色Non-Goals部分明确职责边界，与现有角色区分：
  - 不负责架构整体设计（归architect）
  - 不负责具体代码实现（归developer）
  - 不负责代码审查（归reviewer）
  - 不负责测试编写（归tester）
  - 不负责任务编排协调（归orchestrator）
  - 不做脱离质量底线的极端成本优化
- **FR-5**: Responsibilities中明确引用知识库的关键文档路径（使用相对路径，遵循现有角色引用知识库的格式）
- **FR-6**: 更新 `roles/README.md`：
  - 在职责矩阵表格中添加token-optimizer角色行
  - 在文件结构说明中添加token-optimizer.md
  - 保持表格格式与现有条目一致

## Non-Functional Requirements
- **NFR-1**: 文件格式一致性：严格遵循现有角色文件的Markdown格式、frontmatter字段顺序、标题层级
- **NFR-2**: 链接有效性：所有知识库引用使用相对路径，格式与architect/developer角色中的知识库引用一致
- **NFR-3**: 术语准确性：角色描述中使用的专业术语与知识库术语表（glossary.md）保持一致
- **NFR-4**: 边界清晰性：Non-Goals必须明确覆盖与其他6个现有角色的职责划分，避免职责模糊
- **NFR-5**: 可操作性：Responsibilities中的每一项都应对应知识库中的具体模块或文档，角色"知道去哪里查"

## Constraints
- **Technical**: 
  - 文件必须位于 `d:\AI\.agents\roles\` 目录下
  - 文件名使用kebab-case：`token-optimizer.md`（纯英文，禁止中文）
  - frontmatter字段必须包含id、title、source，x-toml-ref字段如无对应TOML文件可省略或按现有模式处理
  - Markdown表格修改必须替换整个表格（遵循project_memory约束）
- **Business**: 角色定位为"专家顾问"角色，为其他角色提供专业支持，而非独立执行所有优化任务
- **Dependencies**:
  - 依赖现有知识库：`.agents/docs/knowledge/learning/llm-token-optimization/` 下的所有文档
  - 依赖现有角色格式规范：参考architect.md、developer.md的结构
  - 依赖角色索引文件：`roles/README.md`

## Assumptions
- 现有角色的x-toml-ref引用的TOML文件可能不存在或为可选配置，新角色可暂不包含x-toml-ref或使用类似路径
- 角色定义文件不需要立即配置system-prompt，后续使用时再补充
- 更新README.md时，保持现有表格列结构和格式不变，仅新增一行
- 知识库路径使用相对于.agents/的相对路径（如 `../docs/knowledge/learning/llm-token-optimization/README.md`），与现有角色引用方式一致

## Acceptance Criteria

### AC-1: 角色文件创建成功
- **Given**: spec文档已获批准
- **When**: 在 `d:\AI\.agents\roles\` 目录下创建token-optimizer.md
- **Then**: 文件存在，包含合法的YAML frontmatter（id为"token-optimizer"，title包含"Token优化专家"或类似中文名称），正文包含Description、Responsibilities、Non-Goals三个章节
- **Verification**: `programmatic`
- **Notes**: 可通过文件读取验证frontmatter和章节结构

### AC-2: 职责完整覆盖知识库核心能力
- **Given**: token-optimizer.md已创建
- **When**: 检查Responsibilities章节
- **Then**: 包含以下核心能力领域的职责描述：(1)三大路径（减少/复用/压缩）、(2)五大模式（P-001到P-005）、(3)P0级禁令合规检查、(4)三维权衡决策支持、(5)知识库查阅指引
- **Verification**: `human-judgment`
- **Notes**: 对照10-quick-reference.md和09-constraints.md验证核心概念是否体现

### AC-3: 职责边界清晰无重叠
- **Given**: token-optimizer.md已创建
- **When**: 检查Non-Goals章节，并与其他6个角色的Responsibilities对比
- **Then**: Non-Goals明确声明不负责架构设计、代码实现、代码审查、测试、任务编排等，与architect/developer/reviewer/tester/orchestrator的职责边界清晰
- **Verification**: `human-judgment`

### AC-4: 知识库引用正确
- **Given**: token-optimizer.md已创建
- **When**: 检查文件中的Markdown链接
- **Then**: 所有知识库引用使用相对路径（相对于.agents/roles/目录，即 `../docs/knowledge/learning/llm-token-optimization/...`），链接路径指向实际存在的文件
- **Verification**: `programmatic`
- **Notes**: 参考architect.md中 `../docs/knowledge/decisions/README.md` 的引用格式

### AC-5: README索引更新完整
- **Given**: token-optimizer.md已创建
- **When**: 更新roles/README.md
- **Then**: (1)职责矩阵表格新增token-optimizer行，包含角色、ID、领域、层级、层级标记、核心职责列；(2)文件结构说明列表中添加token-optimizer.md；(3)Markdown表格格式完整，未破坏原有结构
- **Verification**: `programmatic` + `human-judgment`

### AC-6: 格式符合现有规范
- **Given**: token-optimizer.md和README.md更新完成
- **When**: 将新文件与architect.md、developer.md对比格式
- **Then**: frontmatter字段顺序、标题层级、列表格式、表格风格、语言风格与现有角色文件保持一致
- **Verification**: `human-judgment`

## Open Questions
- [ ] x-toml-ref字段：现有角色都引用了 `../../.meta/toml/.agents/roles/<id>.toml`，但需要确认这些TOML文件是否实际存在，新角色是否需要创建对应TOML还是可以暂时省略该字段
