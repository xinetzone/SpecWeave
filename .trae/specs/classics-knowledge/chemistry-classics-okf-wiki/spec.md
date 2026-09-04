---
status: "draft"
name: chemistry-classics-okf-wiki-spec
version: 1.0.0
created: 2026-08-30
source: "公开网络调研——公版化学经典原文（Wikisource/Project Gutenberg/ctext.org/维基文库）+ 权威学术共识解读"
methodology: seven-concepts 场景4（知识沉淀）R→I→E→V→C
content-sensitivity: Public（化学经典原文属公共领域，解读为自撰综述）
---

# 中西化学经典原文与解读 OKF Wiki 教程

## Why

awesome-okf-xs 知识包库现有 13 个技术域、280 个知识包，全部面向开源软件源码与 AI 平台；其中 `think/` 域已收录《老子》帛书阅读教程（boshu-reading），验证了"经典原文选读 + 现代解读"的知识包范式在非软件领域的可行性。

用户希望以同样的范式，**全面系统地调研和整理化学著作的原文与解读**，将化学这一自然科学基础学科的元典引入知识库。经用户确认四项关键决策：

1. **著作范围**：中西化学经典双线索——西方近代化学奠基经典（化学革命主线）与中国古代炼丹/工艺化学典籍（经验化学传统）对照组织；
2. **内容形态**：经典原文选读 + 现代解读教程（对齐 boshu-reading 范式：原文选段、注释、现代科学对照解读、阅读路径）；
3. **放置位置**：新建第 14 个技术域 `science/`（自然科学），下设 `chemistry/` 分组，为未来物理、生物等学科预留扩展位；
4. **交付规模**：多 bundle 大规模铺开，首批 7 个知识包（西方 4 + 中国 3），总计约 70+ 篇文档。

本地工作区未发现化学文献资料（已递归搜索 `化学|chemistry` 无结果），全部素材来自公开网络：公版原著原文（1900 年前西方著作、中国古代典籍）与权威学术共识解读。

## What Changes

在 `projects/awesome-okf-xs/doc/bundles/` 下新增：

```
science/                                    # 新建技术域（第14域：自然科学）
  index.md                                  # 域索引（分组导航 + toctree）
  chemistry/                                # 新建分组（化学经典双线索）
    index.md                                # 分组索引（7 束导航 + toctree）
    boyle-sceptical-chymist/                # 波义耳《怀疑的化学家》(1661)
    lavoisier-treatise/                     # 拉瓦锡《化学基础论》(1789)
    dalton-new-system/                      # 道尔顿《化学哲学新体系》(1808)
    mendeleev-periodic-law/                 # 门捷列夫元素周期律 (1869)
    cantongqi/                              # 《周易参同契》(东汉·魏伯阳)
    baopuzi/                                # 《抱朴子·内篇》(东晋·葛洪)
    tiangong-kaiwu/                         # 《天工开物》(明·宋应星)
```

每个知识包遵循 OKF v0.2 三层结构（对齐 boshu-reading 范式）：

```
<bundle>/
  index.md            # 束入口（type: OKF，含 okf_version/sources/generated/verified/status）
  log.md              # 更新日志（YYYY-MM-DD 倒序）
  facts.md            # 零推测事实清单（编号 F-xxx，每条可溯源）
  insights.md         # 核心洞察（四元组）+ 知识地图
  concepts/
    index.md          # 概念索引 + toctree
    00-*.md …         # 4-6 篇概念文档（含原文选读+现代解读）
  examples/
    index.md
    01-*.md …         # 2 篇实操示例（原文精读实操 + 阅读路线）
  references/
    index.md
    *.md              # 2-3 篇信源登记（公版原文 URL + 权威解读 URL）
```

同步更新 `bundles/index.md` 总索引（计数 13→14 域 / 32→33 组 / 280→287 束、域导航表、toctree、生态关系 mermaid 图）。

方法论链路（seven-concepts 场景4 知识沉淀）：
- **R（事实采集）**：逐束网络调研，登记公版原文信源并核验 URL 可达，产出 facts.md（G1：事实无因果词、可溯源）；
- **I（洞察）**：提炼每部著作的核心洞察（G2：现象/根因/影响/建议四元组）与中西对照知识地图；
- **E（批量生成）**：按三层结构生成全部文档（G3：沉淀"公版经典原文+现代解读"可迁移生产模式）；
- **V（对抗审查）**：fresh context 独立审查，每束 ≥5 条关键事实回源抽查；
- **C（原子提交）**：审查通过后按线索原子提交（须经用户确认；子模块内提交，主仓库 gitlink 另行处理）。

