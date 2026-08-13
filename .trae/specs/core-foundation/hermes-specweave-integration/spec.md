---
id: "hermes-specweave-integration-spec"
title: "Hermes 深度集成 SpecWeave 工作区规范"
source: "用户需求：功能调研 hermes-agent + 探索+洞察进化路径 + 集成 .agents/AGENTS.md"
date: "2026-08-12"
tags: ["Hermes", "SpecWeave", "插件", "技能", "上下文路由", "启动协议", "三层路由", "自我演进"]
---

# Hermes 深度集成 SpecWeave 工作区规范 - Product Requirement Document

## Overview
- **Summary**: 为 Hermes Agent 创建一个 **SpecWeave 工作区感知插件**（`specweave-bridge`），使 Hermes 在 SpecWeave 仓库中运行时能够：(1) 识别并遵循根目录 `AGENTS.md` 启动协议；(2) 通过三层路由（SpecWeave → 子区域 apps/projects/vendor → 子应用）按需加载 `.agents/` 下的规范、角色、技能、脚本；(3) 将 SpecWeave 的 19 个 Skill 门面（ci-check/docgen/insight/mermaid/seven-concepts 等）桥接为 Hermes 可调用的技能和工具；(4) 保持 Hermes 原有的提示词缓存友好性（三层缓存架构），最小化核心侵入。采用 Hermes Footprint Ladder 原则：优先通过 Plugin + Skills 实现，不修改核心源码。
- **Purpose**: 让 Hermes 在 SpecWeave 工作区中获得与 Trae IDE 中相同的结构化规范遵循能力——启动即读 AGENTS.md、按需路由加载规范、调用验证脚本、执行方法论工作流。解决当前 Hermes 仅简单合并 AGENTS.md 文本而无法理解其路由语义、无法按需加载 .agents/ 深层规范的问题。
- **Target Users**: SpecWeave 项目维护者、使用 Hermes CLI/TUI/Dashboard 在 SpecWeave 仓库中工作的 AI 工程师和开发者。

## Goals
- **G1**: Hermes 进入 SpecWeave 工作区时自动识别 AGENTS.md 启动协议，按步骤 2.0-2.3 完成任务类型预检、内容敏感度判定、路由定位
- **G2**: 将 SpecWeave 的 19 个 Skill 门面（`.agents/skills/`）封装为 Hermes 可发现、可调用的技能包，通过 `/skill-name` 斜杠命令或技能索引自动暴露
- **G3**: 将 SpecWeave 核心验证脚本（`.agents/scripts/check-*.py` 等）桥接为 Hermes 服务门控工具（service-gated tools），按需要可用
- **G4**: 实现上下文路由感知：当 cwd 在 apps/projects/vendor 子区域时，自动加载对应子区域 AGENTS.md 路由
- **G5**: 遵循 Hermes 提示词缓存三层架构（stable/context/volatile），将 SpecWeave 规范放在 volatile 层最前面（技能索引位置），稳定前缀保持可缓存
- **G6**: 插件不修改 Hermes 核心源码，纯插件+技能包形式安装，可通过 `hermes plugins enable/disable` 切换

## Non-Goals (Out of Scope)
- **NG1**: 不将 SpecWeave 全部 133+ 规则文件、341+ 脚本一次性加载进系统提示词（违反按需加载原则和缓存友好性）
- **NG2**: 不实现 SpecWeave 的 `.trae/specs/` Spec Mode 工作流执行引擎（那是 Trae IDE 的职责，Hermes 侧只提供规范加载和工具调用能力）
- **NG3**: 不将 vendor/flexloop chaos 的 Skill 开发方法论完整移植为 Hermes 核心技能（通过现有 hermes skill 机制按需调用即可）
- **NG4**: 不修改 Hermes 内置的 `build_context_files_prompt` 逻辑（插件通过 hook + on_session_start 注入增强上下文）
- **NG5**: 不集成飞书/Lark/论坛等外部服务工具（那些已有独立 Skill，通过 MCP 或外部工具处理）

## Background & Context
- **Hermes 现有机制**:
  - 上下文文件发现：从 cwd 向上找 `.hermes.md`，目录链合并 `AGENTS.md`，加载 `CLAUDE.md`/`.cursorrules`
  - 三层缓存提示词架构：stable（身份/工具指导）→ context（工作区快照/上下文文件）→ volatile（技能索引/记忆/时间戳）
  - 插件系统：PluginContext API 可注册 tools/hooks/commands/cli 子命令，通过 plugin.yaml 声明
  - 技能系统：`skills/` 目录按分类组织，frontmatter 元数据，`/skill-name` 斜杠命令调用，curator 后台维护生命周期
  - 服务门控工具：`check_fn` 返回 False 时工具从 schema 中隐藏，零 footprint
