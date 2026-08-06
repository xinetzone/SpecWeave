---
version: 1.0
created: 2026-07-06
source: "https://mp.weixin.qq.com/s/iiTmgbtrYHMMjQ7dn7CDrg"
x-toml-ref: "../../../../.meta/toml/.trae/specs/retrospectives-insights/create-zleap-workspace-first-prototype/spec.toml"
author: "基于Zleap-Agent Harness设计学习分析spec"
topic: "Workspace-first 架构 Python 原型"
tags: ["Zleap-Agent", "Workspace-first", "Python原型", "Agent Harness", "行动项", "思维导图"]
---

# Zleap-Agent Workspace-first 架构落地原型 Spec

## Overview

- **Summary**: 基于已完成的 Zleap-Agent Harness 设计学习笔记（`.trae/specs/retrospectives-insights/zleap-agent-harness-learning-analysis/spec.md`），本 spec 将理论架构落地为可运行的三类资产：① 一个实现 Workspace-first 核心思想的 Python 原型代码；② 基于复盘洞察的 7 个行动项任务清单与优先级排序；③ 将 Context、Tools、Memory 等核心概念整理为思维导图结构。
- **Purpose**: 将 spec 中的五大模块（Context/Tools/Memory/Runtime/Boundary）与 Workspace-first 设计哲学转化为可验证、可执行、可复用的工程资产，验证"先选工作区、再组装上下文"的落地可行性。
- **Target Users**: AI Agent 架构师、本地小模型应用开发者、企业私有化部署决策者、Agent 框架研究者

## Goals

- 实现 1 个可运行的 Workspace-first Python 原型（覆盖五大模块骨架）
- 提取 7 个行动项并生成带优先级排序的任务清单
- 将核心概念整理为结构化思维导图（Mermaid 形式）

## Non-Goals (Out of Scope)

- 不实现完整可用的生产级 Agent 框架（仅做架构原型）
- 不接入真实 LLM API（用 mock 模拟上下文装配）
- 不做 PostgreSQL 真实持久化（原型用内存存储模拟）
- 不实现 Memory Dream 离线整理等复杂机制（仅留接口）

## Background & Context

- **来源**：Zleap-Agent Harness 设计学习笔记（已完成的 spec），核心是 Workspace-first 设计哲学
- **核心公式**：`Context = System Prompt + Workspace Prompt + Tools + Memory + History`
- **五大模块**：Context（上下文装配）、Tools（工具工作区绑定）、Memory（人/事/经验三分区）、Runtime（可审计轨迹）、Boundary（四类边界）
- **行动项来源**：复盘洞察萃取出的 7 个行动项（A-01 至 A-07），位于 `.agents/docs/retrospective/reports/competitive-analysis/retrospective-zleap-agent-harness-learning-20260704/insight-action-backlog.md`

## Functional Requirements

### 交付物 1：Python 原型代码

**FR-1**: 实现 `Workspace` 类，包含 workspace_id、name、prompt、tools、memory、model 等属性
**FR-2**: 实现 `ContextAssembler` 类，按 `Context = System Prompt + Workspace Prompt + Tools + Memory + History` 公式装配上下文
**FR-3**: 实现 `Tools` 注册与工作区绑定机制，工具不全局暴露
**FR-4**: 实现 `Memory` 三分区（人/事/经验）与双线设计（people notes / core records）
**FR-5**: 实现 `Runtime` 轨迹记录（记录每次读取的上下文、调用的工具、结果）
**FR-6**: 实现 `Boundary` 四类边界检查（数据/工具/模型/记忆）
**FR-7**: 提供 `main.py` 演示入口，演示"先选工作区再组装上下文"的完整流程

### 交付物 2：行动项任务清单

**FR-8**: 提取 7 个行动项（A-01 至 A-07），生成任务清单
**FR-9**: 按优先级排序（高/中/低），标注关联洞察与验收标准

### 交付物 3：思维导图

**FR-10**: 用 Mermaid 将核心概念（Context/Tools/Memory/Runtime/Boundary/Workspace-first）整理为思维导图结构

## Non-Functional Requirements

- **NFR-1**: 原型代码可运行，无语法错误，`python main.py` 可执行
- **NFR-2**: 代码结构清晰，模块划分符合五大模块边界
- **NFR-3**: 思维导图结构层次清晰，覆盖所有核心概念
- **NFR-4**: 行动项清单与既有 backlog 一致，不遗漏

## Constraints

- **Technical**: 原型用 Python 标准库实现，不依赖第三方包（保证可运行）
- **Dependencies**: 依赖已完成的 Zleap-Agent 学习笔记 spec 与复盘行动项 backlog

## Acceptance Criteria

### AC-1: Python 原型可运行
- **Given**: 完成原型代码
- **When**: 运行 `python main.py`
- **Then**: 演示"先选工作区再组装上下文"流程，无报错
- **Verification**: `programmatic`

### AC-2: 五大模块均有实现
- **Given**: 原型代码
- **When**: 审查代码结构
- **Then**: Context/Tools/Memory/Runtime/Boundary 五个模块均有类实现
- **Verification**: `human-judgment`

### AC-3: 7 个行动项完整提取
- **Given**: 复盘行动项 backlog
- **When**: 生成任务清单
- **Then**: 7 个行动项（A-01 至 A-07）全部提取，无遗漏
- **Verification**: `programmatic`

### AC-4: 行动项含优先级排序
- **Given**: 任务清单
- **When**: 审查
- **Then**: 每项标注优先级（高/中/低）与验收标准
- **Verification**: `human-judgment`

### AC-5: 思维导图覆盖核心概念
- **Given**: 思维导图
- **When**: 审查
- **Then**: 覆盖 Context、Tools、Memory、Runtime、Boundary、Workspace-first 等核心概念
- **Verification**: `human-judgment`

## Open Questions

- [ ] Python 原型是否应接入真实 LLM API 还是仅 mock？
- [ ] 思维导图采用 Mermaid 还是纯文本缩进结构？
- [ ] 原型代码应放在哪个目录？（建议 apps/ 下创建独立原型目录）