## Impact

- **新增目录**：`projects/awesome-okf-xs/doc/bundles/science/`（1 域索引 + 1 组索引 + 7 束，约 70+ 个 .md 文件）
- **修改文件**：`doc/bundles/index.md`（总索引计数、导航表、toctree、mermaid 生态图）
- **不修改**：任何现有 bundle 内容；其他 13 个域的文件
- **构建验证**：`invoke gates.all`（UTF-8 + toctree 完整性）与 `invoke clean && invoke build`（Sphinx 0 warning）必须通过
- **子模块边界**：产出物位于 awesome-okf-xs git submodule 内（第一方子项目，允许子模块内开发）；提交发生在子模块内，主仓库 gitlink 更新需单独确认

## ADDED Requirements

### Requirement: science 技术域与 chemistry 分组骨架

系统 SHALL 在 `doc/bundles/science/` 建立自然科学技术域，包含域索引 `index.md`（frontmatter `type: group` 语义、域说明、分组导航表、`{toctree}` 引用 chemistry/index）与 `chemistry/index.md` 分组索引（7 束导航表 + `{toctree}` 引用全部 7 束入口）。

#### Scenario: 域与组导航完整

- **WHEN** 读者从 `bundles/index.md` 总索引点击进入 science 域
- **THEN** 能经域索引 → 分组索引 → 各束 index 逐层到达每篇文档，无断链、无孤立文档

### Requirement: 七个化学经典知识包

系统 SHALL 提供 7 个 OKF 知识包，覆盖化学经典双线索：

- 西方近代化学奠基线索（化学革命逻辑链）：波义耳《怀疑的化学家》（1661，近代元素概念）→ 拉瓦锡《化学基础论》（1789，氧化学说与化学革命）→ 道尔顿《化学哲学新体系》（1808，近代原子论）→ 门捷列夫元素周期律（1869，元素周期体系）
- 中国古代经验化学线索：《周易参同契》（东汉魏伯阳，炼丹理论元典）→ 《抱朴子·内篇》（东晋葛洪，炼丹实践集大成）→ 《天工开物》（明宋应星，五金/丹青/作咸/燔石等化学工艺）

每束 SHALL 包含 `index.md`、`log.md`、`facts.md`、`insights.md` 与 `concepts/`、`examples/`、`references/` 三个子目录（各含 `index.md`）。

#### Scenario: 束结构完整

- **WHEN** 检查任意一个化学知识包目录
- **THEN** 上述文件与子目录齐全；含子目录的目录均有 `index.md` 并以 `{toctree}` 引用其全部内容文档

### Requirement: 事实零推测与信源溯源（G1）

每束 `facts.md` SHALL 包含 ≥25 条编号事实（F-xxx），事实为纯客观陈述、无因果推断词（"因为/导致/所以"等），每条事实可追溯到 `references/` 登记的信源。所有概念文档的 frontmatter SHALL 含 `sources` 字段，正文引用以脚注（`[^id]`）逐声明归因。

#### Scenario: 事实可核验

- **WHEN** 审查者从 facts.md 任取一条事实
- **THEN** 能在该束 references/ 登记的信源（公版原文或权威资料）中找到依据，无凭空虚构的人名、年代、数据、引文

### Requirement: 公版原文引用合规

原文选读 SHALL 仅引用公共领域原著（西方 1900 年前出版著作、中国古代典籍）的短篇选段，并标注出处（著作名/篇章/节）；现代解读为自撰中文综述，不得大段照抄任何现代版权译本或版权著作。

#### Scenario: 引用合规

- **WHEN** 检查 concepts/examples 中的原文引述
- **THEN** 引文均来自公版信源且有出处标注；现代语译文为自行译写并注明"今译"性质；无版权侵权风险

### Requirement: OKF v0.2 格式合规

每个非保留 .md 文件 SHALL 含可解析的 YAML frontmatter 且 `type` 字段非空；束根 `index.md` SHALL 含 `okf_version: "0.2"`；`index.md`/`log.md` 遵循保留文件约定（index 导航用途、log 按 YYYY-MM-DD 倒序）；正文中文、文件名 kebab-case 纯英文。

#### Scenario: 格式自动检查通过

- **WHEN** 运行 `invoke gates.all`
- **THEN** UTF-8 编码检查与 toctree 完整性检查全部通过

### Requirement: 链接与构建有效性

全部 Markdown 交叉引用 SHALL 使用相对路径（含 bundle 内 `/` 开头的 bundle 相对绝对路径），禁止 `file:///` 绝对路径与环境绑定路径（如 `d:\spaces`、`d:\AI` 本地路径）。新增内容 SHALL 通过 Sphinx 全量构建。

