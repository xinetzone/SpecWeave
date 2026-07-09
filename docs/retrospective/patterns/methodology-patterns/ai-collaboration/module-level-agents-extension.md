---
id: "module-level-agents-extension"
domain: "methodology"
layer: "methodology"
maturity: "L1"
validation_count: 1
reuse_count: 0
documentation_level: "basic"
source: ".agents/insights/packaging/xmnn-packager-agents-skills-roles-retrospective-20260706.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/ai-collaboration/module-level-agents-extension.toml"
rules: []
references: []
skills: []
related_patterns:
  - "ai-agent-workspace-handbook"
  - "progressive-context-disclosure"
  - "convention-driven-creation"
---
# 模块级 .agents/ 扩展模式：通过继承避免重复，仅补充模块特化

## 模式概述

当项目采用"父项目 + 子模块"的多层目录结构时，子模块的 `.agents/` 目录（roles/、skills/）不应重复父项目的通用定义，而应通过 `extends` 声明继承父角色，仅补充模块特化的职责和技能。核心机制：roles/ 用 `extends` 建立继承链 + skills/ 按操作域拆分 + 仅补充"模块特化职责"和"Non-Goals"。

## 问题现象

在大型项目中，子模块往往有自己的 CLI 工具或操作域，需要为 AI 智能体补充模块级知识文档。常见错误做法：

1. **全量复制父角色**：在子模块 roles/ 中完整复制父项目的角色定义，导致维护成本翻倍，父角色更新后子模块不同步
2. **角色粒度混乱**：子模块定义了与父项目重叠的角色，智能体不知道优先读取哪个
3. **技能定义冗余**：子模块 skills/ 中重复描述父项目已定义的通用操作流程
4. **职责边界模糊**：子模块角色不知道自己该做什么、不该做什么，缺少"Non-Goals"约束

## 解决方案

### 核心机制：继承 + 特化

```
父项目 .agents/roles/developer.md  (父角色)
        ↓ extends
子模块 .agents/roles/build-engineer.md  (模块特化)
```

### 三步实施法

**步骤 1：roles/ 继承声明**

每个子模块角色用 `extends` 声明继承关系，仅补充"模块特化职责"和"Non-Goals"：

```markdown
---
id: "build-engineer"
extends: "../../../client/sdk/AI/.agents/roles/developer.md"
tier: "standard"
---
# 构建工程师（Build Engineer）

## 继承声明
本角色继承 [developer](../../../client/sdk/AI/.agents/roles/developer.md) 的全部职责，
并在此基础上增加 xmnn-packager 模块特化职责。

## 模块特化职责
- 执行 `xmnn-pkg build cmake` 编译 TVM C/C++ 源码
- 通过 `xmnn-pkg nuitka execute` 执行 Nuitka 编译
- 通过 `xmnn-pkg package build` 打包 Wheel

## Non-Goals
- 不负责 TVM 核心代码修改（由父项目 developer 负责）
- 不负责 Docker 镜像构建（由 docker-build 知识文档覆盖）
```

**步骤 2：skills/ 按操作域拆分**

每个子模块 Skill 对应一个核心 CLI 命令，遵循五要素模型：

```
xmnn-pkg CLI 命令
├── build cmake      → cmake-build-cmd/SKILL.md
├── nuitka execute   → nuitka-compile-cmd/SKILL.md
└── package build    → wheel-package-cmd/SKILL.md
```

**步骤 3：索引同步更新**

更新 AGENTS.md 和 `.agents/overview.md` 的索引表，新增 roles/skills 条目，确保智能体可以通过路由表发现模块级能力。

### 关键约束

| 约束 | 说明 |
|------|------|
| 不重复父角色 | roles/ 中每个角色必须声明 `extends`，不完整复制父角色内容 |
| 仅补充特化 | 只写"模块特化职责"和"Non-Goals"，通用职责由继承链解决 |
| 操作域粒度 | 每个 Skill 对应一个核心 CLI 命令，不多不少 |
| 目录名同步 | 索引表中的目录名必须与实际模块目录名一致（如 `xmnn_pkg_cli/`） |

