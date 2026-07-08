---
title: "L0-L3 流程分级示例模板设计任务复盘"
source: "retrospective-l0l3-template-design-20260706"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/task-reports/retrospective-l0l3-template-design-20260706/README.toml"
analysis_date: "2026-07-06"
type: "task-retrospective"
tags: [l0-l3, process-tier, codex-philosophy, baby-codex, home-base, agi-pilled, template, retrospective]
---
# L0-L3 流程分级示例模板设计任务复盘

## 任务背景

本复盘对象为"基于 Codex 产品哲学三大概念设计 SpecWeave L0-L3 流程分级示例模板"任务（2026-07-06 完成）。该任务是 Codex 产品哲学文章深度洞察分析的直接下游产物——将分析报告 §9.5 提出的 L0-L3 流程分级提案 + §10.2 三大调适方向，落地为可复用的示例模板。

任务核心挑战：如何将三个抽象的产品哲学概念（baby Codex / home base / AGI-pilled）映射为具体的 4 级流程框架，同时保持与 SpecWeave 现有工作流体系（8步新功能/6步扩展/7步重构）的一致性。

## 复盘输入

| 输入项 | 路径 |
|---|---|
| 上游分析报告 | `../../insight-extraction/external-learning/retrospective-codex-article-analysis-20260706/analysis-report.md`（已归档，§9.5 L0-L3 提案 + §10.2 三大调适方向）|
| 现有工作流索引 | `.agents/workflows/README.md` |
| 现有功能开发流程 | `.agents/workflows/feature-development.md` |
| 阶段守卫规则 | `.agents/rules/stage-guardrails.md` |
| 变更类型判定 | `.agents/workflows/feature-development/01-change-type-overview.md` |
| 新功能 8 步流程 | `.agents/workflows/feature-development/02-new-feature-flow.md` |
| 上下文路由表 | `.agents/context-routing.md` |
| 模板索引 | `.agents/templates/README.md` |

## S1 事实收集

### 执行时间线

| 步骤 | 事件 | 结果 |
|---|---|---|
| S1.1 | 读取 AGENTS.md 启动协议 + 上下文路由表 | ✅ 确认任务类型为"模板设计"，无 vendor 资产命中，常规路由指向 `.agents/templates/` |
| S1.2 | 读取分析报告 §9.5 + §10.2 | ✅ 获取 L0-L3 四级流程提案和三大调适方向 |
| S1.3 | 读取 5 个现有工作流文件 | ✅ 理解 frontmatter 格式、Mermaid 风格、步骤级文档结构、导航链接约定 |
| S1.4 | 读取 templates/README.md | ✅ 确认模板索引结构和现有模板清单 |
| S1.5 | 设计并创建 `l0-l3-process-tier-template.md`（478 行） | ✅ 11 章 + 附录，4 级流程图、判定决策树、角色矩阵、AGI-pilled 检查清单、探针豁免规则 |
| S1.6 | 更新 `templates/README.md` 索引 | ✅ 添加新模板条目 |
| S1.7 | 运行链接检查 | ✅ 新模板链接全部有效；17 个断链均为其他既有模板的占位符 |
| S1.8 | 验证被引用文件存在 | ✅ 04-refactoring-flow.md、3 个模式文件均存在 |

### 产出物清单

| 文件 | 变更类型 | 大小 | 说明 |
|---|---|---|---|
| `.agents/templates/l0-l3-process-tier-template.md` | 新建 | 478 行 / 28KB | 主交付物：frontmatter + 11 章 + 附录 |
| `.agents/templates/README.md` | 修改 | +1 行 | 模板索引添加 L0-L3 条目 |

### 关键设计决策

| 决策点 | 选择 | 理由 |
|---|---|---|
| 存放位置 | `.agents/templates/` 而非 `.agents/workflows/` | 用户明确要求"示例模板"，模板目录更合适 |
| 文件结构 | 单文件而非多文件原子化 | 模板需要整体浏览，4 级流程在一个文件中便于对比 |
| L0 步骤数 | 3 步（假设定义→探针实现→结论归档） | 探索级应极简，重点是"可证伪假设"而非流程步骤 |
| L1 步骤数 | 4 步（共识边界→原型实现→共识审查→合并归档） | 共识级需要"媒介选择决策"作为关键差异点 |
| L2/L3 步骤 | 引用现有 8 步/7 步流程 | 避免重复定义，保持 DRY |
| 探针豁免机制 | `baby-` 前缀 + `.temp/baby/` 目录 + 30 天生命周期 | 显式标注解决"原型精致度与上线准备度脱钩"问题 |
| AGI-pilled 检查 | 4 项检查，≥2 项未通过降级到 L2 | 避免过度治理，形态-能力匹配判据的可操作化 |