- **SpecWeave 现有机制**:
  - AGENTS.md 启动协议：步骤 1（读全文）→ 步骤 2（上下文路由，含 vendor 预检和内容敏感度预检）→ 步骤 3（读对应规范）→ 步骤 3.5（自检）→ 步骤 4（执行）
  - 三层路由体系：SpecWeave 主权区 → apps/projects/vendor 子区域 → 子应用/子项目/子模块
  - .agents/ 双层治理：Core 层（rules/protocols/roles/workflows 规范）+ Tools 层（skills 门面/scripts 实现）
  - 19 个 Skill 门面：ci-check/docgen/insight/mermaid/forum-posting/link-check/atomization/atomic-commit/retrospective/extraction/export-report/seven-concepts/check-duplication 等
  - 341+ Python 验证脚本：check-links/check-vendor/check-gitignore/check-stage-guardrails 等
- **Gap（当前缺失）**:
  - Hermes 加载 AGENTS.md 时只是纯文本合并，不理解"启动协议"是一个需要执行的流程（步骤 2.0-3.5 的自检清单）
  - Hermes 不知道 .agents/ 目录的渐进式披露架构（L0/L1/L2），会尝试一次性加载所有内容或根本不知道里面有可调用工具
  - SpecWeave 的 Skill 门面遵循五要素模型但格式与 Hermes Skill 不完全一致（需要桥接转换）
  - cwd 在 apps/xxx/ 下时 Hermes 不会自动加载 apps/AGENTS.md 的子区域路由表

## Functional Requirements
- **FR-1**: 插件 `specweave-bridge` 自动检测当前工作目录是否为 SpecWeave 仓库（存在 AGENTS.md 且包含"启动协议"关键词）
- **FR-2**: 检测到 SpecWeave 工作区后，通过 `on_session_start` hook 注入 SpecWeave 启动协议指导到系统提示词 volatile 层
- **FR-3**: 提供 `specweave_route` 工具：根据任务类型返回需要加载的规范文件路径列表（遵循 context-routing.md 的映射表）
- **FR-4**: 将 SpecWeave 19 个 Skill 门面封装为 Hermes 技能包，安装到 `~/.hermes/skills/specweave/` 下，分类组织，frontmatter 适配 Hermes 格式
- **FR-5**: 将核心验证脚本（check-links/check-vendor/check-duplication/check-stage-guardrails/check-spec-consistency 等）注册为 Hermes 服务门控工具，`check_fn` 检测在 SpecWeave 工作区内时可用
- **FR-6**: 实现子区域路由感知：cwd 在 apps/projects/vendor 内时，自动加载对应区域 AGENTS.md 入口并在路由工具中体现
- **FR-7**: 提供 `specweave_status` CLI 子命令（`hermes specweave status`），显示当前检测状态、已加载规范、可用技能
- **FR-8**: 提供 `/specweave-load` 斜杠命令：允许用户手动触发指定规范的加载（如 `/specweave-load context-routing`）
- **FR-9**: 技能包包含使用说明：每个 Skill 门面转换为 Hermes 技能时，说明对应的调用方式和脚本路径
- **FR-10**: 不污染非 SpecWeave 工作区：插件在非 SpecWeave 目录中零 footprint（工具隐藏、提示词无额外内容）

## Non-Functional Requirements
- **NFR-1**: 提示词缓存友好：SpecWeave 相关内容注入 volatile 层技能索引位置，stable 层保持字节稳定，不破坏前缀缓存
- **NFR-2**: 零侵入核心：所有功能通过 Plugin API 实现，不 patch Hermes 核心文件
- **NFR-3**: 按需加载：默认只加载 L0（AGENTS.md + ONBOARDING.md）+ 路由表（L1），L2 深度规范只在 `specweave_route` 工具被调用时读取
- **NFR-4**: 路径兼容 Windows：处理 Windows 路径分隔符、Conda 环境路径、UTF-8 BOM
- **NFR-5**: 可卸载：插件禁用后不留残余，所有注入的技能/工具/提示词消失
- **NFR-6**: 中文优先：技能描述、工具描述、提示词指导以中文为主（与 SpecWeave 沟通语言规则一致）

