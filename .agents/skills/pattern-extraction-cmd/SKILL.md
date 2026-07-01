---
name: pattern-extraction-cmd
version: 1.1.0
description: "当用户提到'模式沉淀'、'萃取模式'、'模式入库'、'沉淀为模式'、'pattern extraction'、'可复用模式'、'更新模式库'、'生成模式文档'时，必须使用此技能。提供从复盘/洞察中萃取可复用模式的标准化流程：模式识别→分类定位→标准文档生成→索引更新→质量验证，附带决策路径CMD-LOG日志支持问题回溯。不要手动编写模式文档——本Skill封装了frontmatter规范、目录分类规则、质量检查标准和成熟度管理。"
argument-hint: "<来源：insight/retrospective/experience> [模式名称]"
user-invocable: true
paths:
  - ".agents/skills/pattern-extraction-cmd/SKILL.md"
  - "docs/retrospective/patterns/"
  - ".agents/scripts/pattern-maturity.py"
  - ".agents/scripts/check-pattern-quality.py"
  - ".agents/rules/cmd-log-specification.md"
---

# Pattern Extraction 模式萃取命令 Skill

> ⚠️ **本Skill是命令入口门面（L1索引层）**，遵循[渐进式披露三层架构](../../capabilities/ARCHITECTURE.md)：
> - L0：[.agents/ONBOARDING.md](../../ONBOARDING.md)（入口速查）
> - L1：本文件（<500行，触发词+决策树+核心步骤+安全清单）
> - L2：本文件第5-9节（完整流程）+ [pattern-maturity.py](../../../.agents/scripts/pattern-maturity.py)（成熟度管理脚本）

## 1. Skill ID
`pattern-extraction-cmd`

## 2. 功能描述

提供从洞察/复盘中标准化萃取可复用模式的能力，完成"识别→分类→生成→入库→验证"闭环：

| 方案 | 推荐场景 | 优势 |
|------|---------|------|
| **全新模式创建** | ⭐ 从洞察/经验中提炼新模式 | 标准frontmatter+完整结构，符合分类规范 |
| **现有模式更新** | ⭐ 模式被验证/复用后更新成熟度 | 自动更新validation_count/reuse_count/maturity字段 |
| **模式合并/重构** | ⭐ 多个相似模式需要合并或拆分 | 遵循模式合并边界判断标准 |

核心功能：识别可复用模式→判断分类归属→生成标准TOML frontmatter→生成模式文档结构→更新索引README→运行质量检查→更新成熟度统计。

> **为什么用本Skill而非手动写模式文档？** 手动写模式容易遗漏frontmatter必填字段、放错分类目录、忘记更新索引、不遵循正反例结构要求；本Skill封装了184个模式沉淀的最佳实践和3个自动化脚本（pattern-maturity.py/check-pattern-quality.py/pattern-maturity-stats.py），确保模式质量可预测。

## 3. 何时使用本技能

当用户提到以下任何内容时触发：
- "模式沉淀"、"萃取模式"、"模式入库"、"沉淀为模式"
- "可复用模式"、"生成模式文档"、"更新模式库"
- "pattern extraction"、"pattern 沉淀"
- 复盘/洞察完成后，用户说"把这个经验沉淀下来"、"这个可以做成模式"
- 需要更新模式成熟度、validation_count、reuse_count

> **关于触发**：即使没有明确说"用模式萃取命令"，只要涉及从经验/洞察/复盘中提炼可复用知识并入库到docs/retrospective/patterns/，就应该使用本Skill。模式沉淀是知识复利的核心环节——"产出价值=基础×抽象层级^复用次数"，不要跳过。

## 4. 方案选择决策树

```
需要沉淀模式？
├─ 从新洞察/经验提炼全新模式？ → 全新模式创建（第5节）
│  ├─ 架构相关？ → architecture-patterns/
│  ├─ 具体代码技巧？ → code-patterns/
│  └─ 方法论/流程/AI协作？ → methodology-patterns/<子主题>/
├─ 模式被成功应用/复用需要更新成熟度？ → 现有模式更新（第6节）
├─ 多个模式相似需要合并/拆分？ → 模式合并/重构（第7节）
└─ 只是想查找/阅读已有模式？ → 直接查阅 docs/retrospective/patterns/ 对应目录README
```

