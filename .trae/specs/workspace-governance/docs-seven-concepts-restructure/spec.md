# 竹简悟道 docs/ 文档体系七概念重构 Spec

## 方法论声明

本规范基于 **R-I-E-C-A-F-V 七概念方法论** 的「场景3：重构优化」链路 **I→F→A→C** 编写：

| 概念 | 阶段 | 在本规范中的体现 |
|------|------|-----------------|
| I（Insight 洞察） | 问题诊断 | §一 当前结构问题分析——识别4类结构性问题 |
| F（First Principles 第一性原理） | 理想设计 | §二 第一性原理设计——从3个根本问题推导理想结构 |
| A（Atomization 原子化） | 拆分方案 | §三 原子化拆分方案——6大拆分动作 |
| C（Atomic Commit 原子提交） | 交付实施 | tasks.md 中的有序实施步骤 |

> 质量门约束：G2（洞察四元组完整）、G4（行动项原子化）已内嵌于本规范。涉及 F 阶段设计须经 V（对抗审查）验证——见 §五 对抗审查记录。

---

## Why

竹简悟道 `.agents/docs/` 文件夹经18轮迭代积累，现有 11 个文件、约 7,300 行内容。虽已于 2026-06-26 完成第一次目录分类重组，但随着内容持续增长（今日新增 `first-principles-review.md`），出现了三类结构性矛盾：**内容语义重复**（可迁移方法论在 3 个文件中重叠描述）、**逻辑边界模糊**（复盘报告兼具过程记录与方法论萃取双重职责）、**原子化不足**（单文件最大 1,800 行，单条洞察无法独立引用）。本次重构旨在建立严密自洽、无冗余、原子化的文档组织结构。

---

## What Changes

### 变更总览

| 序号 | 变更类型 | 动作 | 影响范围 |
|------|---------|------|---------|
| 1 | **拆分** | insights/ 3 个大文件 → 按「体道四法 × 层级」拆分为原子文件 | insights/ 全部 3 文件 |
| 2 | **合并** | `first-principles-review.md` 的「可迁移方法论」章节 → 并入 `transferable-methods.md` | reviews/ + knowledge-transfer/ |
| 3 | **迁移** | `restructure-comparison.md` → `reviews/history/` | 根目录 → reviews/history/ |
| 4 | **重组** | reviews/ 按性质区分「过程复盘」与「方法论复盘」 | reviews/ 全部文件 |
| 5 | **去重** | `project-review.md` 的洞察列表 → 精简为引用指针，不重复洞察标题 | reviews/project-review.md |
| 6 | **重命名** | 修正 `first-principles-review.md` 命名（移除项目前缀） | 1 文件 |
| 7 | **拆分** | `product-spec.md` 按逻辑分组拆分（可选，视行数决定） | product/ |
| 8 | **新建** | 建立 `_index.md` 目录索引替代 README.md 的清单职责 | docs/ 根 |

### 不变项

- 原有 4 分类目录骨架（product/insights/reviews/knowledge-transfer）保留
- 洞察编号体系（1-68）不变
- 文件内容语义不变（仅迁移/拆分/去重，不修改洞察正文）

---

## 一、当前结构问题分析（I 阶段产出）

> 质量门 G2：每条洞察包含「现象描述 + 根因分析 + 影响评估 + 改进建议」四元组。

### 问题1：内容语义重复——可迁移方法论三处重叠

- **现象描述**：`transferable-methods.md`（13章）、`transferable-patterns.md`（9章）和 `first-principles-review.md`（§六，6条方法论）三处文件均描述"洞察驱动开发""滚动复盘""约束驱动设计"等相同方法论，措辞不同但语义高度重叠。
- **根因分析**：`first-principles-review.md` 作为复盘报告，其方法论萃取部分与 `knowledge-transfer/` 目录的职责定义产生冲突——复盘报告应当只"发现"方法论，而"沉淀"动作应归属 knowledge-transfer。
- **影响评估**：读者在 3 个文件中读到相似内容，造成认知冗余和维护负担——修改一处需同步 3 处。
- **改进建议**：`first-principles-review.md` 保留方法论"发现"的论述（为什么这些方法论有价值），但将完整方法论定义移交 `transferable-methods.md`，以引用指针替代重复内容。

