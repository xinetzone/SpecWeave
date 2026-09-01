# 《医心方》阅读教程 OKF Wiki Spec

## Why

用户要求使用 seven-concepts-cmd 全面系统地调研和整理《医心方》相关著作的原文与解读，并以 OKF 知识包形式沉淀到 `projects/awesome-okf-xs/doc/bundles` 的恰当位置，形成可发布、可导航的 wiki 教程。《医心方》（日本·丹波康赖，984 年）是日本现存最古老的医方书，以分类汇编方式征引中国隋唐以前医籍 200 余种，其中大量典籍早已亡佚（含《素女经》《洞玄子》《小品方》等），是辑佚学、唐以前医学史与中日医学交流史的核心文献。内容属公开古典文献（Public 级），适用标准工作流；方法论上属于 seven-concepts 场景 4「知识沉淀」（R→I→E 链路，辅以 V 对抗审查与 C 原子提交）。

## What Changes

* 在 `doc/bundles/think/` 下新增「医学经典」分组目录 `medicine/`（与 `yangsheng/`、`sexology/`、`classics/` 平级），含分组 `index.md`

* 新增核心知识包 `medicine/ishinpo-reading/`，结构对齐 `yangsheng/yangsheng-classics-reading` 与 `laozi/boshu-reading` 范本：

  * 根 `index.md`（frontmatter + 快速导航 + 定位 + 学习路径 + toctree）

  * `facts.md`（零推测事实清单，G1 门）

  * `insights.md`（架构洞察，G2 门：现象+根因+影响+建议四元组）

  * `concepts/`（6-8 篇概念文档 + `index.md`）

  * `examples/`（2-3 篇实操指南 + `index.md`）

  * `references/`（3-4 篇信源登记 + `index.md`）

  * `log.md`（工作日志）

* 更新导航链：`think/index.md`（域分组表 + toctree + 域描述文案）、`doc/bundles/index.md`（域统计与条目）

* 建立与既有知识包的交叉引用：`sexology/classics-reading` 中「《医心方》辑佚」相关内容与新包互链（仅追加链接，不改写既有内容）

* 全部 Markdown 遵循 OKF v0.2 frontmatter 规范（`type` 必填；`sources`/`generated`/`verified`/`status`/`stale_after` 齐备）

* 通过质量门：`python scripts/check-toctrees.py`（新包范围零断链/零孤立）+ `python scripts/check-utf8.py`（退出码 0）

## 内容范围（调研对象）

核心对象（必覆盖）：

1. 《医心方》本体——丹波康赖生平与家学、成书与奏进年代（永和/永观年间）、三十卷分类结构、征引书目与辑佚价值
2. 亡佚引书重点——房中/养生类（《素女经》《洞玄子》《玉房秘诀》《玉房指要》）、医方类（《小品方》《深师方》《范汪方》《集验方》《经心录》等）、养生服食类引文
3. 版本与流传——古写本系统（半井家本/御物本等）、江户刊本（安政本）、清末回传中国的路径、中国现代整理本（人民卫生出版社影印本、中医古籍整理本等）
4. 研究史与解读——日本考证学派（丹波家族后续医家、森立之等）、中国辑佚学家的利用（《玉函山房辑佚书》等系统）、现代中日医学交流史研究视角

扩展脉络（按调研深度取舍，写入 references 或 concepts）：

* 丹波家族医籍脉络（《医略抄》等后世相关著作）

* 平安时代医学制度与《大同类聚方》等同时代背景

* 《医心方》与《千金要方》《外台秘要》等中国类书型医籍的体例比较

解读维度：原文要义选读（养生卷/房中卷辑佚文）、版本源流、辑佚方法、历史研究立场、阅读路径设计。

## Impact

* Affected specs：无既有 spec 依赖（`create-sexology-classics-wiki` 已完成，仅追加交叉链接不改其内容）

* Affected code：

  * `projects/awesome-okf-xs/doc/bundles/think/`（新增 medicine 分组 + 更新域 index）

  * `projects/awesome-okf-xs/doc/bundles/index.md`（更新统计与导航）

  * `projects/awesome-okf-xs/doc/bundles/think/sexology/classics-reading/`（仅追加指向新包的交叉引用链接）

