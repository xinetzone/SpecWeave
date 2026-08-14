---
id: "milestone-breakthrough-assetization-process"
title: "专项突破资产化标准流程"
category: "methodology-pattern"
date: "2026-08-01"
pattern_id: "MILESTONE-KNOWLEDGE-CLOOP-001"
maturity: "L1-experimental"
validation_count: 2
source: "SpecWeave知识沉淀规模化里程碑复盘（已验证：LLM Token优化、AI Agent Harness分析）"
tags: ["methodology", "process", "assetization", "knowledge-management", "milestone", "closed-loop"]
---

# 专项突破资产化标准流程

> 对应模式：MILESTONE-KNOWLEDGE-CLOOP-001 里程碑级知识沉淀闭环模式
> 
> **适用场景**：完成一个专项领域的深度研究/工程攻坚后，需要将零散经验转化为可复用组织资产时。
> 
> 本流程定义了专项突破后必须交付的4类资产，以及每类资产的验收标准，确保每次专项突破不是一次性消耗，而是成为组织能力的增量。

---

## 流程总览

```
专项突破完成
    ↓
[1] 知识库沉淀 → 结构化知识文档（人人可读）
    ↓
[2] 技能/命令封装 → 可执行工具（AI可用）
    ↓
[3] 角色定义更新 → 职责与边界清晰（协作可用）
    ↓
[4] 可复用模式萃取 → 跨领域迁移（未来可用）
    ↓
验收与归档
```

---

## 4类交付物标准与验收Checklist（共18项）

### 一、知识库沉淀（Knowledge Base）

**目标**：将专项知识结构化、文档化，成为人人可查阅的知识库。

| 检查项 | 验收标准 | 权重 |
|--------|----------|------|
| KB-001 | 有独立的知识库目录（如 `docs/knowledge/learning/<topic>/`），目录结构清晰 | 必须 |
| KB-002 | 有 README.md 作为入口，包含学习路径、核心内容索引、适用人群 | 必须 |
| KB-003 | 有独立的 glossary.md 术语表，核心术语≥15个，每个术语有通俗解释 | 必须 |
| KB-004 | 核心内容按认知阶梯分层：入门→进阶→高级→参考，符合学习规律 | 必须 |
| KB-005 | 有快速参考卡（quick-reference.md），3分钟可查核心要点 | 必须 |
| KB-006 | 有约束/禁令清单（constraints.md），明确哪些事绝对不能做 | 推荐 |
| KB-007 | 所有交叉引用链接有效，无断链 | 必须 |

**参考案例**：
- [LLM Token优化知识库](../../learning/llm-token-optimization/README.md)（29个文档，10个模块）

---

### 二、技能/命令封装（Skill/Command）

**目标**：将高频操作封装为可被AI Agent直接调用的Skill或命令，避免重复prompt。

| 检查项 | 验收标准 | 权重 |
|--------|----------|------|
| SK-001 | 有对应的Skill门面（`.agents/skills/<skill-name>-cmd/SKILL.md`） | 必须 |
| SK-002 | Skill包含：触发词、决策树、安全检查清单、Gotchas陷阱说明 | 必须 |
| SK-003 | 有对应的L2命令文档（`.agents/commands/<command>.md`）定义完整流程 | 必须 |
| SK-004 | 有可执行脚本支撑（如适用），脚本位于 `.agents/scripts/` 且有 `--help` | 推荐 |
| SK-005 | Skill在capability-registry.md中有索引，可被发现 | 必须 |

**参考案例**：
- seven-concepts-cmd 方法论编排Skill
- token-optimize-cmd Token优化Skill
- atomic-commit-cmd 原子提交Skill

---

### 三、角色定义更新（Role Definition）

**目标**：如果专项产生了新的专业分工，需要明确角色职责、能力边界、协作方式。

| 检查项 | 验收标准 | 权重 |
|--------|----------|------|
| RL-001 | 有独立的角色定义文件（`.agents/roles/<role-name>.md`） | 适用时必须 |
| RL-002 | 角色定义包含：Description、Responsibilities、Non-Goals三要素 | 必须 |
| RL-003 | Responsibilities使用短语形式，不超过15条；Non-Goals明确划清边界 | 必须 |
| RL-004 | 明确该角色需要查阅的知识库、技能、参考文档链接 | 必须 |
| RL-005 | 包含至少2个跨领域迁移验证案例，证明能力可泛化 | 必须 |
| RL-006 | 在capability-registry.md和协作场景文档中有对应索引 | 必须 |

**参考案例**：
- [Token Optimizer角色](../../../../../roles/token-optimizer.md)

> **说明**：不是每个专项都需要新角色。如果专项能力可以并入现有角色，只需更新现有角色定义即可，不需要强行创建新角色。

---

### 四、可复用模式萃取（Pattern Extraction）

**目标**：从专项经验中萃取可跨领域迁移的模式，沉淀到模式库。

| 检查项 | 验收标准 | 权重 |
|--------|----------|------|
| PT-001 | 萃取至少1个核心方法论模式（位于 `docs/retrospective/patterns/methodology-patterns/`） | 必须 |
| PT-002 | 模式文件使用TOML frontmatter，包含id、domain、layer、maturity、validation_count等字段 | 必须 |
| PT-003 | 模式包含：触发场景、核心步骤、反模式、迁移验证四个核心部分 | 必须 |
| PT-004 | **必须有非当前领域的迁移验证场景**：证明模式不是只对这次专项有效 | 必须 |
| PT-005 | 模式与知识库之间建立双向链接（KB引用模式，模式引用KB） | 必须 |
| PT-006 | 成熟度标注客观：validation_count=1时为L1，≥2为L2，≥1次复用为L3 | 必须 |

**参考案例**：
- WINDOWS-COMPAT-ZEROFRICTION-003 Windows零摩擦模式（迁移验证：跨浏览器兼容性）
- ENGINEERING-DEBUG-CLOOP-002 工程攻坚复盘模式（迁移验证：SRE故障处理）

---

## 验收流程

1. **自验收**：专项负责人按上述Checklist逐项打勾，必须项100%完成
2. **链接验证**：运行 `python .agents/scripts/check-links.py` 验证所有交叉引用有效
3. **格式验证**：运行 `python .agents/scripts/check-frontmatter.py` 验证frontmatter符合规范
4. **归档**：更新能力注册中心，确保所有资产可被发现

---

## 里程碑验收签字

| 资产类型 | 完成状态 | 验收人 | 验收日期 |
|----------|----------|--------|----------|
| 知识库沉淀 | [ ] | | |
| 技能/命令封装 | [ ] | | |
| 角色定义更新 | [ ] | | |
| 可复用模式萃取 | [ ] | | |

**整体验收结论**：[ ] 通过 [ ] 需整改

---

## 反模式警示

❌ **反模式1：只做研究不沉淀资产**——专项做完了就完事，知识只在参与者脑子里，下次遇到同类问题从零开始

❌ **反模式2：只有文档没有工具**——写了一堆文档，但高频操作没有封装成Skill/脚本，AI每次还是要重新理解prompt

❌ **反模式3：模式萃取没有跨领域验证**——把"这次怎么做的"直接当模式，没有验证在其他领域是否适用，沉淀的是无效模式

❌ **反模式4：资产孤岛**——新创建的文档/脚本/角色没有在注册中心索引，其他人（包括AI）找不到，等于没做

✅ **正确做法**：严格按照本流程的4类交付物执行，每类资产都验收通过后才算专项真正完成。