## Constraints
- **Technical**: Python 3.11-3.13（与 hermes conda 环境一致），Hermes Plugin API 版本（v0.20.0），Windows 10/11 环境
- **Business**: 插件作为本地用户插件安装到 `~/.hermes/plugins/specweave-bridge/`（或项目级 `./.hermes/plugins/`），不提交到 hermes-agent 上游
- **Dependencies**:
  - Hermes 已安装（conda hermes 环境，v0.20.0）
  - SpecWeave 仓库路径：`c:\Users\admin\Desktop\Dao\flows\SpecWeave\`
  - 不引入新的第三方 Python 包依赖（使用 Hermes 已有依赖 + 标准库）

## Assumptions
- SpecWeave AGENTS.md 的"启动协议"在可预见未来保持基本结构（4步骤+自检清单）
- Hermes Plugin API 的 `on_session_start` hook 和 `register_tool`/`register_command` 接口在 v0.20.x 系列保持稳定
- 用户主要在 SpecWeave 根目录或子目录中启动 Hermes CLI/TUI
- `.agents/skills/` 下的 SKILL.md 格式保持五要素模型（description/触发条件/使用方式/验证/注意事项）

## Acceptance Criteria

### AC-1: SpecWeave 工作区自动检测
- **Given**: Hermes 在 SpecWeave 仓库根目录启动（存在 AGENTS.md 含"启动协议"）
- **When**: 会话开始
- **Then**: 插件检测到 SpecWeave 环境，系统提示词中包含 SpecWeave 启动协议简要指导，`specweave_route` 工具可用
- **Verification**: `programmatic`
- **Notes**: 检测通过特征文件 AGENTS.md + 内容关键词"启动协议"双重判定

### AC-2: 非 SpecWeave 工作区零影响
- **Given**: Hermes 在非 SpecWeave 目录启动
- **When**: 会话开始
- **Then**: specweave 相关工具不出现，系统提示词无额外 SpecWeave 内容，行为与未安装插件时一致
- **Verification**: `programmatic`

### AC-3: 启动协议指导注入
- **Given**: SpecWeave 工作区会话
- **When**: 检查系统提示词 volatile 层
- **Then**: 包含中文的 SpecWeave 启动协议步骤概览（步骤 1-4 精简版），指引 Hermes 先调用 `specweave_route` 获取路由信息再执行任务
- **Verification**: `human-judgment`

### AC-4: specweave_route 工具工作正常
- **Given**: SpecWeave 工作区会话
- **When**: 调用 `specweave_route(task_type="skill 创建")`
- **Then**: 返回需要读取的规范文件路径列表（如 vendor/flexloop skill-creator SKILL.md + rules/skill-development.md），文件路径为相对于 SpecWeave 根的路径
- **Verification**: `programmatic`

### AC-5: SpecWeave 技能包安装成功
- **Given**: 插件初始化完成
- **When**: 执行 `/skills` 或查看技能索引
- **Then**: specweave 分类下可见 19 个 Skill 的索引项（ci-check、docgen、insight、mermaid、seven-concepts 等），可通过 `/ci-check`、`/seven-concepts` 等斜杠命令调用
- **Verification**: `programmatic` + `human-judgment`

### AC-6: 验证脚本工具可用
- **Given**: SpecWeave 工作区会话
- **When**: 调用工具列表检查
- **Then**: `specweave_check_links`、`specweave_check_vendor`、`specweave_check_duplication`、`specweave_ci_check` 等工具在工具列表中可见
- **Verification**: `programmatic`

### AC-7: 子区域路由感知
- **Given**: Hermes 在 `apps/prompt_extraction/` 目录启动
- **When**: 调用 `specweave_route(task_type="功能开发")`
- **Then**: 返回路径包含 apps/AGENTS.md + 对应应用的 AGENTS.md（如存在）
- **Verification**: `programmatic`

### AC-8: CLI 状态命令
- **Given**: 插件已安装
- **When**: 执行 `hermes specweave status`
- **Then**: 输出当前是否在 SpecWeave 工作区、检测到的根路径、已注册工具数量、技能包状态
- **Verification**: `programmatic`

### AC-9: 提示词缓存不被破坏
- **Given**: SpecWeave 工作区多轮对话
- **When**: 进行多轮对话
- **Then**: stable 层前缀在轮次间保持字节稳定（不因 SpecWeave 插件注入内容导致每次重建），技能索引变化只影响 volatile 层尾部
- **Verification**: `human-judgment`（通过日志检查缓存命中）

### AC-10: 斜杠命令可用
- **Given**: SpecWeave 工作区 CLI 会话
- **When**: 输入 `/specweave-load context-routing`
- **Then**: 加载并显示 context-routing.md 的关键路由信息到对话上下文
- **Verification**: `human-judgment`

## Open Questions
- [ ] 技能包是安装到 `~/.hermes/skills/specweave/`（全局）还是 `./.hermes/skills/`（项目级）？建议：全局安装但通过 `check_fn` 控制在 SpecWeave 区内才出现在索引中
- [ ] SpecWeave 脚本调用时的 Python 环境：使用 Hermes 自身的 Python（conda hermes）还是系统 Python？建议：优先使用 Hermes 环境，脚本调用时设置正确的 cwd 和 PYTHONPATH
- [ ] 是否需要实现七概念方法论编排（seven-concepts-cmd）的 Hermes 原生调用（目前是 Trae Skill，Hermes 侧作为技能包还是直接桥接命令）？建议：先作为技能包封装指导文档，脚本直接调用
