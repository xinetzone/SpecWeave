---
id: "gotchas-domain-specialization"
domain: "methodology"
layer: "methodology"
maturity: "L1"
validation_count: 1
reuse_count: 0
documentation_level: "basic"
source: "external: 已迁移-.agents/insights/packaging/xmnn-packager-agents-skills-roles-retrospective-20260706.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/ai-collaboration/gotchas-domain-specialization.toml"
rules: []
references: []
skills: []
related_patterns:
  -   - "skill-five-elements-model"
  -   - "immutable-constraint-documentation"
  -   - "ai-agent-workspace-handbook"
---
# Gotchas 领域特化：在通用模板框架上补充模块特有陷阱

## 模式概述

在 SKILL-TEMPLATE.md 的通用 Gotchas 框架（编码/环境、时序/等待、工具使用三类）基础上，为每个模块级 Skill 新增领域特化小节（如 12.4 节），补充模块特有的陷阱与反直觉行为。核心机制：通用框架提供基线覆盖 + 领域特化补充模块特有踩坑经验。

## 问题现象

SKILL-TEMPLATE.md 的 Gotchas 章节（第 12 节）提供了三类通用陷阱模板：

- 12.1 编码/环境陷阱（Windows GBK、路径分隔符、绝对路径 vs 相对路径）
- 12.2 时序/等待陷阱（页面加载等待、CI 脚本执行顺序、异步操作确认）
- 12.3 工具使用陷阱（Edit 工具前提、Write 工具覆盖、browser 工具协议、Skill 调用边界）

但这些通用陷阱无法覆盖模块特有的领域知识：

1. **CMake 路径陷阱**：Docker 容器内路径与宿主机的 CMakeCache.txt 路径不一致，导致跨环境构建失败
2. **pip 包名冲突**：模块的 pip 包名与系统中其他包的顶层模块名冲突，import 静默解析到错误位置
3. **构建阶段混淆**：CMake 编译和 Wheel 打包是两个独立阶段，混在一起执行会导致各种奇怪错误
4. **权限陷阱**：Docker 容器挂载宿主目录时，UID/GID 不匹配导致 ccache 等工具无法写入

这些陷阱不出现在通用模板中，但对于该模块的智能体操作至关重要。如果不在 SKILL.md 中显式声明，智能体将反复踩坑。

## 解决方案

### 核心机制：模板框架 + 领域补充

在遵循 SKILL-TEMPLATE.md 第 12 节通用 Gotchas 结构的基础上，在模块级 Skill 的 Gotchas 章节中新增领域特化小节：

```markdown
## 12. Gotchas（陷阱与反直觉行为）

### 12.1 编码/环境陷阱
（通用模板内容，按需精简）

### 12.2 时序/等待陷阱
（通用模板内容，按需精简）

### 12.3 工具使用陷阱
（通用模板内容，按需精简）

### 12.4 xmnn-packager 特有陷阱
- **CMakeCache.txt 路径陷阱**：Docker 容器内路径（如 `/workspace/libs/npu_tvm/build`）与宿主机路径不同，CMakeCache.txt 持久化后会导致跨环境构建失败。症状：`cmake --build` 报找不到源文件。修复：删除 build 目录，用 `force=True` 重新配置
- **pip 包名冲突**：顶层包名如 `cli`、`utils` 会与系统中其他包冲突，import 静默解析到错误位置。症状：import 成功但找不到预期的函数/类。修复：使用项目前缀命名（如 `xmnn_pkg_cli`）
- **构建阶段不可混用**：CMake 编译（`tasks.py config()+make()`）和 Wheel 打包（`scikit-build-core`）是两个独立阶段，不可在同一条命令中混合执行
```

### 领域特化 Gotchas 的内容来源

从已有知识文档中提取，而非凭空编造：

| 来源 | 提取内容 |
|------|---------|
| build-workflow.md 常见问题 | CMake 缓存、构建阶段、环境变量相关陷阱 |
| no-llvm-support.md 故障排查 | LLVM 版本不匹配、链接错误相关陷阱 |
| docker-build.md 排障指南 | Docker 权限、挂载路径、用户映射相关陷阱 |
| configuration.md 约束说明 | 配置参数互斥、默认值覆盖相关陷阱 |

### 编写原则