* 非代码影响：子模块内文件变更，最终需在子模块内原子提交（用户确认后执行）

## ADDED Requirements

### Requirement: 医学经典分组落地

`doc/bundles/think/medicine/` SHALL 存在分组 `index.md`，以 toctree 引用其下全部知识包 index，并更新 `think/index.md` 域导航表与域描述。

#### Scenario: 分组导航完整

* **WHEN** 运行 `python scripts/check-toctrees.py`

* **THEN** medicine 范围零断链、零孤立文档，新分组可从 `think/index.md` 到达

### Requirement: 核心知识包结构合规

`ishinpo-reading` 知识包 SHALL 包含根 `index.md`、`facts.md`、`insights.md`、`concepts/`（含 index）、`examples/`（含 index）、`references/`（含 index）、`log.md`，全部文件携带合规 OKF v0.2 frontmatter（`type` 必填 + 溯源/信任/生命周期字段）。

#### Scenario: 结构与范本一致

* **WHEN** 对照 `yangsheng/yangsheng-classics-reading` 检查目录结构与 frontmatter 字段

* **THEN** 目录层级、toctree 链、frontmatter 字段族齐备且格式一致

### Requirement: 事实与信源可溯源

`facts.md` SHALL 仅记录零推测客观事实（G1：无因果词）；每篇内容文档 SHALL 通过 frontmatter `sources` 字段标注信源；参考文献页 SHALL 登记写本/刊本/现代整理本与研究文献（含出处类型：古写本/刊本/影印本/现代整理本/研究论著）。

#### Scenario: 抽查事实无因果推断

* **WHEN** 审查 `facts.md` 全部条目

* **THEN** 无「因为/导致/所以」类因果推断词，均为可核查的客观陈述

### Requirement: 教程可用性

概念文档 SHALL 覆盖：总览与阅读价值、《医心方》成书与结构、亡佚引书与辑佚价值（房中/养生/医方分类）、版本源流与回传史、研究史与解读立场、如何选读整理本；示例文档 SHALL 包含至少 1 篇原文（辑佚文）选读对照与 1 篇阅读计划；内容面向普通读者，中文行文，文件名 kebab-case 纯英文。

#### Scenario: 零基础读者可按路径入门

* **WHEN** 读者从根 index「快速开始」进入

* **THEN** 能按推荐路径依次阅读概念→示例，并到达对应参考文献

### Requirement: 交叉引用不破坏既有包

对 `sexology/classics-reading` 的修改 SHALL 仅限追加指向新包的相对路径链接，不删改既有文字；追加后该包 toctree 与既有内部链接保持零断链。

#### Scenario: 既有包回归通过

* **WHEN** 对 `sexology/classics-reading` 范围运行链接与 toctree 检查

* **THEN** 无新增断链，既有内容无差异（除追加链接行）

### Requirement: 质量门与编码合规

全部新增/修改文件 SHALL 通过 `check-utf8.py`（退出码 0）；`check-toctrees.py` 在 medicine 新包范围零问题；UTF-8 无 BOM；导航统计（bundle 数量、分组数）更新准确。

#### Scenario: 门禁通过

* **WHEN** 在 awesome-okf-xs 根目录运行两个检查脚本

* **THEN** `check-utf8.py` 退出码 0；`check-toctrees.py` 输出中 medicine 范围零问题（全库其他范围若存在其他并行会话引入的问题，按规范不干预）

## MODIFIED Requirements

无既有需求修改。

## REMOVED Requirements

无。

## Constraints / Assumptions / Open Questions

* 约束：不修改子模块构建配置（conf.py 等）；不使用 `file:///` 绝对路径交叉引用；验证以脚本直跑为准；调研中间产物存放 `.temp/` 并在任务完成后清理

* 假设：调研信源以 Web 公开权威资料（影印本信息、学术论文、百科条目、图书馆著录）为主；《医心方》原文选读以公开影印/整理本的辑佚文为限，不转载受版权保护的现代点校全文

* 开放问题：房中类辑佚文与既有 `sexology` 包的边界划分——本包聚焦《医心方》文献学视角（辑佚/版本），性学内容解读仍归 sexology 包，两包互链不重复展开