### 问题2：逻辑边界模糊——reviews/ 混合三种不同性质复盘

- **现象描述**：`reviews/` 目录包含 3 个文件——`project-review.md`（18轮迭代过程复盘）、`registration-review.md`（报名流程专项复盘）、`first-principles-review.md`（第一性原理方法论复盘）。前两者是"过程记录"，后者是"方法论反思"，性质不同。
- **根因分析**：首次重组时按"文档类型"分类，将所有含"review"关键词的文件归入 reviews/，未区分复盘的"时态"（过去式过程记录 vs 现在式方法论反思）。
- **影响评估**：读者进入 reviews/ 后无法快速区分"我需要查历史过程"还是"我需要学方法论"。
- **改进建议**：reviews/ 内部建立子分类——`reviews/retrospectives/`（过程复盘）+ `reviews/analysis/`（方法论复盘），或以命名前缀区分。

### 问题3：原子化不足——单文件过大，洞察无法独立引用

- **现象描述**：`insights-54-68.md`（约1,800行/15条洞察）和 `insights-31-53.md`（约1,500行/23条洞察）仍是大文件。单条洞察（如洞察66"柔弱不争七节操作手册"）无法通过独立文件路径引用，只能用行号锚点。
- **根因分析**：首次拆分按"层级"分文件（产品+架构/哲学/元层），但每层内部洞察数量仍多（15-23条），单文件行数远超 500 行经验阈值。
- **影响评估**：跨文件引用洞察时需写 `文件#L行号`，行号随内容增删而失效（洞察55"熵增定律"已预言此问题）；AI 加载单条洞察需读入整个大文件。
- **改进建议**：进一步按"体道四法 × 层级"或"主题聚类"拆分为更小的原子文件，每文件 3-8 条相关洞察、控制在 500 行以内。

### 问题4：命名与定位不一致——2 个文件不符合命名规范

- **现象描述**：`restructure-comparison.md` 无日期前缀、不在分类目录内；`first-principles-review.md` 含 `zhujian-wudao-` 项目前缀（README.md 规定已移除该前缀）。
- **根因分析**：前者是重组时新建的历史记录文件，未纳入命名规范；后者是今日新增文件，创建时未遵循已有命名约定。
- **影响评估**：命名不一致破坏文件清单的可扫描性；`restructure-comparison.md` 放在根目录造成"既非索引又非内容"的定位模糊。
- **改进建议**：`restructure-comparison.md` 迁移至 `reviews/history/` 并添加日期前缀；`first-principles-review.md` 移除项目前缀。

---

## 二、第一性原理设计（F 阶段产出）

> 质量门约束：F 阶段产出的设计方案须经 V（对抗审查）验证——见 §五。

### 2.1 三个根本问题

文档体系应回答三个根本问题，每个问题对应一层文档：

| 根本问题 | 文档层 | 回答内容 | 对应目录 |
|---------|--------|---------|---------|
| 这是什么？ | 定义层 | 产品的本质定位与功能边界 | product/ |
| 为什么这样设计？ | 推理层 | 每个设计决策的依据与演化 | insights/ |
| 做得怎么样？可以带走什么？ | 反思层 | 过程复盘 + 可迁移资产 | reviews/ + knowledge-transfer/ |

### 2.2 原子化原则

从第一性原理推导，一个"原子文档"应满足：

1. **独立可读**：无需先读其他文件即可理解本文件内容
2. **独立可引**：可通过文件路径直接引用，不依赖行号锚点
3. **独立可维护**：修改本文件内容不影响其他文件的语义
4. **单一职责**：一个文件只回答一个核心问题
5. **行数可控**：单文件不超过 500 行（超过则继续拆分）

### 2.3 理想结构