1. **每条陷阱包含三要素**：症状（如何识别）→ 根因（为什么发生）→ 修复（如何解决）
2. **从实际出发**：只写已踩过的坑，不写"可能"发生的陷阱
3. **与通用框架不重复**：通用框架（12.1-12.3）已覆盖的不再写
4. **保持精炼**：每条陷阱 2-4 行，不超过 5 行

## 适用场景

- 使用 SKILL-TEMPLATE.md 五要素模型创建模块级 Skill
- 模块有领域特有的构建/部署/配置陷阱
- 模块的陷阱已被知识文档记录，需要在 Skill 中显式告知智能体
- 多个 Skill 有共享的领域陷阱（可通过 references/ 复用）

## 实际案例

### xmnn-packager 三个 Skill 的 Gotchas 领域特化

**背景**：SKILL-TEMPLATE.md 的 Gotchas 框架提供了通用陷阱模板，但 xmnn-packager 模块有多个特有的陷阱需要告知智能体。

**实施**：在 cmake-build-cmd/SKILL.md、nuitka-compile-cmd/SKILL.md、wheel-package-cmd/SKILL.md 中，均在通用 Gotchas 后新增 12.4 节领域特化陷阱。

**具体陷阱示例**：

| Skill | 领域特化陷阱 |
|-------|------------|
| cmake-build-cmd | CMakeCache.txt 路径不一致（Docker vs 宿主机）、force 参数必要性 |
| nuitka-compile-cmd | Docker 内 ccache 权限问题、LLVM 版本不匹配导致链接错误 |
| wheel-package-cmd | pip 包名冲突、scikit_build_core.build 不支持直接 CMake 执行 |

**效果**：智能体在操作这些 Skill 时，能提前避开领域特有陷阱，避免反复踩坑后再查排障文档。

## 反模式

### 反模式 1：完全跳过 Gotchas 章节

```
Skill 定义中没有 Gotchas 章节，或只写了"暂无"
```

→ 智能体在遇到陷阱时没有预警，只能通过试错发现，反复踩坑。

**正确做法**：每个 Skill 至少包含通用 Gotchas 框架，如有领域特有陷阱则补充 12.4 节。

### 反模式 2：领域特化陷阱过于泛化

```
12.4 节写"注意权限问题"、"注意路径正确性"
```

→ 没有症状、根因、修复三要素，智能体不知道具体如何识别和处理。

**正确做法**：每条陷阱包含"症状 → 根因 → 修复"三要素，足够具体可操作。

### 反模式 3：在通用小节中混入领域陷阱

```
在 12.1 编码/环境陷阱中混入 CMakeCache.txt 路径问题
```

→ 通用框架和领域特化混在一起，其他模块复用通用框架时被误导。

**正确做法**：通用陷阱放在 12.1-12.3，领域特有陷阱放在独立的 12.4（或更高编号）节。

## 与其他模式的关系

| 关系模式 | 关系类型 | 说明 |
|---------|---------|------|
| [skill-five-elements-model.md](skill-five-elements-model.md) | 上位 | Gotchas 是五要素模型中"要素 4：Why-Explanation"和"要素 5：Safety Checklist"的补充 |
| [immutable-constraint-documentation.md](../governance-strategy/immutable-constraint-documentation.md) | 互补 | 不可变约束清单记录项目级约束，Gotchas 记录 Skill 操作级陷阱，两者互补 |
| [ai-agent-workspace-handbook.md](ai-agent-workspace-handbook.md) | 支撑 | 工作手册中的知识文档是 Gotchas 内容的主要来源 |

## 边界与选型

**何时使用本模式**：
- 模块有 2 个以上领域特有陷阱
- 陷阱已被知识文档记录，但未在 Skill 中显式告知智能体
- 陷阱具有"不报错但结果不符合预期"的反直觉特征

**何时不需要**：
- 模块没有领域特有陷阱 → 仅使用通用 Gotchas 框架即可
- 陷阱仅出现一次，不会再发生 → 留在复盘报告中，不沉淀为 Skill 陷阱
- 陷阱是通用性（非模块特有）的 → 应提交到 SKILL-TEMPLATE.md 的通用框架中

## Changelog

- **v1.0.0** (2026-07-06): 初始版本，基于 xmnn-packager .agents/ skills/ 创建复盘萃取