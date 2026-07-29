---
id: "establish-four-region-routing-system"
version: "1.0"
source: "I→F→V 七概念方法论分析"
---
# 建立四大区域路由体系 - Product Requirement Document

## Overview
- **Summary**: 系统性分析并明确 SpecWeave 项目中 `.agents/`、`apps/`、`projects/`、`vendor/` 四个顶层目录的功能职责边界，补全 `apps/` 区域缺失的 AGENTS.md 入口路由，完善根 AGENTS.md 启动协议以覆盖全部子区域，优化 `.agents/` 规范容器结构，形成对称、完整、可维护的四层路由体系。
- **Purpose**: 当前项目存在架构不对称问题——`projects/` 和 `vendor/` 都有完整的 AGENTS.md 入口路由，但 `apps/` 区域缺失；根 AGENTS.md 启动协议仅覆盖 vendor/ 路由判断，导致智能体进入 apps/ 或 projects/ 区域时缺少规范指引。这造成了认知负担、路由不完整、维护不一致等问题。
- **Target Users**: AI 智能体（orchestrator/architect/developer/reviewer/tester）、项目维护者、新加入的贡献者

## Goals
- 明确四大顶层区域的功能职责划分与边界定义
- 为 `apps/` 区域创建与 projects/vendor 对称的 AGENTS.md 入口路由文档
- 更新根 AGENTS.md 启动协议，完整覆盖 apps/projects/vendor 三个子区域的路由判断
- 在根 AGENTS.md 中添加四大区域对比表，降低新人认知负担
- 更新 `.agents/context-routing.md` 添加 apps 区域入口
- 创建 `apps/.agents/` 元数据容器目录
- 更新 `apps/README.md` 引用 AGENTS.md 智能体入口
- 验证所有链接有效性和结构一致性

## Non-Goals (Out of Scope)
- 不修改 projects/ 或 vendor/ 内部的子项目/子模块内容
- 不重构 `.agents/` 内部现有的规范体系结构
- 不为每个 apps 子应用强制创建 AGENTS.md（仅当应用自身有复杂规范体系时需要）
- 不涉及 external/ 或 playground/ 目录（当前未在根目录结构中）
- 不修改任何应用的业务代码
- 不改变现有应用的生命周期管理流程（.temp→apps 迁移流程保持不变）

## Background & Context
- **现状问题**:
  1. `apps/` 缺少 AGENTS.md 入口文件，与 projects/vendor 模式不对称
  2. 根 AGENTS.md 启动协议步骤 2.1 仅判断 vendor/ 目录，遗漏 apps/ 和 projects/
  3. 上下文路由表 `.agents/context-routing.md` 缺少 apps 区域入口
  4. 四大区域的职责边界没有在入口文档中集中对比说明
- **参考模式**: `projects/AGENTS.md` 和 `vendor/AGENTS.md` 提供了成熟的区域入口模板，apps/ 应遵循相同模式但明确其主仓库内应用的本质区别
- **七概念分析**: 经过 I（洞察）→F（第一性原理）→V（对抗审查）分析，确认了 6 条公理和修正后的优化方案

## Functional Requirements
- **FR-1**: 创建 `apps/AGENTS.md` 作为 apps 区域智能体入口，包含区域性质、应用路由表、嵌套优先级、可用资产索引、边界声明、跨应用调用规范、异常处理分支
- **FR-2**: 创建 `apps/.agents/` 元数据容器目录及 README.md
- **FR-3**: 更新根 `AGENTS.md` 启动协议步骤 2.1，从仅判断 vendor/ 扩展为统一的区域路由判断，覆盖 apps/、projects/、vendor/
- **FR-4**: 在根 AGENTS.md 中添加「四大顶层区域对比表」，清晰说明各区域的用途、维护方式、版本控制策略
- **FR-5**: 更新 `.agents/context-routing.md`，在常规任务路由表中添加 apps 区域入口（apps/AGENTS.md、app-development-workflow 等）
- **FR-6**: 更新 `apps/README.md`，在顶部添加 AGENTS.md 智能体入口引用
- **FR-7**: 在根 AGENTS.md 核心规范入口表格中添加 projects/AGENTS.md、apps/AGENTS.md、vendor/AGENTS.md 三个区域入口链接

## Non-Functional Requirements
- **NFR-1**: 结构对称性：apps/AGENTS.md 的章节结构应与 projects/AGENTS.md、vendor/AGENTS.md 保持一致，降低认知负担
- **NFR-2**: 向后兼容：不改变现有文件的已有内容语义，仅补充和完善
- **NFR-3**: 链接完整性：所有新增和修改的链接必须有效，无断链
- **NFR-4**: 清晰性：四大区域的区别必须在一张对比表中一目了然，新人 30 秒内能理解
- **NFR-5**: 可维护性：未来新增/删除 app 时，只需更新 apps/AGENTS.md 的路由表，遵循与 projects/vendor 相同的维护模式