#### Scenario: 构建零警告

- **WHEN** 运行 `invoke clean && invoke build`
- **THEN** 构建成功，0 warning、0 error，无断链、无孤立文档

### Requirement: 总索引更新

`doc/bundles/index.md` SHALL 更新为 14 域 / 33 组 / 287 束（以实现时实际计数为准），新增 science 域导航小节（分组表 + 束数 + 说明）、toctree 条目、生态关系 mermaid 节点，并在推荐入门路径中体现。

#### Scenario: 总索引一致

- **WHEN** 读者打开知识包总索引
- **THEN** science 域计数、导航表、toctree、mermaid 图四处一致，且与磁盘实际束数相符

### Requirement: 阅读教程内容质量（对齐 boshu-reading 范式）

每束概念文档 SHALL 覆盖：为什么读（阅读价值）、成书背景与作者、著作结构与核心论点、关键概念的原文选读 + 逐段注释 + 现代科学对照解读、阅读方法与注本/译本选用；examples SHALL 含至少 1 篇原文段落精读实操（逐句对照演示）与 1 篇阅读路线/计划。中国典籍束 SHALL 含与现代化学的对照辨析（哪些是经验化学成就、哪些是理论局限），避免无依据的拔高或贬斥。

#### Scenario: 学习者可用

- **WHEN** 零基础读者按束 index 的快速开始路径阅读
- **THEN** 能理解该著作讲什么、为何重要、原文关键段落如何用现代科学视角解读，并知道下一步读什么

### Requirement: 方法论闭环与模式沉淀（G3）

任务 SHALL 留下 seven-concepts 方法论应用痕迹（facts/insights 工作文档入束），并沉淀"公版经典原文 + 现代解读"知识包生产模式（触发条件、核心步骤、反模式、跨学科迁移示例），供未来物理/生物等学科经典知识包复用。

#### Scenario: 模式可迁移

- **WHEN** 未来为另一学科经典（如《物种起源》《自然哲学之数学原理》）创建知识包
- **THEN** 可直接复用本次沉淀的生产模式与质量检查清单

## MODIFIED Requirements

无（本任务为全新增量；`bundles/index.md` 总索引为追加性更新，不改动既有域内容）。

## REMOVED Requirements

无。

## Constraints

- **技术约束**：OKF v0.2 frontmatter 规范；Sphinx + myst_parser 构建；文件名 kebab-case 纯英文；正文中文；相对路径链接
- **信源约束**：公版原文优先 Wikisource（en/zh）、Project Gutenberg、Internet Archive、ctext.org（中国哲学书电子化计划）；权威解读以学术共识为准（百科条目仅作线索，关键事实须多源交叉）
- **版权约束**：仅短引公版原文；现代译文自撰；不复制版权书籍内容
- **子模块约束**：不修改 awesome-okf-xs 的 .agents/ 规范与 tasks/scripts 工具链；不触碰其他域文件
- **环境约束**：网络调研通过 WebSearch/WebFetch；每个登记 URL 须在 R 阶段实测可达

## Assumptions

- 7 部著作原文均属公共领域（西方著作出版于 1661-1869 年；中国典籍为公元 2-17 世纪作品），短篇引用与自撰解读无版权障碍
- 子模块 awesome-okf-xs 已初始化且工作树干净（如存在未提交变更，实施前需先与既有变更隔离核对）
- 计数 287 = 280 + 7；若实施时总索引基线计数已变化，以实际磁盘计数为准更新
- 原子提交（C 阶段）在执行前将再次征得用户确认；提交在子模块内进行

## Acceptance Criteria

### AC-1: science 域与 chemistry 分组骨架

- **Type**: `rule`
- **Given**: 任务完成后的 `doc/bundles/science/` 目录
- **When**: 检查目录结构与索引
- **Then**: `science/index.md` 与 `science/chemistry/index.md` 存在，均含导航表与 `{toctree}`，toctree 条目覆盖全部下层入口
- **Pass Condition**: 两个索引文件存在且 toctree 引用目标全部存在
- **Evidence**: 目录列表 + `invoke gates.toctrees` 输出

### AC-2: 七个知识包结构完整

- **Type**: `rule`
- **Given**: 7 个化学经典 bundle
- **When**: 逐束检查文件清单
- **Then**: 每束含 index.md、log.md、facts.md、insights.md + concepts/index.md、examples/index.md、references/index.md；concepts ≥4 篇、examples ≥2 篇、references ≥2 篇
- **Pass Condition**: 7 束全部满足上述文件与数量要求
- **Evidence**: 逐束文件清单核对表

