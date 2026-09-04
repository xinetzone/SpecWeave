---
title: "养生经典 OKF Wiki 教程"
status: "draft"
---

# 养生经典 OKF Wiki 教程 Spec

## Why

用户要求全面系统地调研和整理养生相关著作的原文与解读，并以 OKF 知识包形式沉淀到 `projects/awesome-okf-xs/doc/bundles` 的恰当位置，形成可发布、可导航的 wiki 教程。该内容属公开古典文献（Public 级），适用标准工作流；方法论上属于 seven-concepts 场景 4「知识沉淀」（R→I→E 链路）。

## What Changes

* 在 `doc/bundles/think/` 下新增「养生经典」分组目录 `yangsheng/`（与 `psi/`、`laozi/` 平级），含分组 `index.md`

* 新增核心知识包 `yangsheng/yangsheng-classics-reading/`，结构对齐 `laozi/boshu-reading` 范本：

  * 根 `index.md`（frontmatter + 快速导航 + 定位 + 学习路径 + toctree）

  * `facts.md`（零推测事实清单，G1 门）

  * `insights.md`（架构洞察，G2 门：现象+根因+影响+建议）

  * `concepts/`（6-7 篇概念文档 + `index.md`）

  * `examples/`（2-3 篇实操指南 + `index.md`）

  * `references/`（3-4 篇信源登记 + `index.md`）

* 更新导航链：`think/index.md`（域分组表 + toctree）、`doc/bundles/index.md`（域统计与条目）、必要时 `think` 域描述文案

* 全部 Markdown 遵循 OKF v0.2 frontmatter 规范（`type` 必填；`sources`/`generated`/`verified`/`status`/`stale_after` 齐备）

* 通过质量门：`python scripts/check-toctrees.py`（零断链/零孤立）+ `python scripts/check-utf8.py`

## 内容范围（调研对象）

核心经典（必覆盖）：

1. 《黄帝内经》（《素问》+《灵枢》）——中医养生理论源头（法于阴阳、和于术数、食饮有节、起居有常）
2. 《养生论》（嵇康）——文人养生论奠基之作
3. 《千金要方》养性篇（孙思邈）——医家养生集成
4. 《遵生八笺》（高濂）——明代养生百科全书
5. 《老老恒言》（曹庭栋）——老年养生专书
6. 《寿亲养老新书》（陈直/邹铉）——养老尊老专书

扩展脉络（按调研深度取舍，写入 references 或 concepts）：

* 食养类：《食疗本草》（孟诜）、《饮膳正要》（忽思慧）

* 导引类：马王堆《导引图》、《云笈七签》导引法、八段锦/易筋经文献源流

* 道教养生：《黄庭经》、《悟真篇》节选

解读维度：原文要义选读、版本与源流、历史注家立场、现代研究视角、阅读路径设计。

## Impact

* Affected specs：无既有 spec 依赖

* Affected code：

  * `projects/awesome-okf-xs/doc/bundles/think/`（新增 yangsheng 分组 + 更新域 index）

  * `projects/awesome-okf-xs/doc/bundles/index.md`（更新统计与导航）

* 非代码影响：子模块内文件变更，最终需在子模块内原子提交（用户确认后执行）

## ADDED Requirements

### Requirement: 养生经典分组落地

`doc/bundles/think/yangsheng/` SHALL 存在分组 `index.md`，以 toctree 引用其下全部知识包 index，并更新 `think/index.md` 域导航表。

#### Scenario: 分组导航完整

* **WHEN** 运行 `python scripts/check-toctrees.py`

* **THEN** 零断链、零孤立文档，新分组可从 `think/index.md` 到达

### Requirement: 核心知识包结构合规

`yangsheng-classics-reading` 知识包 SHALL 包含根 `index.md`、`facts.md`、`insights.md`、`concepts/`（含 index）、`examples/`（含 index）、`references/`（含 index），全部文件携带合规 OKF v0.2 frontmatter（`type` 必填 + 溯源/信任/生命周期字段）。

#### Scenario: 结构与范本一致

* **WHEN** 对照 `laozi/boshu-reading` 检查目录结构与 frontmatter 字段

* **THEN** 目录层级、toctree 链、frontmatter 字段族齐备且格式一致

### Requirement: 事实与信源可溯源

`facts.md` SHALL 仅记录零推测客观事实（G1：无因果词）；每篇内容文档 SHALL 通过 frontmatter `sources` 字段标注信源；参考文献页 SHALL 登记权威版本与整理本（含出处类型：传世本/出土文献/现代整理本）。

#### Scenario: 抽查事实无因果推断

* **WHEN** 审查 `facts.md` 全部条目

* **THEN** 无「因为/导致/所以」类因果推断词，均为可核查的客观陈述

### Requirement: 教程可用性

概念文档 SHALL 覆盖：总览与阅读价值、核心经典逐部要义（≥5 部）、养生思想谱系（医家/道家/文人/食养/导引）、如何选读注本；示例文档 SHALL 包含至少 1 篇原文选读对照与 1 篇阅读计划；内容面向普通读者，中文行文，文件名 kebab-case 纯英文。

#### Scenario: 零基础读者可按路径入门

* **WHEN** 读者从根 index「快速开始」进入

* **THEN** 能按推荐路径依次阅读概念→示例，并到达对应参考文献

### Requirement: 质量门与编码合规

全部新增/修改文件 SHALL 通过 `check-toctrees.py` 与 `check-utf8.py`；UTF-8 无 BOM；导航统计（bundle 数量、分组数）更新准确。

#### Scenario: 门禁通过

* **WHEN** 在 awesome-okf-xs 根目录运行两个检查脚本

* **THEN** 退出码均为 0

## MODIFIED Requirements

无既有需求修改。

## REMOVED Requirements

无。

## Constraints / Assumptions / Open Questions

* 约束：不修改子模块构建配置（conf.py 等）；不使用 `file:///` 绝对路径交叉引用；`invoke` 不可用，验证以脚本直跑为准

* 假设：调研信源以 Web 公开权威资料（原著整理本、学术论文、百科条目）为主；本地无养生类藏书目录（`playground/books` 仅有道德经资料）

* 开放问题：是否需要拆分为多个 bundle（如「内经专包」）——初版按单 bundle + 概念分篇承载，规模超限再拆