### 关键数据

- 模板总行数：478 行
- Mermaid 流程图：6 个（1 个判定决策树 + 4 个层级流程图 + 1 个 L2 引用图）
- 步骤详情：L0 3 步 + L1 4 步 + L2/L3 引用 = 7 个详细步骤定义
- 检查清单：AGI-pilled 4 项 × 3-4 个检查点 = 14 个检查点
- 使用示例：4 个场景（L0/L1/L2/L3 各一）
- 角色参与矩阵：5 角色 × 4 层级 = 20 个单元格
- 探针豁免规则：6 项约束

## S2 过程分析

### 成功因素

| 因素 | 验证依据 | 说明 |
|---|---|---|
| 上游分析报告提供了清晰的 L0-L3 提案 | §9.5 已明确 4 级流程定义 | 设计无需从零构思，重点是落地而非抽象 |
| 设计前读取了 5 个现有工作流文件 | frontmatter 格式、Mermaid 风格、步骤结构均一致 | 确保模板与现有体系无缝衔接 |
| 三大概念到四级流程的映射清晰 | baby Codex→L0、home base→L1/L2、AGI-pilled→L3 | 每个概念都有对应的流程层级载体 |
| L2/L3 引用现有流程而非重复定义 | 模板中明确标注"详见 02/04 文档" | 避免 DRY 违规，降低维护成本 |
| 探针豁免机制设计具体可操作 | 6 项约束规则 + 运行时支持建议 | 不仅提出概念，还给出了落地路径 |

### 失败原因与可改进点

| 问题 | 原因 | 影响 | 改进方向 |
|---|---|---|---|
| 未创建 spec/tasks/checklist 三件套 | 任务从用户直接指令启动，未走 spec 流程 | 缺乏任务边界定义和验收标准 | 即使是模板设计任务，也应创建轻量 spec |
| 未使用 brainstorming skill 探索替代方案 | 直接进入设计，未探索"是否应该用多文件""是否应该放在 workflows/"等替代方案 | 可能存在更优设计未被发现 | 设计类任务前应先 brainstorming |
| 探针豁免规则未在运行时实现 | 设计了 `baby-` 前缀识别规则，但 `check-stage-guardrail-runtime.py` 尚未支持 | 模板的运行时支持缺失 | 作为行动项跟进 |
| L1 的媒介选择决策矩阵较粗 | 四维判定（受众×频率×认知×协作）但每维只有二元选项 | 决策粒度可能不够细 | 后续迭代中细化 |
| 未与现有 `elastic-workflow-classification.md` 模式对照 | 设计前未搜索模式库中的相关模式 | 可能与已有模式重复 | 复盘中对照（见 S3） |

### 流程瓶颈

1. **设计前缺少模式库扫描**：未先搜索 `docs/retrospective/patterns/` 中是否已有类似模式（如 `elastic-workflow-classification.md`、`governance-tier-priority.md`），可能导致重复设计
2. **运行时支持滞后于设计**：模板定义了探针豁免的运行时识别规则，但实际运行时脚本尚未实现，设计与实现存在时间差

## S3 洞察提炼（萃取四层漏斗）

### 第一层：去噪（可重复性检验）

**通过（≥2 场景验证）**：

| 洞察 | 验证场景 | 成熟度 |
|---|---|---|
| **概念映射驱动设计：将外部抽象概念映射到内部结构** | Codex 三概念→L0-L3 四级；之前 Codex 文章分析中五主题→十章节 | L2 验证（2 次） |
| **引用而非重复：新模板引用现有流程而非复制** | L2/L3 引用 02/04 文档；comprehensive-retrospective-template 也引用共享模式 | L3 稳定（多次验证） |

**待验证假设（仅 1 次观察）**：

