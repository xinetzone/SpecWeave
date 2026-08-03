# Zleap-Agent Workspace-first 架构落地原型 - The Implementation Plan

## [x] Task 1: 创建 Python 原型目录结构
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 `apps/` 下创建独立原型目录（如 `apps/zleap-workspace-first-prototype/`）
  - 规划模块划分：workspace.py / context.py / tools.py / memory.py / runtime.py / boundary.py / main.py
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录结构与模块划分符合五大模块边界
  - `human-judgement` TR-1.2: 每个模块对应一个核心概念（Context/Tools/Memory/Runtime/Boundary）
- **Notes**: 原型目录需遵循 apps/ 应用开发规范

## [x] Task 2: 实现 Workspace 类
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 实现 `Workspace` 类，包含 workspace_id、name、prompt、tools、memory、model 等属性
  - 实现"先选工作区"的核心逻辑（Main 工作区作为调度台）
  - 支持工作区注册与查询
- **Acceptance Criteria Addressed**: [AC-1, AC-2]
- **Test Requirements**:
  - `programmatic` TR-2.1: 能创建 Workspace 实例并设置属性
  - `programmatic` TR-2.2: 能注册多个工作区并查询
- **Notes**: 对应 FR-1

## [x] Task 3: 实现 ContextAssembler 类
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 实现 `ContextAssembler` 类，按 `Context = System Prompt + Workspace Prompt + Tools + Memory + History` 公式装配上下文
  - 支持 Prefetch（预取）与 Agentic（按需读取）两种加载方式
- **Acceptance Criteria Addressed**: [AC-1, AC-2]
- **Test Requirements**:
  - `programmatic` TR-3.1: 装配后的上下文包含所有组成部分
  - `human-judgement` TR-3.2: 装配顺序符合公式
- **Notes**: 对应 FR-2

## [x] Task 4: 实现 Tools 注册与工作区绑定
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 实现工具注册机制（工具名、描述、函数）
  - 实现工具与工作区绑定，工具不全局暴露
  - 实现"当前工作区可见工具集"查询
- **Acceptance Criteria Addressed**: [AC-1, AC-2]
- **Test Requirements**:
  - `programmatic` TR-4.1: 一个工作区只能看到绑定的工具
  - `programmatic` TR-4.2: 工具 schema 可按工作区获取
- **Notes**: 对应 FR-3

## [x] Task 5: 实现 Memory 三分区与双线设计
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 实现 Memory 三分区（人/事/经验）
  - 实现双线设计（A 线 people notes / B 线 core records）
  - 实现经验记忆准入规则（允许 4 类 / 禁止 6 类）
- **Acceptance Criteria Addressed**: [AC-1, AC-2]
- **Test Requirements**:
  - `programmatic` TR-5.1: 记忆可按分区存取
  - `programmatic` TR-5.2: 经验准入规则能拦截禁止项
- **Notes**: 对应 FR-4

## [x] Task 6: 实现 Runtime 轨迹记录
- **Priority**: medium
- **Depends On**: Task 3, Task 4
- **Description**:
  - 实现 Runtime 轨迹记录（记录读取的上下文、调用的工具、执行结果）
  - 支持轨迹查询与审计
- **Acceptance Criteria Addressed**: [AC-1, AC-2]
- **Test Requirements**:
  - `programmatic` TR-6.1: 每次执行后能查询到轨迹记录
  - `human-judgement` TR-6.2: 轨迹包含关键信息（上下文/工具/结果）
- **Notes**: 对应 FR-5

## [x] Task 7: 实现 Boundary 四类边界检查
- **Priority**: medium
- **Depends On**: Task 4, Task 5
- **Description**:
  - 实现数据边界（不出内网）、工具边界（按工作区可见）、模型边界（按工作区绑定）、记忆边界（不跨用户/任务串）
  - 实现边界检查方法
- **Acceptance Criteria Addressed**: [AC-1, AC-2]
- **Test Requirements**:
  - `programmatic` TR-7.1: 越界访问被拦截
  - `human-judgement` TR-7.2: 四类边界均有检查
- **Notes**: 对应 FR-6

## [x] Task 8: 编写 main.py 演示入口
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4, Task 5, Task 6, Task 7
- **Description**:
  - 编写 `main.py`，演示"先选工作区再组装上下文"的完整流程
  - 演示 Main 工作区调度到具体业务工作区
  - 演示工具绑定、记忆分区、轨迹记录、边界检查
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `programmatic` TR-8.1: `python main.py` 可运行无报错
  - `human-judgement` TR-8.2: 演示覆盖五大模块
- **Notes**: 对应 FR-7

## [x] Task 9: 生成 7 个行动项任务清单
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 提取复盘行动项 backlog 中的 7 个行动项（A-01 至 A-07）
  - 生成按优先级排序的任务清单（高/中/低）
  - 标注关联洞察与验收标准
- **Acceptance Criteria Addressed**: [AC-3, AC-4]
- **Test Requirements**:
  - `programmatic` TR-9.1: 7 个行动项全部提取，无遗漏
  - `human-judgement` TR-9.2: 每项含优先级与验收标准
- **Notes**: 对应 FR-8, FR-9

## [x] Task 10: 生成思维导图结构
- **Priority**: medium
- **Depends On**: None
- **Description**:
  - 用 Mermaid 将核心概念（Context/Tools/Memory/Runtime/Boundary/Workspace-first）整理为思维导图
  - 覆盖五大模块、核心公式、加载方式、对照案例
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `human-judgement` TR-10.1: 思维导图覆盖所有核心概念
  - `human-judgement` TR-10.2: 层次结构清晰
- **Notes**: 对应 FR-10

## [x] Task 11: 原型代码验证与运行
- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - 运行 `python main.py` 验证原型可运行
  - 对照 checklist.md 逐项验证
  - 修复发现的问题
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3, AC-4, AC-5]
- **Test Requirements**:
  - `programmatic` TR-11.1: 原型运行无报错
  - `human-judgement` TR-11.2: 所有验收标准满足
- **Notes**: 完成最终验证

# Task Dependencies
- Task 1 → Task 2（目录结构先建立）
- Task 2 → Task 3, Task 4, Task 5（Workspace 是基础）
- Task 3, Task 4 → Task 6（上下文与工具完成后才能记录轨迹）
- Task 4, Task 5 → Task 7（工具与记忆完成后才能做边界检查）
- Task 2, 3, 4, 5, 6, 7 → Task 8（main.py 依赖所有模块）
- Task 8 → Task 11（验证依赖 main.py）
- Task 9, Task 10 独立于代码任务，可并行