## 适用场景

- 父项目已定义通用智能体角色（developer/reviewer/tester 等）
- 子模块有独立的 CLI 工具或操作域
- 子模块有领域特有的陷阱和约束需要告知智能体
- 需要保持角色层次清晰，避免"每个子模块都重新定义一遍角色"

## 实际案例

### xmnn-packager 模块 .agents/ 扩展

**背景**：xmnn-packager 是 `server/dev-env/` 下的子模块，有独立的 CLI 工具（xmnn-pkg），父项目 `client/sdk/AI/` 已定义 7 个通用智能体角色。

**原始状态**：`.agents/` 仅有 6 个知识文档（overview、commands、build-workflow 等），缺少 roles/ 和 skills/ 目录。

**实施过程**：

1. 创建 `roles/build-engineer.md`，通过 `extends` 继承父项目 `developer` 角色
2. 创建 3 个 Skill（cmake-build-cmd、nuitka-compile-cmd、wheel-package-cmd），每个对应一个核心 CLI 命令
3. 每个 Skill 包含 `references/index.md` 引用已有知识文档
4. 更新 AGENTS.md 和 overview.md 索引表

**效果**：build-engineer 角色仅 39 行（vs 完整复制 developer 约 100+ 行），维护成本大幅降低，父角色更新自动传递到子模块。

## 反模式

### 反模式 1：全量复制父角色

```
子模块 roles/developer.md 中完整复制父项目的 developer 角色定义
```

→ 父角色更新后子模块不同步，维护两份几乎相同的文档，浪费精力且容易产生不一致。

**正确做法**：使用 `extends` 声明继承，仅补充模块特化职责。

### 反模式 2：角色粒度与父项目重叠

```
子模块定义了 developer、reviewer、tester 等与父项目完全相同的角色
```

→ 智能体不知道优先读取哪个，职责边界模糊，容易产生冲突。

**正确做法**：子模块只定义模块特化角色（如 build-engineer），通用角色由父项目覆盖。

### 反模式 3：skills/ 中重复定义通用流程

```
子模块 Skill 中详细描述了"如何运行测试"、"如何进行代码审查"等通用流程
```

→ 与父项目 skills/ 重复，维护成本翻倍，通用流程更新后子模块遗漏。

**正确做法**：子模块 Skill 只描述模块特化的 CLI 命令操作，通用流程通过 references/ 引用父项目文档。

## 与其他模式的关系

| 关系模式 | 关系类型 | 说明 |
|---------|---------|------|
| [ai-agent-workspace-handbook.md](ai-agent-workspace-handbook.md) | 前置 | 本模式是工作手册模式在多层项目结构中的扩展应用 |
| [progressive-context-disclosure.md](progressive-context-disclosure.md) | 互补 | 继承机制本身就是渐进式披露的一种实现——智能体先读父角色再读子角色特化 |
| [convention-driven-creation.md](../governance-strategy/convention-driven-creation.md) | 支撑 | 继承声明（extends）是约定驱动创建的具体体现 |

## 边界与选型

**何时使用本模式**：
- 项目有明确的"父项目 + 子模块"多层目录结构
- 父项目已定义完整智能体角色体系
- 子模块有独立操作域，需要告知智能体模块特有信息

**何时不需要**：
- 独立项目（无父项目）→ 直接定义完整角色，无需继承
- 子模块没有独立操作域 → 不需要模块级 .agents/ 扩展
- 父项目角色体系不完善 → 先完善父项目角色，再考虑子模块扩展

## Changelog

- **v1.0.0** (2026-07-06): 初始版本，基于 xmnn-packager .agents/ skills/roles 扩展复盘萃取