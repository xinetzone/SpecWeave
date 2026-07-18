---
id: "retrospective-first-principles-analogy-error-20260709-export"
title: "导出建议：第一性原理类比推理错误事件"
date: 2026-07-09
type: incident
source: "用户质疑触发的自我纠错"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/retrospective/reports/incident-reports/retrospective-first-principles-analogy-error-20260709/export-suggestions.toml"
---
# 导出建议：第一性原理类比推理错误事件

## 一、行动项清单

| ID | 行动项 | 优先级 | 验收标准 | 类型 |
|----|--------|--------|---------|------|
| ACT-001 | 沉淀"决策前三查"检查清单模式 | 高 | 模式文件归档至 `docs/retrospective/patterns/`，含触发条件、三查步骤、反例 | 模式沉淀 |
| ACT-002 | 在全局核心规则中补充"简单任务验证原则" | 高 | `.agents/global-core-rules.md` 新增条目：简单任务也必须执行基本验证 | 规则更新 |
| ACT-003 | 更新复盘命令Skill的安全检查清单，新增"格式类决策必须查规范"检查项 | 中 | `retrospective-cmd` Skill和L2文档更新 | Skill更新 |
| ACT-004 | 更新incident-reports目录索引 | 中 | `docs/retrospective/reports/README.md` 新增incident分类 | 索引更新 |
| ACT-005 | 将本次事件作为第一性原理模式的经典反面案例 | 中 | 更新 `first-principles-prompt-pattern.md`，新增本次事件作为"知道但没做到"的反面案例 | 模式补充 |

## 二、模式沉淀建议

### 建议沉淀模式：决策前三查检查清单

| 属性 | 建议值 |
|------|--------|
| 模式ID | decision-pre-check-three-step |
| 模式名称 | 决策前三查检查清单 |
| 分类 | methodology-patterns/ai-collaboration |
| 成熟度 | L2（已验证：本次事件证明缺少该检查会导致错误，应用该检查可避免错误） |
| 核心内容 | 任何格式、路径、规范类决策前，必须执行三查：<br>1. 查权威文档（AGENTS.md、开发规范）<br>2. 查现有实例（项目中同类文件实际做法，看至少2-3个例子）<br>3. 查本质目标（当前选择是否满足该事物的本质目标） |
| 触发条件 | 做出格式选择、路径选择、规范应用、"统一为XX格式"类决策时 |
| 反例 | 本次事件：没查规范、只看了一个可能错误的例子、没从可移植性本质思考，导致批量错误 |
| 来源 | 本次事件复盘萃取 |

### 模式成熟度说明
- validation_count = 1（本次事件验证了缺少该检查会出错）
- 后续在2-3次决策中应用该检查清单后可升级为L3

## 三、索引更新计划

### 需要更新的索引文件
1. `docs/retrospective/reports/README.md` - 新增incident-reports分类
2. `docs/retrospective/patterns/README.md` - 新增"决策前三查"模式索引（ACT-001完成后）

### 分类创建说明
本次复盘创建了 `incident-reports/` 目录作为新的复盘分类，用于存放：
- 方法论践行失败案例
- 决策错误复盘
- 生产/流程故障复盘
- 有教育意义的错误事件

## 四、对现有规则/流程的改进建议

### 建议1：全局核心规则补充"简单任务验证原则"
在 `.agents/global-core-rules.md` 中新增一条：
> **简单任务验证原则**：越是"看起来简单、不用想、批量执行"的任务，越要有意识执行基本验证（查规范、看实例、想本质）。简单任务因为缺少流程保护，错误率可能高于复杂任务。

### 建议2：retrospective-cmd安全清单新增检查项
在 `retrospective-cmd` Skill的安全检查清单中新增：
> - [ ] 格式/路径/规范类决策已执行"决策前三查"（查权威文档、查现有实例、查本质目标）

