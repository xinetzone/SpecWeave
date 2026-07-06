---
id: "meta-atomization-bisect-overview"
source: "docs/retrospective/reports/project-governance/comprehensive-reviews/retrospective-full-lifecycle-report-atomization-20260705/insight-extraction.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/document-architecture/meta-atomization-bisect-overview.toml"
maturity: "L2"
validation_count: 5
reuse_count: 4
documentation_level: "operation-guide"
related_patterns:
  - "large-document-atomization-method"
  - "entry-container-separation"
  - "atomization-three-criteria-test"
  - "atomization-three-tier-classification"
  - "bidirectional-navigation-links"
  - "document-atomization-u-curve"
  - "classification-disposition-decision-tree"
  - "phased-rollout-validation"
---
# 元原子化二分+概览模式操作指南

## 模式概述

当复盘报告的 `execution-retrospective.md`（或其他长文档）中存在**单一超长章节**（通常是"各阶段详细记录"或"分阶段复盘"）占据全文50%以上、且主文件因此超过250-300行时，采用两种标准拆分策略将该长章节原子化，主文件保留**概览表+导航链接**，实现"主文件可读可导航、详情文件独立可维护"的二元结构。

本模式是[large-document-atomization-method.md](large-document-atomization-method.md)的**轻量子模式**——针对的不是2000行级别的巨型文档，而是250-500行的中型文档中某一章节膨胀的场景，拆分粒度更细、操作成本更低。

## 两种拆分策略

### 策略A：时间二分法（Time Bisect）

**适用场景**：长章节内容具有**线性时间/阶段顺序**（如"七阶段深度复盘"、"按周/月记录的过程回顾"），且阶段数≥5个。

**拆分方式**：按时间轴将阶段分为两半，各放入一个原子文件。

```
原章节（N个阶段，150-400行）
    ↓ 二分
文件1：阶段1~⌈N/2⌉（前期/奠基期/上半场）
文件2：阶段⌈N/2⌉+1~N（后期/验证期/下半场）
```

**命名规范**：`{原章节关键词}-s{起始}-s{结束}.md`
- 示例：`execution-phases-s1-s3.md`、`execution-phases-s4-s7.md`

### 策略B：概览+详情分离法（Overview-Detail Separation）

**适用场景**：长章节包含**结构化列表内容**（如"各阶段详细记录"、"模板升级对比"、"功能清单详解"），每个条目都有统一的子结构。

**拆分方式**：将所有条目的详细内容整体移至一个 `*-details.md` 文件，主文件保留概览摘要表。

```
原章节（6个阶段详细记录，200-260行）
    ↓ 分离
主文件：概览表（每个条目1行，含核心指标+链接）
详情文件：execution-phase-details.md（所有条目的完整内容）
```

**命名规范**：`{原章节关键词}-details.md`
- 示例：`execution-phase-details.md`、`l3-template-upgrade-details.md`

### 策略选择决策树

```
长章节是否需要拆分？（三标准检验）
├── 主文件总行数 < 200行 → ❌ 不需要拆分
├── 长章节占比 < 30% → ❌ 不需要拆分
└── 需要拆分 → 选择策略：
    ├── 内容是否按时间/阶段线性排列？且阶段数≥5？
    │   ├── 是 → 策略A（时间二分法）
    │   └── 否 → 策略B（概览+详情分离法）
    └── （两种策略不互斥：可对时间线用二分法，对结构化列表用详情分离法）
```

---

## 批量推广前置检查清单

当需要将本模式**批量应用于N≥5个文档/项目**时，在开始拆分前必须完成以下7项前置检查（参考[phased-rollout-validation.md](../governance-strategy/phased-rollout-validation.md)渐进式验证模式）：