**与其他Skill的关系**：
- 复盘流程S5步骤使用本Skill沉淀模式
- 洞察萃取完成后使用本Skill入库
- 模式文档过大时使用 `atomization-cmd` 拆分
- 沉淀完成后使用 `docgen-cmd` 更新导航索引

### ⚠️ 强制：触发时必须记录输入参数日志

每次本Skill被触发、进入决策树**之前**，必须输出一条CMD-LOG日志记录完整输入参数，方便后续排查逻辑分支选择问题：

```
[CMD-LOG] | level=INFO | cmd=pattern-extraction | step=S0 | event=CMD_START | session=<SESSION_ID> | msg=开始模式萃取：<操作简述> | ctx={"trigger_phrase":"<用户触发短语>","operation_type":"<create|update|merge|query>","source":"<来源文件/对话>","pattern_name":"<模式名称>","user_explicit":<true|false>,"dry_run":<true|false>,"auto_classify":<true|false>}
```

**ctx字段必填说明**（第9节执行日志有完整规范）：
- `trigger_phrase`：用户触发时的原始短语（如"把这个洞察沉淀成模式"）
- `operation_type`：决策树选择的操作类型（create=新建/update=更新/merge=合并/query=查询）
- `source`：来源文件路径或对话上下文标识
- `pattern_name`：用户指定的模式名称（可空）
- `user_explicit`：用户是否明确指定了操作类型（true=用户说"新建模式"/false=自动判断）
- `dry_run`：是否为预览模式
- `auto_classify`：是否自动分类目录（true=自动判断/false=用户指定）

> **为什么必须在决策前记录参数？** 模式萃取涉及多层分类决策（架构/代码/方法论→子主题→成熟度初始值），如果后续发现分类错误或选错了操作类型，没有触发时的输入参数日志就无法回溯"当时为什么选了这个分支"。CMD_START日志在决策前输出，记录原始输入，是排查分支逻辑问题的关键证据。

## 5. 核心步骤（快速开始）

```
步骤1：识别模式——确认是否满足可复用条件
   可复用三标准：
   □ 可命名：有清晰的问题场景和解决方案名称
   □ 可复现：在≥1个场景中成功验证
   □ 可迁移：核心机制不依赖特定上下文细节
步骤2：分类定位——确定归属目录
   □ 架构层 → architecture-patterns/
   □ 代码层 → code-patterns/
   □ 方法论层 → methodology-patterns/<子主题>/（7个子主题见L2）
步骤3：生成模式文档
   □ TOML frontmatter（id/domain/layer/maturity/validation_count等必填字段）
   □ 标准内容结构（问题→解决方案→适用场景→实际案例→反模式→相关模式）
步骤4：更新索引
   □ 更新对应目录的README.md，添加模式条目和一句话说明
   □ 更新CATEGORIES.md（如为方法论模式）
步骤5：质量验证
   □ 运行 python .agents/scripts/check-pattern-quality.py <模式文件>
   □ 运行 python .agents/scripts/pattern-maturity.py check-index --fix 更新统计
步骤6：向用户展示生成的模式文档，获得确认
```

> 完整的分类决策树、frontmatter字段说明、正反例写作要求见本文第6-8节；模式分类边界详见 [CATEGORIES.md](../../../docs/retrospective/patterns/methodology-patterns/CATEGORIES.md)。

> **为什么必须先判断"可复用三标准"再创建模式？** 模式库的价值取决于信噪比——把一次性的特定解决方案沉淀为模式会稀释模式库质量，增加检索成本。只有同时满足"可命名+可复现+可迁移"三个条件的经验才值得沉淀，否则留在复盘报告中即可。这是从184个模式沉淀中总结出的关键质量门。

## 6. 方案一：全新模式创建（推荐）

### 6.1 模式文档标准结构