## Constraints
- **Technical**: 必须遵循现有 Markdown 格式和 frontmatter 规范；所有路径引用使用相对路径；遵循项目的文档风格
- **Business**: 不破坏现有功能，不影响子模块（projects/xuanspace、vendor/flexloop）的自治性
- **Dependencies**: 依赖现有的 projects/AGENTS.md 和 vendor/AGENTS.md 作为参考模板；依赖现有启动协议结构

## Assumptions
- apps/ 区域内的应用直接属于 SpecWeave 主仓库（不是 git submodule），SpecWeave 主权区可以直接修改
- apps 下的单个应用不需要都有 AGENTS.md，只有当应用自身包含复杂的 .agents/ 规范体系时才需要（如 zhujian-wudao、jupyter-ssh-base 等）
- 现有 `generate-apps-index.py` 脚本不需要修改（它只扫描 README.md 生成应用表格，不涉及 AGENTS.md）

## Acceptance Criteria

### AC-1: apps/AGENTS.md 存在且结构完整
- **Given**: apps/ 目录存在且包含多个子应用
- **When**: 智能体进入 apps/ 目录执行任务
- **Then**: 存在 apps/AGENTS.md 文件，包含：区域性质说明、应用路由表、嵌套优先级流程图、可用资产索引、边界声明、跨边界调用规范、异常处理分支
- **Verification**: `programmatic`
- **Notes**: 结构参照 projects/AGENTS.md 和 vendor/AGENTS.md，但在「区域性质」中明确区分 apps 是主仓库内应用与 projects 是 git submodule 的区别

### AC-2: apps/.agents/ 元数据容器存在
- **Given**: apps/AGENTS.md 已创建
- **When**: 检查 apps 目录结构
- **Then**: 存在 apps/.agents/ 目录及 README.md 文件，作为 apps 区域元数据容器
- **Verification**: `programmatic`

### AC-3: 根 AGENTS.md 启动协议覆盖三大子区域
- **Given**: 智能体启动并读取根 AGENTS.md
- **When**: 执行步骤 2.1（区域路由判断）
- **Then**: 启动协议依次判断工作目录是否在 apps/、projects/、vendor/ 内，并指引读取对应区域的 AGENTS.md
- **Verification**: `programmatic` + `human-judgment`
- **Notes**: 建议使用统一的判断流程图而非三个独立的 if 判断

### AC-4: 四大区域对比表清晰明确
- **Given**: 新人阅读根 AGENTS.md
- **When**: 查看区域边界说明
- **Then**: 存在一张对比表，包含：目录、用途、维护方式、版本控制策略、是否可直接修改、AGENTS.md 入口
- **Verification**: `human-judgment`
- **Notes**: 新人应能在 30 秒内理解四个区域的区别

### AC-5: 上下文路由表包含 apps 入口
- **Given**: 智能体查阅 .agents/context-routing.md
- **When**: 查找 apps 相关规范
- **Then**: 常规任务路由表中包含 apps 区域入口（apps/AGENTS.md、app-development-workflow 协议等）
- **Verification**: `programmatic`

### AC-6: apps/README.md 引用 AGENTS.md 入口
- **Given**: 开发者或智能体查看 apps/README.md
- **When**: 阅读文档开头
- **Then**: README.md 顶部有指向 AGENTS.md 的智能体入口说明
- **Verification**: `human-judgment`

### AC-7: 根 AGENTS.md 核心规范入口表包含三大区域入口
- **Given**: 智能体查阅核心规范入口表
- **When**: 寻找区域入口文档
- **Then**: 表格中包含 apps/AGENTS.md、projects/AGENTS.md、vendor/AGENTS.md 三个条目
- **Verification**: `programmatic`

### AC-8: 所有链接有效无断链
- **Given**: 所有修改完成
- **When**: 运行链接检查
- **Then**: 新增和修改的文件中无断链，所有相对路径引用正确
- **Verification**: `programmatic`
- **Notes**: 使用 `python .agents/scripts/check-links.py --path .trae/specs/core-foundation/establish-four-region-routing-system/../../..` 验证（至少检查 AGENTS.md、apps/、.agents/context-routing.md）

### AC-9: 结构对称性验证
- **Given**: 三个子区域的 AGENTS.md 都存在
- **When**: 对比三个文件的章节结构
- **Then**: apps/AGENTS.md 与 projects/AGENTS.md、vendor/AGENTS.md 具有一致的章节编排（区域性质→路由表→嵌套优先级→资产索引→边界声明→调用规范→异常处理）
- **Verification**: `human-judgment`

## Open Questions
- [ ] 是否需要在 apps/AGENTS.md 中明确规定单个 app 何时需要自己的 AGENTS.md？（建议：当 app 包含自己的 .agents/ 目录或复杂规范体系时）