- [ ] **扫描盘点**：先扫描所有待处理对象，列出完整清单（文件路径、行数、当前状态）
- [ ] **分类处置**：按下方"分类处置决策树"对每个对象标记处置方式，生成处置清单
- [ ] **验证批选择**：选择3-5个低风险对象作为P0验证批
- [ ] **验证批执行**：先完成P0批，运行所有检查脚本，记录遇到的问题
- [ ] **检查项更新**：将P0批发现的问题转化为检查项，添加到检查清单
- [ ] **分批执行**：按风险等级分P1（中风险）/P2（高风险/特殊）批次执行，每批完成后验证
- [ ] **全量验证**：所有批次完成后，运行全量链接检查和结构验证

---

## 分类处置决策树

批量处理前，对每个待处理对象按以下决策树判断处置方式（本模式的分类策略是[classification-disposition-decision-tree.md](classification-disposition-decision-tree.md)通用模式在元原子化场景的专用版本）：

```
待处理对象
├── 已有原子化目录（phases/、details/、*-s1-s3.md、*-details.md等）？
│   └── ✅ 补全导航：检查父README导航完整性，补全缺失条目，修复断链，不重新拆分
├── 文件<100行 或 内容高度关联、分段独立阅读价值低？
│   └── ⏭️ 保留原状：不拆分，添加changelog条目和适当导航即可
├── 文件已归档/已完成（archive状态）？
│   └── ⏭️ 保持原状：仅修复断链，不做结构改动
└── 以上都不是
    └── ✂️ 按本模式SOP拆分（下方6步法）
```

**判断准则补充**：
- "已有原子化目录"包括`*-details.md`/`*-s{起始}-s{结束}.md`文件形式，以及`phases/`/`chapters/`/`details/`等子目录形式
- "内容高度关联"的判断标准：拆分后任意子文件无法独立理解，必须频繁交叉引用其他子文件
- "分段独立阅读价值低"的判断标准：单段<30行，或段落之间构成连续的推理/因果链条
- 当拿不准是否拆分时，遵循"保守原则"——先不拆分，在使用中如果确实发现导航困难再拆分

---

## 操作步骤（6步法）

### 步骤1：识别目标长章节

```powershell
# 扫描 execution-retrospective.md 中超过250行的文件
Get-ChildItem -Path "docs\retrospective\reports" -Recurse -Filter "execution-retrospective.md" | ForEach-Object {
    $lines = (Get-Content $_.FullName | Measure-Object -Line).Lines
    if ($lines -gt 250) { "$lines `t $($_.FullName)" }
} | Sort-Object { [int]($_ -split "`t")[0] } -Descending
```

**判断标准**（三标准检验，参考[atomization-three-criteria-test.md](atomization-three-criteria-test.md)）：
1. **单一职责违例**：主文件中某一章节占比 >50%，该章节可独立作为一份文档阅读
2. **独立可验证**：拆分后的详情文件可以独立阅读，不依赖主文件其他章节
3. **命名聚合性**：拆分出的文件能用一个明确的短语命名（如"各阶段详细记录"）

### 步骤2：选择拆分策略

根据内容特征选择策略A或策略B（见上方决策树）。

**前置检查**：在创建新文件之前，**先检查目标目录是否已存在同类原子文件或子目录**（如 `phases/` 目录下已有各阶段独立文件），避免重复创建冗余文件。

```powershell
# 检查是否已有子目录拆分
ls <目标目录> | Select-Object Name
```

如果发现已有 `phases/`、`details/` 等子目录或已存在的 `*-details.md` 文件，应链接到已有文件而非重新创建。

### 步骤3：提取内容到详情文件

**策略A操作**（时间二分）：

1. 新建两个文件，使用 `s{起始}-s{结束}` 命名
2. 将前段内容（阶段1~⌈N/2⌉）完整移入第一个文件
3. 将后段内容（阶段⌈N/2⌉+1~N）完整移入第二个文件
4. 为每个文件添加YAML frontmatter：

```yaml
---
id: "{文档id}-phases-s1-s3"
title: "XX项目执行阶段详细复盘（阶段一~三）"
source: "execution-retrospective.md"
x-toml-ref: "{对应toml路径}"
---
```

**策略B操作**（概览+详情分离）：

1. 新建一个 `*-details.md` 文件
2. 将长章节的所有详细条目完整移入该文件
3. 保留原有的章节结构（二级标题、三级标题）
4. 添加YAML frontmatter
5. 在文件开头添加一句回溯说明：

```markdown
> 本文件是 [execution-retrospective.md](execution-retrospective.md) 第二章"各阶段详细记录"的原子化拆分，包含Phase 1-6的完整执行步骤。
```

### 步骤4：改造主文件为概览入口

主文件中被拆分章节替换为**概览表+链接**，格式如下：

**策略A概览表模板**：

```markdown
## 三、七阶段深度复盘