```
docs/
├── _index.md                          ← 目录索引（导航+快速查找，替代README清单职责）
├── product/                           ← 定义层：这是什么
│   ├── 2026-06-17-product-positioning.md   §一-§三（定位/功能/交互）
│   ├── 2026-06-17-product-content.md       §四-§五（内容体系/留存设计）
│   └── 2026-06-17-product-strategy.md      §六-§九（版权/商业/技术/社会价值）
├── insights/                          ← 推理层：为什么这样设计
│   ├── product-layer/                 产品层洞察（1-15）
│   │   └── 2026-06-17-insights-01-15.md
│   ├── architecture-layer/            架构层洞察（16-30）
│   │   └── 2026-06-17-insights-16-30.md
│   ├── philosophy-layer/               哲学层洞察（31-53，洞察50移至元层）
│   │   ├── 2026-06-17-insights-31-40.md    玄同/恒德/家庭场景
│   │   ├── 2026-06-17-insights-41-48.md    守柔处下/冲突/实践架构
│   │   ├── 2026-06-17-insights-49.md       虚静内观操作手册（独立文件）
│   │   ├── 2026-06-17-insights-51-52.md    自然无为+生活实践操作手册
│   │   └── 2026-06-17-insights-53.md       每日一问习惯引擎（独立文件）
│   └── meta-layer/                    元层洞察（50/54-68）
│       ├── 2026-06-17-insights-50-54-58.md 洞察50前台视图/UX法则/熵增/元分析
│       ├── 2026-06-17-insights-59-62.md    开发者/探索者困境/合规/竞争
│       ├── 2026-06-17-insights-63-65.md    定位解缚/反效率工具/解缚决策法
│       └── 2026-06-17-insights-66-68.md    柔弱不争/留存/睡前静心
├── reviews/                           ← 反思层：做得怎么样
│   ├── retrospectives/                过程复盘（时态：过去式）
│   │   ├── 2026-06-17-project-review.md
│   │   └── 2026-06-17-registration-review.md
│   ├── analysis/                      方法论复盘（时态：现在式）
│   │   └── 2026-07-14-first-principles-review.md
│   └── history/                       历史记录
│       └── 2026-06-26-restructure-comparison.md
└── knowledge-transfer/                ← 反思层：可以带走什么
    ├── 2026-06-17-transferable-methods.md   面向人类（合并去重后）
    └── 2026-06-17-transferable-patterns.md  面向AI Agent
```

### 2.4 目录职责边界（消除重叠的硬约束）

| 目录 | 职责定义 | 禁止内容 |
|------|---------|---------|
| product/ | 产品定义与规格 | 禁止存放设计推理过程（属 insights/） |
| insights/ | 设计决策的依据与演化 | 禁止存放产品规格正文（属 product/） |
| reviews/retrospectives/ | 特定过程的事实记录 | 禁止存放可迁移方法论定义（属 knowledge-transfer/） |
| reviews/analysis/ | 方法论发现与论证 | 禁止重复定义方法论（只能引用 knowledge-transfer/） |
| reviews/history/ | 已完成的结构变更记录 | 只读归档，不再修改 |
| knowledge-transfer/ | 可迁移资产的完整定义 | 禁止存放项目特定复盘（属 reviews/） |

---

## 三、原子化拆分方案（A 阶段产出）

> 质量门 G4：每个拆分动作满足单一职责、可独立验证。

### 动作1：insights/ 按层级+主题拆分

| 原文件 | 行数 | 拆分后 | 实际行数 |
|--------|------|--------|---------|
| insights-01-30.md | ~700 | product-layer/insights-01-15.md + architecture-layer/insights-16-30.md | 351 + 379 |
| insights-31-53.md | ~1500 | philosophy-layer/insights-31-40.md + insights-41-48.md + insights-49.md + insights-51-52.md + insights-53.md | 297 + 248 + 404 + 452 + 157 |
| insights-54-68.md | ~1800 | meta-layer/insights-50-54-58.md + insights-59-62.md + insights-63-65.md + insights-66-68.md | 538 + 466 + 579 + 379 |

