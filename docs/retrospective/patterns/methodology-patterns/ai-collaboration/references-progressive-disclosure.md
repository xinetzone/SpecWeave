---
id: "references-progressive-disclosure"
domain: "methodology"
layer: "methodology"
maturity: "L1"
validation_count: 1
reuse_count: 0
documentation_level: "basic"
source: ".agents/insights/xmnn-packager-agents-skills-roles-retrospective-20260706.md"
rules: []
references: []
skills: []
related_patterns:
  - "progressive-context-disclosure"
  - "ai-agent-workspace-handbook"
  - "entry-container-separation"
---
# references/ 渐进式披露：通过引用已有知识文档避免内容重复

## 模式概述

在模块级 Skill 定义中，通过 `references/index.md` 引用已有知识文档，而非在 SKILL.md 中直接复制内容。核心机制：每个 Skill 目录下创建 `references/index.md`，按"核心参考"和"故障排查"分类列出文档链接，SKILL.md 正文中引用 references/ 而非直接复制。

## 问题现象

当模块已有丰富的知识文档（如 build-workflow.md、commands.md、docker-build.md）时，创建 Skill 定义时常见的错误做法：

1. **内容复制**：将已有知识文档的内容直接复制到 SKILL.md 中，导致同一信息出现在两个地方
2. **维护成本翻倍**：知识文档更新后，SKILL.md 中的副本不会同步更新，产生信息不一致
3. **SKILL.md 膨胀**：大量复制内容使 SKILL.md 超过 500 行上限，违反五要素模型规范
4. **信息过载**：智能体加载 SKILL.md 时被大量已有知识淹没，难以快速定位 Skill 特有的操作步骤

## 解决方案

### 核心机制：引用代替复制

```
Skill 目录/
├── SKILL.md              ← 仅包含 Skill 特有的操作步骤和决策树
└── references/
    └── index.md          ← 分类引用已有知识文档
```

### references/index.md 标准结构

```markdown
# 参考文档

## 核心参考
| 文档 | 路径 | 说明 |
|------|------|------|
| 构建工作流 | [build-workflow.md](../build-workflow.md) | CMake 编译完整流程 |
| CLI 命令参考 | [commands.md](../commands.md) | 全部 xmnn-pkg 命令 |
| 配置参考 | [configuration.md](../configuration.md) | 配置参数详解 |

## 故障排查
| 文档 | 路径 | 说明 |
|------|------|------|
| 无 LLVM 支持 | [no-llvm-support.md](../no-llvm-support.md) | LLVM 解耦场景排障 |
| Docker 构建 | [docker-build.md](../docker-build.md) | Docker 环境排障 |
```

### SKILL.md 中的引用方式

在 SKILL.md 正文中，不直接复制知识文档内容，而是通过内联引用指向 references/：

```markdown
## 依赖与前置准备

- **必读知识库**：构建工作流、CLI 命令参考、配置参考 —— 详见 [references/index.md](references/index.md)
- **构建环境**：Conda 环境 `py313`，详见 [commands.md](../commands.md#环境激活)
```

### 三层引用模型

```
SKILL.md（L1：Skill 门面，<500行）
  └── references/index.md（L2：分类索引，<50行）
        └── 已有知识文档（L3：详细内容，按需加载）
```

每一层都是对下一层的"渐进式披露"，智能体按需深入，无需一次性加载全部内容。

## 适用场景

- 模块已有丰富的知识文档（3 个以上）
- 知识文档内容可能独立更新（如构建流程变更、配置参数新增）
- Skill 定义需要引用已有知识但不应重复描述
- 需要保持 SKILL.md 在 500 行以内

## 实际案例

### xmnn-packager 三个 Skill 的 references/ 实现

**背景**：xmnn-packager 的 `.agents/` 目录已有 6 个知识文档，创建 3 个 Skill 时面临内容重复问题。

**实施过程**：

1. 为每个 Skill 创建 `references/index.md`（cmake-build-cmd、nuitka-compile-cmd、wheel-package-cmd）
2. 按"核心参考"和"故障排查"分类列出知识文档链接
3. SKILL.md 正文中通过 `详见 references/index.md` 引用，不复制内容

**效果对比**：

| 指标 | 无 references/（复制内容） | 有 references/（引用） |
|------|--------------------------|----------------------|
| SKILL.md 行数 | 估计 250-350 行 | 实际 142-152 行 |
| 知识文档更新后 | 需手动同步 SKILL.md | 自动生效，无需同步 |
| 信息一致性 | 两份副本，容易不一致 | 单一来源，始终一致 |
| 智能体认知负载 | 信息过载 | 按需加载，认知负担低 |

## 反模式

### 反模式 1：在 SKILL.md 中完整复制知识文档

```
SKILL.md 中完整复制 build-workflow.md 的 CMake 步骤、常见问题等内容
```

→ 知识文档更新后 SKILL.md 过期，智能体读到过时信息，导致错误操作。

**正确做法**：SKILL.md 仅写 Skill 特有的操作步骤和决策逻辑，已有知识通过 references/index.md 引用。

### 反模式 2：references/ 过于简略

```
references/index.md 仅写"参考 .agents/ 目录下的文档"
```

→ 没有具体分类和链接，智能体仍需自己搜索，失去了渐进式披露的意义。

**正确做法**：按"核心参考"和"故障排查"分类，每项列出具体文档路径和一句话说明。

### 反模式 3：同一内容在多个 Skill 中重复

```
cmake-build-cmd/SKILL.md 和 nuitka-compile-cmd/SKILL.md 都复制了 Docker 环境配置
```

→ 两个 Skill 中的 Docker 配置可能不同步，维护成本翻倍。

**正确做法**：Docker 环境配置统一放在知识文档中，各 Skill 的 references/ 都指向同一份文档。

## 与其他模式的关系

| 关系模式 | 关系类型 | 说明 |
|---------|---------|------|
| [progressive-context-disclosure.md](progressive-context-disclosure.md) | 上位 | 本模式是渐进式披露在 Skill 文档体系中的具体应用 |
| [ai-agent-workspace-handbook.md](ai-agent-workspace-handbook.md) | 前置 | 已有知识文档是工作手册体系的组成部分，references/ 是对其的索引层 |
| [entry-container-separation.md](../document-architecture/entry-container-separation.md) | 相关 | references/ 与 SKILL.md 的关系类似于"入口-容器分离"——SKILL.md 是入口，references/ 指向容器 |

## 边界与选型

**何时使用本模式**：
- 模块已有 3 个以上知识文档
- 知识文档内容可能独立更新
- 多个 Skill 需要引用相同的知识文档

**何时不需要**：
- 模块没有已有知识文档 → 直接写在 SKILL.md 中
- 知识文档内容极少（<20 行）→ 直接引用路径即可，无需 references/ 子目录
- Skill 内容完全独立，不依赖任何已有文档 → 无需 references/

## Changelog

- **v1.0.0** (2026-07-06): 初始版本，基于 xmnn-packager .agents/ skills/ 创建复盘萃取