七阶段详细复盘已按"奠基期→闭合期"和"治理期→验证期"拆分为两个原子文件：

| 文件 | 覆盖阶段 | 时间段 | 核心主题 |
|------|---------|--------|---------|
| [execution-phases-s1-s3.md](execution-phases-s1-s3.md) | 阶段一~三 | MM/DD-MM/DD | {核心主题简述} |
| [execution-phases-s4-s7.md](execution-phases-s4-s7.md) | 阶段四~七 | MM/DD-MM/DD | {核心主题简述} |

每个阶段包含：{说明详情文件中的分析维度}。
```

**策略B概览表模板**：

```markdown
## 第二章：各阶段详细记录

各阶段（Phase 1-N）的完整执行步骤、输入条件、产出和备注已原子化拆分至 [execution-phase-details.md](execution-phase-details.md)。

### 阶段概览

| 阶段 | 名称 | 核心产出 | 耗时 | 关键Step数 |
|------|------|---------|------|-----------|
| Phase 1 | {名称} | {核心产出摘要} | {耗时} | {步骤数} |
| Phase 2 | {名称} | {核心产出摘要} | {耗时} | {步骤数} |
| ... | ... | ... | ... | ... |

详细执行步骤见 [execution-phase-details.md](execution-phase-details.md)。
```

**关键原则**：
- 概览表每行是一个条目的**一句话摘要**，让读者无需跳转即可了解全貌
- 表格列选择：保留最有信息量的3-5列，不要把详情中的所有字段都塞进概览表
- 主文件中添加一次 `> 版本说明` 标注原子化变更（如 `> **v1.2 更新**：七阶段深度复盘已原子化拆分...`）

### 步骤5：更新父级README导航

更新当前目录的 `README.md`，在"交付物清单"和"子模块导航"两个表格中添加新建原子文件的入口行：

```markdown
| 各阶段详细记录 | [execution-phase-details.md](execution-phase-details.md) | Phase 1-6 完整执行步骤、输入条件、产出和备注 |
```

### 步骤6：链接验证

```powershell
# 验证目标目录所有链接
python .agents/scripts/check-links.py --path "docs/retrospective/reports/{分类}/{项目目录}"
```

确保：
- ✅ 所有本地引用有效（不能有断链）
- ✅ 详情文件中如有回链，路径正确
- ✅ README导航表中的新链接有效

## 正反例

### 正例1：全生命周期复盘七阶段拆分（策略A）

| 拆分前 | 拆分后 |
|-------|-------|
| execution-retrospective.md："七阶段深度复盘"章节占350行中的约200行 | execution-retrospective.md ~183行（概览表10行） + execution-phases-s1-s3.md + execution-phases-s4-s7.md |
| 浏览阶段三详情需滚过所有阶段 | 直接打开对应时间段文件 |
| 主文件信息密度不均匀（阶段复盘膨胀，其他章节被挤压） | 主文件概览+决策+评估结构均衡 |

### 正例2：Tuya HA学习阶段详情分离（策略B）

| 拆分前 | 拆分后 |
|-------|-------|
| execution-retrospective.md 422行，第二章261行（62%） | execution-retrospective.md ~207行（概览表13行） + execution-phase-details.md 261行 |
| 想看关键决策需滚过261行阶段记录 | 关键决策第三章紧随概览表，阅读路径缩短 |
| 无法单独引用某阶段详情 | execution-phase-details.md可独立链接 |

### 正例3：已有子目录的情况（避免冗余）

TuyaOpen 项目已有 `phases/phase-1~6.md` 的深度拆分结构，最初错误地创建了 `execution-phase-details.md`（冗余文件），发现后删除冗余文件，将主文件概览表直接链接到已有 `phases/` 目录下的文件。

### 反模式

| 反模式 | 表现 | 问题 |
|--------|------|------|
| **拆分过度** | 3个阶段也拆成两个文件 | 内容太少，文件碎片化增加跳转成本 |
| **概览表过详** | 概览表保留了所有详情字段，每行50+字符 | 主文件依然很长，概览失去"概"的意义 |
| **概览表过简** | 只有"见xxx.md"一句话，无表格 | 读者不跳转就不知道内容概要，导航价值丧失 |
| **忽略已有结构** | 不检查就新建details文件，与已有phases/目录重复 | 产生冗余文件，读者困惑 |
| **遗漏README更新** | 只改了主文件，没更新README导航表 | README成为过时文档，新读者找不到详情文件 |
| **详情文件无回溯链接** | 详情文件开头没有指回主文件的说明 | 读者直接打开详情文件时不知道上下文位置 |

## 适用边界

### 适用场景

- ✅ execution-retrospective.md 在250-500行之间，某一章节占比>50%
- ✅ 长章节内容具有结构化特征（阶段列表、对比表格、清单条目）
- ✅ 使用四文件原子化复盘模板生成的复盘报告
- ✅ 需要快速降低主文件行数、改善阅读体验的中型文档

### 不适用场景

- ❌ 主文件 < 200行（拆分收益不足）
- ❌ 长章节 < 100行（不需要拆分）
- ❌ 非结构化散文式内容（无法提炼概览表）
- ❌ 2000行级巨型文档（应使用[large-document-atomization-method.md](large-document-atomization-method.md)完整五步法）
- ❌ L0旧单文件模板格式（使用 `2.1/2.2/2.3` 编号的旧报告需先升级为四文件模板）

## 量化效果

从3个应用案例统计：

| 指标 | 拆分前 | 拆分后 | 改善幅度 |
|------|-------|-------|---------|
| 主文件平均行数 | 408行 | ~196行 | **-52%** |
| 主文件最长章节占比 | 58% | <10%（概览表） | 结构均衡 |
| 单文件最大行数 | 457行 | 261行 | -43% |
| 新增文件数 | - | 1-2个 | 增量极小 |
| 链接验证通过率 | - | 100% | 无断链 |

## 配套工具

- [check-links.py](../../../../../.agents/scripts/check-links.py)：链接验证（步骤6必跑）
- [finalize-atomization.py](../../../../../.agents/scripts/finalize-atomization.py)：原子化收尾（断链修复+导航更新），注意使用 `--scope` 参数限定目录
- [atomization-three-criteria-test.md](atomization-three-criteria-test.md)：拆分前三标准检验

## 与其他模式的关系

| 关系模式 | 关系类型 | 说明 |
|---------|---------|------|
| [large-document-atomization-method.md](large-document-atomization-method.md) | 父模式 | 本模式是大文档原子化法针对"中型文档单章节膨胀"场景的轻量子模式 |
| [entry-container-separation.md](entry-container-separation.md) | 架构原则 | 概览（入口）+详情（容器）分离是entry-container-separation在章节级的应用 |
| [atomization-three-criteria-test.md](atomization-three-criteria-test.md) | 判断标准 | 用于步骤1判断是否需要拆分 |
| [atomization-three-tier-classification.md](atomization-three-tier-classification.md) | 分类框架 | 判断文档是否达到需要本模式处理的复杂度 |
| [bidirectional-navigation-links.md](bidirectional-navigation-links.md) | 配套要求 | 详情文件应回溯链接到主文件，形成双向导航 |
| [document-atomization-u-curve.md](document-atomization-u-curve.md) | 理论基础 | 拆分粒度的U曲线——本模式是中型文档的最优拆分点 |
| [progressive-readme-growth.md](progressive-readme-growth.md) | 渐进模式 | README随原子化逐步扩展导航表，符合渐进增长原则 |