| 洞察 | 观察 | 下一步 |
|---|---|---|
| **豁免机制合法化：通过显式标注创建合法例外通道** | `baby-` 前缀让探针代码合法化 | 下一次设计治理规则时验证是否适用 |
| **形态-能力匹配检查清单：用检查清单防止过度治理** | AGI-pilled 4 项检查 | 下一次 L3 流程启动时验证实用性 |
| **设计前模式库扫描可避免重复** | 本次未扫描，复盘中发现 `elastic-workflow-classification.md` 可能相关 | 下一次设计任务前执行扫描 |

**剔除（孤立个案）**：
- L1 的媒介选择四维判定（仅本次设计，未验证实用性）

### 第二层：结构化（分类）

| 分类 | 洞察 | 适用场景 |
|---|---|---|
| 设计方法论 | 概念映射驱动设计 | 将外部学习转化为内部结构时 |
| 文档架构 | 引用而非重复 | 新模板与现有体系有重叠时 |
| 治理策略 | 豁免机制合法化 | 需要为例外情况提供合法通道时 |
| 治理策略 | 形态-能力匹配检查 | 防止重型流程被过度应用于轻量任务 |
| 流程改进 | 设计前模式库扫描 | 所有设计类任务的前置步骤 |

### 第三层：标准化（可复用模式）

**模式 1：概念映射驱动设计**（成熟度 L2）

- **适用场景**：将外部学习（文章/竞品/演讲）的抽象概念映射到 SpecWeave 内部结构
- **执行流程**：
  1. 提取外部内容的核心概念（3-5 个）
  2. 为每个概念找到 SpecWeave 中的对应载体（流程层级/角色/资产类型）
  3. 建立"概念 × 载体"映射矩阵
  4. 验证映射的完整性（每个概念都有载体，每个载体都有概念）
  5. 在产出物中显式标注映射关系
- **优势**：确保外部学习不流失，每个抽象概念都有具体落地

**模式 2：豁免机制合法化**（成熟度 L1，待验证）

- **适用场景**：治理规则需要为例外情况提供合法通道时
- **设计要素**：
  1. 显式前缀标注（如 `baby-`、`experimental-`）
  2. 隔离存放位置（如 `.temp/baby/`）
  3. 生命周期限制（如 30 天）
  4. 主干隔离（不入主干、不进 CI）
  5. 审计追溯（关联假设卡片 ID）
  6. 运行时识别（脚本支持前缀识别）
- **待验证**：下一次设计治理规则时验证是否适用

**模式 3：形态-能力匹配检查清单**（成熟度 L1，待验证）

- **适用场景**：重型流程启动前防止过度治理
- **设计要素**：
  1. 复杂度匹配验证
  2. 必要性验证（每项治理措施是否真的需要）
  3. 替代方案验证（是否存在更轻量的方案）
  4. ROI 验证（增量成本是否对应增量价值）
  5. 降级规则（≥N 项未通过即降级）
- **待验证**：下一次 L3 流程启动时验证实用性

### 第四层：可操作化（执行指南）

**模板设计任务操作清单**：

```
1. 读取上游分析报告/学习材料，提取核心概念（3-5 个）
2. 搜索模式库（docs/retrospective/patterns/）是否已有相关模式  ← 本次新增
3. 读取现有相关文件（workflows/rules/templates），理解格式约定
4. 建立"概念 × 载体"映射矩阵
5. 设计模板结构（优先单文件，超 500 行考虑原子化）
6. 对每个载体编写详细内容（步骤/规则/检查清单）
7. 引用现有资产而非重复定义（DRY）
8. 更新索引文件（README.md）
9. 运行链接检查（python .agents/scripts/check-links.py --path <目录>）
10. 验证被引用文件存在
```

## S4 改进行动项