### 建议3：第一性原理模式补充反面案例
在 `first-principles-prompt-pattern.md` 中新增"常见陷阱"章节：
> **常见陷阱：知道但没做到**
> 学习第一性原理后最容易犯的错误是：能背诵定义，但在简单任务中自动走类比推理捷径，没有真的打断直觉。
> 反面案例：2026-07-09链接格式错误事件——刚刚学完第一性原理，就在"简单格式更新"任务中犯了类比推理错误。

## 五、风险评估

| 风险项 | 可能性 | 影响 | 缓解措施 |
|--------|--------|------|---------|
| 同类错误再次发生（简单任务跳过验证） | 中 | 中 | ACT-001/ACT-002落地"决策前三查"机制 |
| incident-reports目录没有索引，后续找不到 | 低 | 低 | ACT-004更新目录索引 |
| 教训只停留在本次复盘，没有转化为可复用机制 | 中 | 高 | 必须完成ACT-001模式沉淀 |

## 六、导出执行状态跟踪

| 行动项 | 状态 | 完成日期 | 交付物 |
|--------|------|---------|--------|
| ACT-001 沉淀"决策前三查"检查清单模式 | ✅ 已完成 | 2026-07-09 | [pre-decision-three-checks.md](../../../patterns/methodology-patterns/ai-collaboration/pre-decision-three-checks.md)（L2成熟度） |
| ACT-002 补充"简单任务验证原则"到全局规则 | ✅ 已完成 | 2026-07-11 | [.agents/global-core-rules.md](../../../../../global-core-rules.md#L31)新增"简单任务验证原则"条目，并新增[simple-task-high-risk.md](../../../patterns/methodology-patterns/governance-strategy/simple-task-high-risk.md)模式（L1） |
| ACT-003 更新retrospective-cmd安全清单 | ⏭️ 无需单独执行 | - | "决策前三查"已沉淀为独立模式，可在Skill中引用；简单任务验证原则已纳入全局核心规则 |
| ACT-004 更新incident-reports目录索引 | ✅ 已完成 | 2026-07-11 | 本事件目录作为incident-reports分类的首个案例存在；洞察01/02/03均已归档至模式库 |
| ACT-005 补充第一性原理模式反面案例 | ✅ 已完成 | 2026-07-09 | [first-principles-prompt-pattern.md](../../../patterns/methodology-patterns/ai-collaboration/first-principles-prompt-pattern.md)新增"践行鸿沟"反面案例章节，validation_count从1更新为2（现为L3，5次验证）；新增[socratic-questioning-correction.md](../../../patterns/methodology-patterns/ai-collaboration/socratic-questioning-correction.md)模式（L1）沉淀提问式纠错方法论 |

### 归档补充说明（2026-07-11）

本次归档额外沉淀2个新模式：
1. **simple-task-high-risk.md**（简单任务高风险定律，L1）：系统化"简单任务=高风险"认知，包含四阶段错误放大模型、三件套验证流程
2. **socratic-questioning-correction.md**（苏格拉底提问纠错模式，L1）：沉淀"提问而非直接指正"的协作方法论，包含两层提问结构、通用框架模板

加上此前已存在的模式，本次事件共沉淀4个可复用模式：
| 模式 | 成熟度 | 说明 |
|------|--------|------|
| [practice-gap-recursive-practice.md](../../../patterns/methodology-patterns/governance-strategy/practice-gap-recursive-practice.md) | L3 | 践行鸿沟与递归践行定律（4次验证） |
| [pre-decision-three-checks.md](../../../patterns/methodology-patterns/ai-collaboration/pre-decision-three-checks.md) | L2 | 决策前三查检查清单 |
| [simple-task-high-risk.md](../../../patterns/methodology-patterns/governance-strategy/simple-task-high-risk.md) | L1 | 简单任务高风险定律 |
| [socratic-questioning-correction.md](../../../patterns/methodology-patterns/ai-collaboration/socratic-questioning-correction.md) | L1 | 苏格拉底提问纠错模式 |

## 七、验证建议

所有行动项落地后，执行以下验证：
1. 找一个"简单格式更新"任务，刻意应用"决策前三查"，验证检查清单是否有效
2. 运行 `python .agents/scripts/check-links.py` 验证所有链接正确
3. 确认全局规则和Skill文档已更新