```markdown
+++
id = "<kebab-case-id>"
domain = "architecture|code|methodology"
layer = "architecture|code|methodology"
maturity = "L1"  # 新创建的模式默认L1
validation_count = 1
reuse_count = 0
documentation_level = "basic"
source = "<来源文件相对路径>"

[bindings]
rules = []
references = []
skills = []
related_patterns = []
+++

# <模式名称>：<一句话核心说明>

## 模式概述
<用2-3句话说明这个模式解决什么问题、核心机制是什么>

## 问题现象
<描述这个模式解决的具体问题场景和痛点>

## 解决方案
<详细说明核心机制、关键步骤、决策逻辑>
<推荐使用表格对比、Mermaid流程图、代码示例等>

## 适用场景
<列出哪些情况应该使用这个模式>

## 实际案例
<至少1个本项目中的真实应用案例，说明如何应用、效果如何>

## 反模式
<列出1-3个常见的错误做法，说明为什么不对>

## 与其他模式的关系
<列出相关的模式，说明是前置/互补/被细化等关系>

## 边界与选型
<说明这个模式的适用边界，什么情况下不应该用，什么情况下用其他模式>
```

> **为什么需要"反模式"章节？** 只知道"怎么做正确"不足以覆盖边界场景——知道"怎么做错误"能帮助Agent在模糊情况下做出正确判断，避免把模式用在不适用的地方。每个高质量模式（L2及以上）至少应包含1个反模式。

### 6.2 目录分类速查

| 层级 | 目录 | 子主题 |
|------|------|--------|
| 架构层 | architecture-patterns/ | - |
| 代码层 | code-patterns/ | - |
| 方法论层 | methodology-patterns/ | retrospective-knowledge（复盘知识）/ document-architecture（文档架构）/ tools-automation（工具自动化）/ governance-strategy（治理策略）/ ai-collaboration（AI协作）/ creative-design（创意设计）/ product-growth（产品增长） |

> 完整的子主题边界说明见 [CATEGORIES.md](../../../docs/retrospective/patterns/methodology-patterns/CATEGORIES.md)。

## 7. 方案二：现有模式更新

当模式被成功应用或复用时，更新frontmatter字段：

```bash
cd d:\spaces\SpecWeave

# 验证模式被成功应用后
python .agents/scripts/pattern-maturity.py validate <模式文件路径>

# 模式被其他任务复用后
python .agents/scripts/pattern-maturity.py reuse <模式文件路径>

# 检查并更新索引统计
python .agents/scripts/pattern-maturity.py check-index --fix
```

成熟度升级条件：
- L1→L2：validation_count ≥ 2（至少2次成功验证）
- L2→L3：reuse_count ≥ 1 且 validation_count ≥ 2（已被非原作者复用）
- L3→L4：已集成至CI/工具链自动化验证

> **为什么validation_count和reuse_count要分开计数？** "自己用了两次"和"别人复用了一次"的可信度完全不同。reuse_count是模式通用性的强信号——非原作者能成功复用说明模式的抽象层级合适、文档足够清晰，这是L3（可复用）的核心判断标准。

## 8. 方案三：模式合并/重构

遵循 [pattern-merge-boundary.md](../../../docs/retrospective/patterns/methodology-patterns/document-architecture/pattern-merge-boundary.md) 的三维重叠度判断：

```
两个模式是否需要合并？
├─ 场景重叠度 >70% AND 机制重叠度 >70% AND 建议重叠度 >70% → 合并
├─ 三维重叠度均 <30% → 独立创建
└─ 30%-70%重叠 → 独立判断，考虑引用关联而非合并
```

合并后保留更成熟的模式id，将另一个的内容整合进来，更新related_patterns，删除被合并的文件并在索引中标记。

## 9. 执行日志（CMD-LOG）

遵循项目 [CMD-LOG命令集执行日志规范](../../rules/cmd-log-specification.md)，使用统一前缀+键值对+JSON上下文格式。

### 9.1 基本标识

| 字段 | 值 |
|------|-----|
| cmd标识 | `pattern-extraction` |
| Session前缀 | `ptrn-` |
| Session格式 | `ptrn-YYYYMMDD-<pattern-name>` |
| 步骤数 | 6步（S0-S5） |

### 9.2 步骤编号

| 步骤 | 名称 | 对应核心步骤 |
|------|------|-------------|
| S0 | 启动与参数记录 | 第4节强制触发日志（决策前） |
| S1 | 模式识别与分类 | 步骤1-2（三标准判断+目录定位） |
| S2 | 方案决策 | 决策树分支选择（create/update/merge） |
| S3 | 文档生成/更新 | 步骤3-4（frontmatter+标准结构） |
| S4 | 质量验证 | 步骤5（check-pattern-quality.py） |
| S5 | 索引更新与归档 | 步骤6（README/CATEGORIES更新+maturity统计） |

