# Harness Engineering 七概念分析 — Product Requirement Document

## Overview
- **Summary**: 使用七概念方法论（R→I→E→V→入库）对微信公众号文章《新 ClaudeCode 和 Codex 变得越来越强的 5 个 Harness 设计》进行系统性分析，提取核心洞察，沉淀可复用模式到项目知识库。
- **Purpose**: 将 Harness Engineering 领域的前沿思想引入 SpecWeave 项目，为智能体运行时架构提供理论参考，同时验证七概念方法论在外部技术文章分析中的适用性。
- **Target Users**: SpecWeave 架构师、智能体开发者、方法论实践者

## Goals
- G1: 完成对 Harness Engineering 文章的系统性分析，输出结构化事实清单
- G2: 提取至少 3 条核心洞察，每条包含完整四元组（陈述/证据/反常识/行动）
- G3: 沉淀 1-2 个可复用方法论模式到 `docs/retrospective/patterns/`
- G4: 通过对抗审查验证模式的可迁移性
- G5: 完成模式入库与索引更新

## Non-Goals (Out of Scope)
- 不修改现有智能体运行时代码
- 不创建新的 Skill 工具
- 不直接实现 Harness 架构（仅做知识沉淀）
- 不扩展七概念方法论体系本身

## Background & Context
- **文章来源**: 微信公众号"皇子谈技术"，标题《新 ClaudeCode 和 Codex 变得越来越强的 5 个 Harness 设计》
- **核心主题**: Harness Engineering — AI Agent 运行时架构设计
- **七概念方法论**: 基于复盘(R)、洞察(I)、萃取(E)、对抗审查(V)、原子提交(C)、原子化(A)、第一性原理(F)的知识沉淀流程
- **参照规范**: [.agents/commands/seven-concepts.md](../../../../.agents/commands/seven-concepts.md) 知识沉淀流程

## Functional Requirements
- **FR-1**: 执行七概念知识沉淀流程（R→I→E→V→入库）
- **FR-2**: 提取文章核心事实清单（≥20条，无因果词）
- **FR-3**: 生成至少 3 条核心洞察，每条包含四元组
- **FR-4**: 沉淀 1-2 个结构化模式文档（触发场景/步骤/反模式/迁移验证）
- **FR-5**: 执行对抗审查（≥5条审查意见，至少采纳2条）
- **FR-6**: 完成模式入库、索引更新、交叉引用修复

## Non-Functional Requirements
- **NFR-1**: 事实清单严格无因果词（因为/所以/导致/错误/失误）
- **NFR-2**: 洞察四元组完整可证伪
- **NFR-3**: 模式可迁移到≥1个非当前领域场景
- **NFR-4**: 所有产出遵循项目命名规范与文档标准

## Constraints
- **Technical**: 输出格式为 Markdown，遵循 SpecWeave 文档规范
- **Business**: 知识沉淀场景，遵循七概念质量门标准
- **Dependencies**: 依赖七概念方法论体系规范

## Assumptions
- 用户已阅读并理解七概念方法论体系
- 文章内容可被完整提取和分析
- 模式入库流程符合项目已有规范

## Acceptance Criteria

### AC-1: 事实清单无因果词
- **Given**: 已完成 R 阶段事实采集
- **When**: 检查事实清单内容
- **Then**: 清单中无"因为/所以/导致/错误/失误"等判断词，≥20条客观事实
- **Verification**: `programmatic`

### AC-2: 洞察四元组完整
- **Given**: 已完成 I 阶段洞察分析
- **When**: 检查每条洞察
- **Then**: 每条洞察包含陈述、证据(Fxx)、反常识、下次行动四个要素
- **Verification**: `human-judgment`

### AC-3: 模式可迁移验证
- **Given**: 已完成 E 阶段模式萃取
- **When**: 验证模式迁移性
- **Then**: 模式能迁移到≥1个非 Harness 领域场景
- **Verification**: `human-judgment`

### AC-4: 对抗审查有实质内容
- **Given**: 已完成 V 阶段对抗审查
- **When**: 检查审查意见
- **Then**: 审查意见≥5条且具体，至少采纳2条修正
- **Verification**: `human-judgment`

### AC-5: 模式入库完成
- **Given**: 已完成模式萃取与审查
- **When**: 执行原子提交
- **Then**: 模式文件已入库到正确目录，索引已更新，无断链
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要将 Harness 架构思想映射到 SpecWeave 现有运行时设计？
- [ ] 是否需要创建 Harness 相关的实战演练题目？