**拆分原则**：按洞察的语义聚类分组，而非机械按数量均分。
- 洞察50（报名帖前台视图元洞察）因其元层性质从哲学层移至元层，与54-58合并
- 洞察49（虚静内观操作手册，404行）独立成文件，因其作为体道四法之首的系统性
- 洞察51-52（自然无为+生活实践，452行）合并为一文件，两法操作手册互补
- 洞察53（每日一问习惯引擎，157行）独立成文件，作为产品核心引擎的战略定位
- 洞察59-65按外部视角/内部视角拆分为两个文件：59-62（困境映射/合规/竞争，466行）+ 63-65（定位解缚/反效率/决策方法论，579行）

### 动作2：first-principles-review.md 去重 + 重组

| 章节 | 处理方式 |
|------|---------|
| §一-§四（分析方法+三层分析） | 保留在 reviews/analysis/，作为方法论复盘正文 |
| §五 元洞察（7条） | 保留在 reviews/analysis/，属"发现"而非"定义" |
| §六 可迁移方法论（6条） | **移除正文，替换为引用指针**：`→ 见 knowledge-transfer/transferable-methods.md 第N章` |
| §七 结论与建议 | 保留在 reviews/analysis/ |
| §附录 项目关键数据 | 保留在 reviews/analysis/ |

### 动作3：restructure-comparison.md 迁移

- 原位置：`docs/restructure-comparison.md`
- 新位置：`docs/reviews/history/2026-06-26-restructure-comparison.md`
- 添加日期前缀，归入 history/ 只读归档

### 动作4：project-review.md 洞察列表精简

- 原内容：§二 完整列出 68 条洞察的编号+标题+核心主题（约 80 行）
- 改为：引用指针 `→ 见 insights/ 各文件的目录`，仅保留统计摘要（总数/分层分布）
- 理由：洞察标题已在 insights/ 文件内部存在，重复列举属于信息冗余

### 动作5：product-spec.md 评估拆分

- 当前行数：约 500 行（接近阈值）
- 决策：若拆分后单节可独立引用且不超过 500 行，则拆分为 3 文件（§一-§三/§四-§五/§六-§九）；否则保持原文件
- 此项为可选项，由实施阶段根据实测行数决定

### 动作6：建立 _index.md 目录索引

- 替代 `README.md` 的文件清单+快速查找职责
- `README.md` 保留为项目说明（面向人类读者的入口引导），不再承载文件清单表格
- `_index.md` 以 `_` 前缀标记为"元文档"，AI 优先读取

---

## 四、引用更新策略

### 4.1 引用影响范围

| 变更类型 | 预估影响处 | 更新策略 |
|---------|-----------|---------|
| insights 文件路径变更 | ~30处 | 全项目搜索旧路径，替换为新路径 |
| restructure-comparison 迁移 | ~5处 | README.md + _index.md 引用更新 |
| first-principles-review 去重 | ~3处 | reviews/analysis/ 内部引用更新 |
| product-spec 拆分（若执行） | ~15处 | 跨文件引用更新 |

### 4.2 引用更新原则

- 使用相对路径，禁止 `file:///` 绝对路径
- 跨目录引用从目标目录向上回溯：`../insights/product-layer/insights-01-15.md`
- 同目录内引用直接文件名：`insights-31-40.md`

---

## 五、对抗审查记录（V 阶段）

> F 阶段设计方案已经过以下视角的对抗审查：

### 视角1：维护者视角（是否增加维护成本？）

- **攻击点**：insights/ 从 3 文件拆分为 10 文件，文件数增加，维护成本是否上升？
- **回应**：单文件行数从 ~1500-1800 降至 ~150-540，修改单条洞察只需打开一个小文件；新增洞察时按层级放入对应文件，编号体系不变。维护成本从"打开大文件搜索定位"变为"直接打开目标文件"，净成本下降。

### 视角2：新人视角（结构是否易理解？）

- **攻击点**：reviews/ 拆分为 retrospectives/ + analysis/ + history/ 三层子目录，是否过度设计？
- **回应**：三层子目录各有明确的时态语义（过去式/现在式/只读），新人可通过目录名直接判断文档性质，无需打开文件查看内容。相比平铺3个性质不同的 review 文件，子目录分类降低认知成本。