### AC-3: OKF frontmatter 合规

- **Type**: `rule`
- **Given**: 全部新增 .md 文件
- **When**: 检查 frontmatter
- **Then**: 每个非保留 .md 含 YAML frontmatter 且 type 非空；7 个束根 index.md 含 `okf_version: "0.2"`；log.md 按日期倒序
- **Pass Condition**: 无缺失 type 的文档；okf_version 仅出现在束根 index
- **Evidence**: frontmatter 抽查 + 构建无 frontmatter 报错

### AC-4: 事实零推测与可溯源（G1）

- **Type**: `rule`
- **Given**: 每束 facts.md
- **When**: 审查事实条目
- **Then**: 每束 ≥25 条编号事实；无因果推断词；每条事实在 references/ 信源中有依据；concepts 文档含 sources 字段与脚注归因
- **Pass Condition**: 7 束 facts 均达标，抽查事实可在登记信源中定位
- **Evidence**: facts.md 条目数统计 + V 阶段抽查记录

### AC-5: 公版引用与版权合规

- **Type**: `rule`
- **Given**: 全部原文引述内容
- **When**: 检查引文来源与长度
- **Then**: 引文均出自公版原著并标注出处；现代解读为自撰；无大段照抄现代版权文本
- **Pass Condition**: 每处引文可对应 references 中登记的公版信源；无版权风险内容
- **Evidence**: 引文-信源对照表

### AC-6: 链接规范无断链

- **Type**: `rule`
- **Given**: 全部新增 Markdown 链接
- **When**: 扫描链接形式与目标
- **Then**: 全部为相对路径；无 file:/// 前缀；无 d:\ 等环境绑定绝对路径；无断链
- **Pass Condition**: 链接扫描 0 违规；`invoke gates.toctrees` 通过
- **Evidence**: 链接扫描结果 + gates 输出

### AC-7: 质量门与构建通过

- **Type**: `rule`
- **Given**: 全部产出物落盘
- **When**: 运行 `invoke gates.all` 与 `invoke clean && invoke build`
- **Then**: UTF-8 检查通过、toctree 检查通过、Sphinx 构建 0 warning 0 error
- **Pass Condition**: 两条命令均成功退出
- **Evidence**: 命令输出日志

### AC-8: 总索引一致更新

- **Type**: `rule`
- **Given**: 更新后的 `doc/bundles/index.md`
- **When**: 核对计数与导航
- **Then**: 域/组/束计数与磁盘实际一致；science 域小节、toctree 条目、mermaid 节点齐全且四处一致
- **Pass Condition**: 计数一致 + 三处导航元素齐全
- **Evidence**: 总索引片段 + 磁盘计数核对

### AC-9: 独立对抗审查（V 阶段）

- **Type**: `rule`
- **Given**: 全部知识包初稿完成
- **When**: 由 fresh context 独立审查员执行 V 阶段
- **Then**: 每束 ≥5 条关键事实回源核验；输出结构化审查报告（pass/fail/blocked）；所有 actionable 发现已转为修复任务并闭环
- **Pass Condition**: 审查报告结果为 pass（或 fail 后修复至新一轮 pass）
- **Evidence**: review.md 审查记录 + 修复闭环证据

### AC-10: 内容质量与教程可用性

- **Type**: `rubric`
- **Dimension**: 原文选读准确性、现代解读科学性、中西对照知识地图、阅读路径可用性
- **Scale**: 1-5
- **Anchors**: 1 = 事实错误多/解读误导/无法自学；3 = 主线正确但有少量疏漏或解读笼统；5 = 事实准确、解读深入、对照有洞见、零基础可按路径自学
- **Pass Threshold**: >= 4
- **Evidence**: V 阶段审查员评分与逐束评语

### AC-11: 生产模式可迁移（G3）

- **Type**: `rubric`
- **Dimension**: "公版经典原文+现代解读"生产模式的完整性与可迁移性
- **Scale**: 1-5
- **Anchors**: 1 = 无模式沉淀；3 = 有步骤清单但缺反模式与迁移示例；5 = 含触发条件、核心步骤、信源策略、反模式、跨学科迁移示例，可直接复用于下一学科
- **Pass Threshold**: >= 4
- **Evidence**: 模式沉淀文档（specs 工作区留档）

## Open Questions

- 无（四项关键决策已经用户确认：中西双线索 / 原文+解读形态 / science 新域 / 多 bundle 规模）