### 9.3 特有事件定义

| 时机 | level | event | msg模板 | ctx必填字段 |
|------|-------|-------|---------|------------|
| 触发参数记录（S0，决策前强制） | INFO | `CMD_START` | 开始模式萃取：\<操作简述\> | trigger_phrase, operation_type, source, pattern_name, user_explicit, dry_run, auto_classify |
| 三标准检查不通过 | WARN | `REUSABILITY_FAIL` | 模式可复用性检查未通过：\<原因\> | failed_criteria（命名/复现/迁移）, pattern_name |
| 目录分类自动判断 | DEBUG | `CLASSIFY_AUTO` | 自动分类目录：\<路径\>，置信度：\<high/med/low\> | target_dir, confidence, classification_basis |
| 决策树分支选择 | INFO | `BRANCH_SELECTED` | 决策分支：\<create/update/merge\>，依据：\<判断依据\> | operation_type, decision_basis, similarity_score（merge时） |
| frontmatter生成 | DEBUG | `FRONTMATTER_READY` | frontmatter已生成：id=\<id\>, maturity=\<L1/L2\>, domain=\<domain\> | pattern_id, maturity, domain, layer, has_source |
| 发现重复模式 | WARN | `DUPLICATE_FOUND` | 发现疑似重复模式：\<现有模式id\>，相似度：\<分数\> | existing_id, similarity_score, overlap_analysis |
| 模式质量检查通过 | INFO | `QUALITY_PASS` | 模式质量检查通过：\<模式id\>，得分：\<分数\> | pattern_id, quality_score, checks_passed |
| 模式质量检查失败 | ERROR | `QUALITY_FAIL` | 模式质量检查失败：\<错误数\>个错误 | pattern_id, error_count, error_details |
| 索引更新完成 | INFO | `INDEX_UPDATED` | 模式索引更新完成：\<目录路径\> | index_path, new_patterns_count |
| 成熟度更新 | DEBUG | `MATURITY_UPDATED` | 模式成熟度更新：\<id\> validation=\<N\> reuse=\<M\> → maturity=\<Lx\> | pattern_id, validation_count, reuse_count, maturity |

### 9.4 关键日志示例

```
[CMD-LOG] | level=INFO | cmd=pattern-extraction | step=S0 | event=CMD_START | session=ptrn-20260701-markdown-as-interface | msg=开始模式萃取：从insight-b-markdown-as-interface创建新模式 | ctx={"trigger_phrase":"把这个洞察沉淀成模式","operation_type":"create","source":"insight-b-markdown-as-interface.md","pattern_name":"markdown-as-interface","user_explicit":false,"dry_run":false,"auto_classify":true}
[CMD-LOG] | level=DEBUG | cmd=pattern-extraction | step=S1 | event=CLASSIFY_AUTO | session=ptrn-20260701-markdown-as-interface | msg=自动分类目录：methodology-patterns/ai-collaboration，置信度：high | ctx={"target_dir":"methodology-patterns/ai-collaboration","confidence":"high","classification_basis":"涉及Agent接口/五要素模型，属AI协作方法论"}
[CMD-LOG] | level=INFO | cmd=pattern-extraction | step=S2 | event=BRANCH_SELECTED | session=ptrn-20260701-markdown-as-interface | msg=决策分支：create，依据：无同名/相似模式，满足三标准 | ctx={"operation_type":"create","decision_basis":"三标准通过，无重复","similarity_score":null}
[CMD-LOG] | level=INFO | cmd=pattern-extraction | step=S5 | event=CMD_COMPLETE | session=ptrn-20260701-markdown-as-interface | msg=模式萃取完成：markdown-as-interface（L1），总耗时：约15分钟 | ctx={"duration":"~15m","pattern_id":"markdown-as-interface","maturity":"L1","quality_score":100}
```

### 9.5 决策分支排查示例

当发现分类错误或分支选错时，可通过以下命令快速定位问题：