| ID | 优先级 | 行动项 | 验收标准 | 状态 |
|---|---|---|---|---|
| A1 | 高 | 在 `project_memory.md` 记录"设计前模式库扫描"约定 | 下次设计任务前执行模式库搜索 | ✅ 已完成（约定已写入 `project_memory.md`，含触发条件/扫描范围/关键词策略/扫描方法/决策规则/扫描记录/豁免条件 7 要素） |
| A2 | 中 | 对照 `elastic-workflow-classification.md` 模式，评估 L0-L3 模板是否与之重叠 | 评估文档创建，明确边界或合并建议 | ✅ 已完成（[评估文档](./a2-overlap-assessment.md)） |
| A3 | 中 | 实现 `check-stage-guardrail-runtime.py` 的 `baby-` 前缀识别 | 探针代码跨阶段操作不触发拦截 | ✅ 已完成（[实现说明](#a3-实现说明)） |
| A4 | 低 | 检查 L0-L3 模板与现有项目目录结构是否存在潜在冲突（用户重新定义，原"概念映射驱动设计沉淀"转为候选模式待评估） | 冲突评估文档创建，明确冲突清单与建议 | ✅ 已完成（[评估文档](./a4-directory-structure-conflict-assessment.md)） |
| A5 | 低 | 将"豁免机制合法化"沉淀为 L1 模式文档（待第二次验证后升级） | 下次设计治理规则时验证后决定 | ✅ 已完成（升级为 L2，[模式文档](../../../patterns/methodology-patterns/governance-strategy/exemption-mechanism-legalization.md)） |
| A6 | 低 | 细化 L1 媒介选择决策矩阵（当前四维二元，可扩展为多维多级） | 矩阵细化或纳入现有 `document-architecture` 模式 | 待评估 |

## 模式入库情况

### 本次复盘识别的 3 个候选模式

| 模式 | 成熟度 | 入库决策 | 理由 |
|---|---|---|---|
| 概念映射驱动设计 | L2（2 次验证） | ⏸ 暂缓入库 | 2 次验证均为本会话内任务，需跨会话验证后再入库 |
| 豁免机制合法化 | L2（4 次验证） | ✅ 已入库 | A5 行动项完成回溯性验证，发现 3 个已有应用场景（`.temp/` 目录机制、skip/rollback 审批、选择性归档豁免），共 4 次验证（1 前瞻性 + 3 回溯性），升级为 L2 并入库。[模式文档](../../../patterns/methodology-patterns/governance-strategy/exemption-mechanism-legalization.md) |
| 形态-能力匹配检查清单 | L1（1 次验证） | ⏸ 暂缓入库 | 仅 1 次验证，需 L3 流程实际启动时验证 |

**决策更新**：豁免机制合法化通过 A5 行动项完成回溯性验证，发现已有 3 个应用场景符合模式特征，共 4 次验证，升级为 L2 并入库。其余 2 个候选模式仍暂缓。

### 与现有模式的对照

| 现有模式 | 对照结果 |
|---|---|
| `elastic-workflow-classification.md` | ✅ A2 已评估：保持独立，L0-L3 是其扩展（新增 L0 层级），不合并 |
| `governance-tier-priority.md` | 与"阶段守卫分级应用"（§8.1）相关，L0-L3 的守卫强度分级可能与之重叠 |
| `learn-validate-adopt.md` | 已在模板中引用，是 L0-L3 升级路径的方法论基础 |
| `three-layer-rule-enforcement.md` | 与"治理规则映射"（§8）相关，L0-L3 的守卫强度分层与之平行 |
| `dual-zone-development-model.md` | A5 回溯性验证发现：`.temp/` 机制是豁免机制合法化与双区开发模型的共同应用案例 |

## 关键发现总结

```
[CMD-LOG] | level=INFO | cmd=retrospective | step=S3 | event=KEY_FINDING | session=retro-20260706-l0l3-template-design | msg=关键发现:概念映射驱动设计(L2,2次验证);豁免机制合法化(L1待验证);形态-能力匹配检查清单(L1待验证);设计前缺少模式库扫描(改进点)
```

```
[CMD-LOG] | level=INFO | cmd=retrospective | step=S3 | event=PATTERN_EXTRACTED | session=retro-20260706-l0l3-template-design | msg=模式萃取:概念映射驱动设计(L2暂缓入库)+豁免机制合法化(L1待验证)+形态-能力匹配检查清单(L1待验证);3个候选模式均因验证次数不足暂不入库
```

```
[CMD-LOG] | level=INFO | cmd=retrospective | step=S4 | event=ACTION_ITEM | session=retro-20260706-l0l3-template-design | msg=行动项:A1(高)模式库扫描约定入project_memory;A2(中)对照elastic-workflow-classification;A3(中)实现baby-前缀运行时识别;A4-A6(低)模式沉淀与矩阵细化待评估
```

```
[CMD-LOG] | level=INFO | cmd=retrospective | step=S4 | event=REPORT_GENERATED | session=retro-20260706-l0l3-template-design | msg=复盘报告已生成:docs/retrospective/reports/task-reports/retrospective-l0l3-template-design-20260706/README.md
```

## S5 归档沉淀

- ✅ 复盘报告归档至 `docs/retrospective/reports/task-reports/retrospective-l0l3-template-design-20260706/README.md`
- ✅ 关键约定已更新至 `project_memory.md`（A1：设计前模式库扫描约定，含触发条件/扫描范围/关键词策略/扫描方法/决策规则/扫描记录/豁免条件 7 要素）
- ⏸ 模式入库：3 个候选模式暂缓入库（验证次数不足）
- ⏸ 索引更新：task-reports 索引待同步

## A3 实现说明：baby- 前缀运行时识别

A3 行动项已于 2026-07-06 完成。在 `check-stage-guardrail-runtime.py` 的核心运行时模块中实现了 L0 探索级探针代码的豁免机制。

### 修改文件清单

| 文件 | 变更类型 | 说明 |
|---|---|---|
| `lib/stage_guardrails/boundary.py` | 新增函数 | `is_baby_code(file_path)` 识别函数，规则：文件名以 `baby-` 开头 OR 路径包含 `.temp/baby/`（跨平台路径分隔符） |
| `lib/stage_guardrails/interceptor.py` | 修改方法 | `format_boundary_check` 和 `format_boundary_pass` 添加 `baby_code` 参数，为 True 时在 ctx 中标记 `baby_code: true` |
| `lib/stage_guardrails/runtime.py` | 修改方法 | `guard_operation` 添加 `baby_code` 和 `file_path` 参数；探针代码跳过 `BoundaryChecker.check()` 直接放行 |
| `lib/stage_guardrails/__init__.py` | 导出 | 导出 `is_baby_code` 函数 |
| `tests/test_stage_guardrails_runtime.py` | 新增测试 | `TestIsBabyCode`（11 项）+ `TestBabyCodeExemption`（11 项） |

### 核心 API

```python
from lib.stage_guardrails import GuardrailRuntime, OperationType

rt = GuardrailRuntime(session_id='task-001')
rt.enter_stage('S1', 'orchestrator', '探索侧边栏群聊可行性')

# 方式一：显式声明 baby_code=True
out = rt.guard_operation(OperationType.WRITE_CODE, 'orchestrator',
                         detail='探针实现', baby_code=True)
# out.is_intercept == False，SG-LOG 含 baby_code: true

# 方式二：通过 file_path 自动识别
out = rt.guard_operation(OperationType.WRITE_CODE, 'orchestrator',
                         detail='探针实现',
                         file_path='baby-sidebar-chat-probe.tsx')
# out.is_intercept == False，自动识别 baby- 前缀

# 方式三：通过 .temp/baby/ 路径自动识别
out = rt.guard_operation(OperationType.WRITE_CODE, 'orchestrator',
                         detail='探针实现',
                         file_path='.temp/baby/auth-test.py')
# out.is_intercept == False，自动识别 .temp/baby/ 路径
```

### 识别规则（来自 l0-l3-process-tier-template.md §8.3）

1. 文件名（basename）以 `baby-` 开头 → 标记为探针
2. 文件路径包含 `.temp/baby/` 片段（跨平台路径分隔符 `\` 和 `/`）→ 标记为探针
3. SG-LOG 中探针操作的 `BOUNDARY_CHECK` 和 `BOUNDARY_PASS` 日志 ctx 包含 `baby_code: true` 字段

### 测试结果

- 新增 22 项测试全部通过（`TestIsBabyCode` 11 项 + `TestBabyCodeExemption` 11 项）
- 原有 49 项测试无回归
- 相关模块（boundary/interceptor/state）156 项测试无回归
- 探针豁免不增加 `interception_count`，不触发 `BypassDetector`

## 关联资源

- [复盘对象模板](../../../../../.agents/templates/l0-l3-process-tier-template.md)
- [上游分析报告（已归档）](../../insight-extraction/external-learning/retrospective-codex-article-analysis-20260706/analysis-report.md)
- [上游任务复盘](../retrospective-codex-article-analysis-20260706/README.md)
- [retrospective-cmd Skill](../../../../../.agents/skills/retrospective-cmd/SKILL.md)
- [萃取四层漏斗模型](../../../patterns/methodology-patterns/retrospective-knowledge/extraction-four-layer-funnel.md)
- [已评估的现有模式：弹性工作流分类](../../../patterns/methodology-patterns/governance-strategy/elastic-workflow-classification.md)（[A2 评估报告](./a2-overlap-assessment.md)）
