---
id: "symmetric-directory-structure"
domain: "governance"
layer: "methodology-patterns/governance-strategy"
title: "对称目录结构设计（Symmetric Directory Structure）"
maturity: "L3"
maturity_level: "L3"
validation_count: 2
reuse_count: 0
documentation_level: "standard"
version: "1.0.0"
created_date: "2026-07-24"
last_updated: "2026-07-24"
source: "retro-establish-four-region-routing-system-20260724"
tags: ["directory-structure", "architecture-symmetry", "governance", "tech-debt-prevention", "template"]
trigger_conditions:
  - "新增顶层目录/区域时"
  - "架构评审检查结构一致性时"
  - "重构现有目录结构消除不对称时"
  - "定义新工作区模板时"
problem_solved: "架构演进过程中，新增目录时容易产生\"临时例外\"——\"这个区域比较简单，暂时不需要AGENTS.md\"。这些例外累积成结构性技术债务：有的区域有入口，有的没有；路由逻辑需要特殊处理；新加入的智能体/开发者无法预测去哪里找规范。本模式通过定义最小结构模板和对称检查表，确保所有同构区域结构一致，消除例外累积。"
related_patterns:
  - "three-layer-routing-protocol"
  - "entry-comparison-table"
  - "triple-entry-design"
  - "bootstrap-driven-self-evolution"
---
# 对称目录结构设计（Symmetric Directory Structure）

## 模式类型
治理模式（架构一致性/技术债务预防）

## 成熟度
L3 可复用级（已在apps/区域补齐实践中验证，对称结构模板可直接复用）

## 问题陈述

架构不对称是技术债务的隐形来源：

**不对称的典型演进路径**：
1. 初始只有vendor/区域，有完整AGENTS.md → ✅ 对称
2. 新增projects/区域，参考vendor建立AGENTS.md → ✅ 仍然对称
3. 新增apps/区域，\"这个比较简单，先不加AGENTS.md\" → ⚠️ 第一个例外
4. 智能体启动协议只判断vendor/，因为apps没有入口需要处理 → ⚠️ 逻辑开始特殊化
5. 又新增一个区域，参考apps的做法也不加AGENTS.md → ⚠️ 例外变成惯例
6. 此时路由逻辑需要多个if-else判断哪些区域有入口哪些没有 → ❌ 技术债务爆发
7. 重构时需要补齐所有缺失的入口，成本是当初建立的N倍 → 💥 非线性返工成本

**核心问题**：
- "最小可行入口"的成本极低（一个50行的AGENTS.md），但不对称的修复成本极高（重构启动协议、更新多处文档、验证所有路由）
- 每次做"临时例外"决策时，都低估了未来的重构成本（参见非线性返工成本定律）
- 不对称具有传染性：一个例外会成为后续例外的借口

## 解决方案

为同构区域定义"最小结构模板"，所有区域必须满足该模板；新增区域时通过对称检查表验证。

### 最小结构模板

所有顶层区域必须满足以下最小结构：

```
<region>/
├── AGENTS.md              # ✅ 必须有：区域入口路由
├── .agents/
│   └── README.md          # ✅ 必须有：元数据容器说明（即使内容极简）
└── README.md              # ⭐ 建议有：区域概览，包含智能体入口引用
```

#### 各文件最小内容要求

**AGENTS.md（必需）最小内容**：
```markdown
---
title: <区域名称> 入口路由
---
# <区域名称>

## 区域性质
<!-- 一句话说明该区域与其他区域的本质区别、管理方式、是否可直接修改 -->

## <子模块>路由表
| 名称 | AGENTS.md 入口 | .agents/ | 说明 |
|------|---------------|:---:|------|
| xxx | [xxx/AGENTS.md](xxx/AGENTS.md) | ✅/❌ | 说明 |
| yyy | —（遵循本层规范） | ❌ | 暂无独立规范 |

## 边界声明
<!-- 默认行为、权限约束、与其他区域的交互规则 -->
```

**.agents/README.md（必需）最小内容**：
```markdown
# <区域名称> 元数据容器

本目录是 <区域名称> 区域的规范元数据容器。

| 维度 | 本目录 | 子模块 .agents/ |
|------|--------|----------------|
| 归属 | 上层区域 | 子模块自有 |
| 内容 | 元数据/索引/路由 | 完整规范体系 |
| 可修改 | ✅ 可直接修改 | ✅ 按子模块规范修改 |
```

**README.md（建议）最小补充**：
在README顶部添加智能体入口引用：
```markdown
> **AI 智能体入口**：[AGENTS.md](AGENTS.md) — <区域>智能体路由与资产索引，.agents/ 目录为元数据容器。
```

### 新增区域对称检查表

新增任何顶层目录/区域前，必须逐项确认：