```powershell
# 查看某次模式萃取的完整决策路径
Select-String -Path ".agents/logs/cmd-*.log" -Pattern "ptrn-20260701-<pattern-name>" | Select-Object -Property Line

# 查看所有模式分类决策（排查目录归类问题）
Select-String -Path ".agents/logs/cmd-*.log" -Pattern "CLASSIFY_AUTO|BRANCH_SELECTED" | Select-Object -Property Line
```

## 10. 安全检查清单（模式质量门）

模式入库前必须逐项确认：

- [ ] **可复用三标准已满足**：可命名+可复现+可迁移，不是一次性特定方案
- [ ] **分类目录正确**：已判断是架构/代码/方法论层，子主题归属准确
- [ ] **frontmatter字段完整**：id/domain/layer/maturity/validation_count/reuse_count/documentation_level/source均已填写
- [ ] **source字段已标注**：指向来源洞察/复盘文件的相对路径（溯源要求）
- [ ] **标准结构完整**：包含问题/解决方案/案例/反模式/边界章节
- [ ] **至少1个实际案例**：不是纯理论，有本项目真实应用场景
- [ ] **文件路径使用相对路径**：禁止file:///绝对路径
- [ ] **索引已更新**：对应目录README.md和CATEGORIES.md（如适用）已添加条目
- [ ] **质量检查已通过**：check-pattern-quality.py 无错误
- [ ] **成熟度统计已更新**：pattern-maturity.py check-index --fix 已运行
- [ ] **模式文档控制在合理长度**：单模式文档建议<300行，复杂内容拆分L2引用
- [ ] **命名符合kebab-case**：文件名和frontmatter id使用kebab-case格式

## 11. 常见错误处理

| 问题场景 | 处理方式 |
|---------|---------|
| 不确定应该归到哪个分类 | 先看CATEGORIES.md的核心关注点和边界说明，仍不确定时放到governance-strategy/并标注"待分类" |
| 类似模式已存在 | 使用模式合并判断标准，考虑更新现有模式而非新建 |
| 模式太抽象没有具体案例 | 停留在洞察层面，不要强行沉淀为模式；等有第二个验证案例再创建 |
| frontmatter字段校验失败 | 运行check-pattern-quality.py查看具体错误，按提示补全字段 |
| 索引更新冲突 | 先运行check-index --fix自动修复，仍有冲突时手动检查README.md |

## 12. 关键参考速查表

| 参考 | 层级 | 路径 | 何时查阅 |
|------|------|------|---------|
| 模式文档标准结构（frontmatter/章节/案例） | L1 | [第6.1节](#61-模式文档标准结构) | 创建新模式时 |
| 模式库总索引与成熟度标准 | L2 | [patterns/README.md](../../../docs/retrospective/patterns/README.md) | 了解成熟度定义和统计 |
| 方法论模式7个子主题分类边界 | L2 | [CATEGORIES.md](../../../docs/retrospective/patterns/methodology-patterns/CATEGORIES.md) | 判断方法论模式归属时 |
| 模式合并边界判断标准 | L2 | [pattern-merge-boundary.md](../../../docs/retrospective/patterns/methodology-patterns/document-architecture/pattern-merge-boundary.md) | 合并/拆分模式时 |
| 洞察萃取漏斗 | L2 | [extraction-four-layer-funnel.md](../../../docs/retrospective/patterns/methodology-patterns/retrospective-knowledge/extraction-four-layer-funnel.md) | 从洞察萃取模式时 |
| 质量检查脚本 | L2 | [check-pattern-quality.py](../../../.agents/scripts/check-pattern-quality.py) | 验证模式格式 |
| 成熟度管理脚本 | L2 | [pattern-maturity.py](../../../.agents/scripts/pattern-maturity.py) | 更新validation_count/reuse_count |

## 13. Changelog

- **v1.1.0** (2026-07-01): 添加CMD-LOG执行日志规范。在决策树前强制记录触发输入参数（trigger_phrase/operation_type/source等7个字段），方便后续排查逻辑分支选择问题；新增9个特有事件定义（CMD_START/BRANCH_SELECTED/CLASSIFY_AUTO等），支持决策路径回溯。
- **v1.0.0** (2026-07-01): 初始版本。基于markdown-as-interface五要素模型，封装模式沉淀标准化流程，整合3个现有自动化脚本。