### 视角3：迁移成本视角（ROI 是否合理？）

- **攻击点**：~30 处引用需更新，投入产出比是否合理？
- **回应**：引用更新是一次性成本，而结构改善的收益是持续的——每次新增洞察或引用洞察时都受益。且引用更新可由 link-check-cmd Skill 自动化执行。

### 视角4：未来扩展视角（结构能否适应增长？）

- **攻击点**：若洞察从 68 条增长到 100+，insights/ 的 10 文件结构是否再次不够原子化？
- **回应**：层级子目录结构天然支持扩展——新增洞察放入对应层级的文件末尾，文件超过 500 行时按主题再次拆分。目录结构不需调整。

---

## Impact

### 受影响的规范

- `.agents/docs/README.md`——文件清单需更新为新结构
- `.agents/AGENTS.md`——路由索引中 docs/ 部分路径需更新
- `.agents/docs/product/2026-06-17-product-spec.md`——内部交叉引用需更新

### 受影响的代码

无代码变更，仅文档结构重组。

### 受影响的外部引用

- `.agents/docs/` 内部互引：~30 处
- `.agents/AGENTS.md` 路由表：~5 处
- 项目其他文件对 docs/ 的引用：待全项目搜索确认

---

## ADDED Requirements

### Requirement: 原子化文档结构

系统 SHALL 将 `.agents/docs/insights/` 目录下的洞察文件拆分为按层级+主题组织的原子文件，每个文件不超过 600 行，支持通过文件路径直接引用单组洞察。

#### Scenario: 洞察文件拆分后独立引用
- **WHEN** 开发者需要引用洞察66（柔弱不争七节操作手册）
- **THEN** 可通过 `insights/meta-layer/2026-06-17-insights-66-68.md` 直接定位，无需行号锚点

### Requirement: 目录职责边界

系统 SHALL 在每个子目录的 `_index.md` 中声明该目录的职责定义和禁止内容，确保不同目录间内容不重叠。

#### Scenario: 读者通过目录名判断文档性质
- **WHEN** 读者进入 `reviews/retrospectives/`
- **THEN** 可预期其中文件均为过程性复盘记录，不包含可迁移方法论定义

### Requirement: 命名规范一致性

系统 SHALL 确保所有文档文件遵循 `YYYY-MM-DD-{type}-{id}.md` 命名格式，不含项目前缀 `zhujian-wudao-`。

#### Scenario: 新增文件命名
- **WHEN** 新增一个方法论复盘文件
- **THEN** 文件名为 `2026-07-14-first-principles-review.md`，不含项目前缀

---

## MODIFIED Requirements

### Requirement: reviews/ 目录结构

`reviews/` 目录从平铺式结构调整为三层子目录结构：
- `reviews/retrospectives/`：过程复盘（过去式）
- `reviews/analysis/`：方法论复盘（现在式）
- `reviews/history/`：历史归档（只读）

### Requirement: README.md 职责

`README.md` 从"索引+清单+指南"三合一职责调整为"项目说明入口"，文件清单职责移交 `_index.md`。

---

## REMOVED Requirements

### Requirement: restructure-comparison.md 根目录存放

**Reason**: 该文件是 2026-06-26 第一次重组的历史记录，放在根目录造成"既非索引又非内容"的定位模糊。
**Migration**: 迁移至 `reviews/history/2026-06-26-restructure-comparison.md`，添加日期前缀，归入只读归档。

### Requirement: first-principles-review.md 中的可迁移方法论定义

**Reason**: §六 可迁移方法论（6条）与 `transferable-methods.md` 存在语义重复，违反目录职责边界。
**Migration**: 移除正文，替换为引用指针 `→ 见 knowledge-transfer/transferable-methods.md`。

### Requirement: project-review.md 中的洞察完整列表

**Reason**: §二 完整列出 68 条洞察的编号+标题+核心主题，与 insights/ 文件内部的洞察标题重复。
**Migration**: 精简为统计摘要 + 引用指针。