| 检查项 | 必需/建议 | 说明 |
|--------|----------|------|
| ▢ 该区域是否有自己的 AGENTS.md 入口文件？ | 必需 | 即使区域再简单，也要有最小入口 |
| ▢ AGENTS.md 是否包含「区域性质」章节？ | 必需 | 明确管理方式、是否可修改、与其他区域的区别 |
| ▢ AGENTS.md 是否包含「子模块路由表」？ | 必需 | 即使当前只有一个子模块或没有子模块，也要有表格 |
| ▢ AGENTS.md 是否包含「边界声明」？ | 必需 | 明确默认行为和跨区域交互规则 |
| ▢ 该区域是否有 .agents/README.md 元数据容器？ | 必需 | 即使为空，也要占位说明 |
| ▢ 上层路由表（根AGENTS.md）是否已注册该区域？ | 必需 | 在顶层对比表中添加一行 |
| ▢ 启动协议（步骤2.1）是否已覆盖该区域？ | 必需 | 在判断顺序中添加该区域 |
| ▢ context-routing.md 是否需要添加该区域的任务类型路由？ | 必需 | 如有任务类型需要进入该区域，必须注册 |
| ▢ 该区域的 README.md 是否包含智能体入口引用？ | 建议 | 方便人类发现AI入口 |
| ▢ 是否已从所有其他区域的视角验证路由可达？ | 建议 | 从其他区域进入该区域时路径正确 |

### 渐进式扩展路径

对称不是要求一步到位建立完整规范体系，而是要求"入口先行"：

```
阶段0：目录创建
  └── 立即建立最小AGENTS.md + .agents/README.md（对称占位）

阶段1：子模块加入
  └── 在路由表中注册子模块
  └── 子模块如有需要建立自己的AGENTS.md

阶段2：规范扩展
  └── 根据需要在.agents/下添加rules/roles/skills等
  └── 不需要的区域保持最小结构即可

阶段3：成熟稳定
  └── 规范体系完整，可作为其他区域的参考模板
```

**关键原则**：阶段0的最小结构是强制的，阶段1-3是按需扩展的。这样既保证了架构对称性，又不会造成过度设计。

### 对称性违反处理

如果发现现有结构不对称：

1. **识别缺口**：用对称检查表逐项扫描，列出缺失项
2. **补齐入口**：优先补齐AGENTS.md和.agents/README.md（成本最低，收益最高）
3. **更新路由**：同步更新上层路由表和启动协议
4. **验证回归**：确认新入口可被智能体正确发现和使用
5. **记录复盘**：分析不对称产生的原因，更新检查表防止再次发生

## 适用场景

| 场景 | 适用度 | 说明 |
|------|--------|------|
| 新增顶层工作区目录 | 核心场景 | 新目录创建时立即应用对称模板 |
| monorepo多区域架构 | 核心场景 | apps/projects/vendor等多区域结构一致性 |
| 多插件/多扩展架构 | 核心场景 | 每个插件/扩展有对称的入口结构 |
| 架构重构债务偿还 | 推荐 | 补齐历史遗留的不对称结构 |
| 项目模板/脚手架设计 | 推荐 | 模板内置对称结构，新项目天然一致 |
| 单目录小项目 | 不适用 | 不需要分区域，无需对称 |
| 临时实验目录 | 谨慎使用 | 短期存在的目录可以简化，但合并到主干前必须补齐 |

## 反模式警示

| 错误做法 | 后果 | 正确做法 |
|---------|------|---------|
| "这个区域简单，先不加AGENTS.md" | 第一个例外产生，不对称开始累积 | 即使50行的最小AGENTS.md也要先建立 |
| 只给"重要"区域建立入口，"次要"区域不管 | 路由逻辑特殊化，维护成本指数上升 | 所有同构区域一视同仁，都有最小入口 |
| 等区域"成熟"了再补规范 | 早期没有规范导致错误累积，补的时候成本高 | 入口先行，规范按需扩展 |
| 复制其他区域AGENTS.md但不更新内容 | 过时信息误导，比没有更糟 | AGENTS.md内容必须准确反映该区域实际情况 |
| 对称检查表只在首次创建时用，后续不管 | 增量变更破坏对称性 | 每次新增子模块或重大变更时重新检查 |
| 要求所有区域都有完整的.agents/规范体系 | 过度设计，简单区域承担不必要的维护负担 | 最小结构强制，完整规范按需 |

## 与三层路由协议的关系

本模式与三层路由协议是互补关系：
- **三层路由协议**定义了"路由如何工作"——数据驱动的判断流程、状态恢复、默认行为
- **对称目录结构**定义了"路由目标长什么样"——每个区域必须有可被路由到的入口

没有对称结构，三层路由就找不到目标；没有三层路由，对称结构只是孤立的文件。两者结合才能形成完整的可扩展路由体系。

## 验证来源

- **验证1：apps/区域补齐（2026-07-24）**：从无AGENTS.md的不对称状态，补齐为与projects/vendor对称的完整入口结构；包含215行AGENTS.md、87行.agents/README.md，验证了最小模板的充分性
- **验证2：vendor/projects历史实践**：vendor/（含flexloop嵌套）和projects/长期以来保持对称入口结构，智能体路由稳定，验证了对称结构的长期可维护性

## 关联资源

- 关联模式：[three-layer-routing-protocol.md](../../architecture-patterns/three-layer-routing-protocol.md)（三层路由协议）
- 关联模式：[entry-comparison-table.md](../document-architecture/entry-comparison-table.md)（入口对比表模式）
- 关联模式：[triple-entry-design.md](../../architecture-patterns/triple-entry-design.md)（三层入口设计）
- 关联模式：[bootstrap-driven-self-evolution.md](bootstrap-driven-self-evolution.md)（自举驱动自我演进）
- 验证来源：[retrospective-establish-four-region-routing-system-20260724](../../../reports/project-governance/documentation-governance/retrospective-establish-four-region-routing-system-20260724/README.md)（复盘报告）
