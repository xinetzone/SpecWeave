---
type: Reference
id: "<bundle-id>"
title: "<中文标题：对象 + 研究角度>"
category: "tech"
tags:
  - <tag1>
  - <tag2>
date: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
status: "verified"
author: "SpecWeave Agent（方法论编排 session sc-YYYYMMDD-<topic>）"
summary: "以七概念方法论（R→I→E→V→C，standard）<做了什么>：采集 <N> 条带来源客观事实（<前缀>-001~<前缀>-NNN，覆盖 <时间/范围>），形成 <N> 条四元组洞察与 <N> 个可迁移模式（<模式名>，<成熟度>）。知识包按问题域拆为 <N> 个概念页，附信源台账与对抗审查记录。"
security_level: "public"
knowledge_type: "conditional"
validation_status: "verified"
reuse_count: "0"
integrity: "unchecked"
source: "<一手信源列举与采集日期；引用本地包时写明文件名与冻结时点；完整 URL 见 references/source-inventory.md>"
---

# <中文标题>

> 模板使用说明：本文件复制到知识包根目录后另存为 `index.md`；下方"页面 → 路径"形式的是示例链接，填实时改写成 Markdown 链接 `[页面](路径)` 并替换全部 `<...>` 占位符。

> 一句话摘要：<30—80 字，回答"这是什么、最反直觉的结论是什么"；所有结论可回溯到事实编号与信源台账。>

- **编排 session**：`sc-YYYYMMDD-<topic>`
- **场景与链路**：场景 4 知识沉淀，`R→I→E→V→C（入库）`，depth=standard
- **采集时点**：YYYY-MM-DD（动态数据为该时点快照）
- **信源分工**（如适用）：<主调研侧事实编号 X-001~X-NNN，来源 [S01]~[SNN]；对照侧以锚点引用既有本地包，不重复采集>

---

## 0. 快速导航：按你的问题出发

| 我想…… | 去读哪一篇（填实时改写为 Markdown 链接） |
|---|---|
| <一分钟看清……> | 00 <画像页> → `concepts/00-overview.md` |
| <决策/选型/行动> | 05 <决策页> → `concepts/05-selection-guide.md` |
| 核查每条事实的出处 | 信源台账 → `references/source-inventory.md` |
| 了解结论经受了哪些攻击与修正 | V 对抗审查记录 → `references/adversarial-review.md` |

---

## 1. R 阶段：客观事实清单（<前缀>-001 ~ <前缀>-NNN）

> G1 已通过：全部为可验证客观陈述，无"因为/所以/导致/从而"等因果推断词；数字、日期、URL 按信源原文记录并标注时点；口径不同或互相矛盾的数据显式并列。来源键 [Sxx] 对应信源台账 `references/source-inventory.md`。

### 1.1 A 组：<组名>（X-001 ~ X-NNN）

| 编号 | 事实 | 来源 |
|---|---|---|
| X-001 | <客观陈述；数字带时点与口径；URL 完整> | [S01] |
| X-002 | <……> | [S02][S03] |

> ⚠️ 规模/份额/性能数字前的口径提示块：标明统计对象、发布方、原始/转引层级，提示禁止跨口径比较。

### 1.N <跨包引用锚点（可选）>

| 锚点 | 事实 | 引用位置 |
|---|---|---|
| K-001 | <对方包事实一句话> | 兄弟包文件 → `../<sibling-bundle>/references/<file>.md`（references/ 子页引用兄弟包时层数为 ../../） |

---

## 2. I 阶段：核心洞察（四元组）

> G2 已通过：每条含 **陈述 / 证据（编号）/ 反常识 / 行动**，各维度互不重叠。

### I-1　<洞察标题>

- **陈述**：<结论本身>
- **证据**：X-001/X-005（<各证据支撑什么>）
- **反常识**：<直觉判断是什么、证据为何推翻它>
- **行动**：<可执行的清单/评估问题/核查动作>

---

## 3. E 阶段：可迁移模式（G3）

### 模式：<4—8 字模式名>（L1-draft / L1 / L2）

**一句话**：<定义>

| 要素 | 内容 |
|---|---|
| **适用于** | <触发场景> |
| **不适用于** | <边界> |
| **核心步骤** | ① …… ② ……（3—7 步） |
| **检验标准** | <可判定通过的条件> |
| **反模式** | ① ……（≥3 条） |
| **跨域迁移** | ≥1 个其他领域的用法 |
| **成熟度** | L1-draft/L1/L2 + 案例数与升级条件 |

> 完整操作版见决策页 `concepts/05-selection-guide.md`。模式默认只在本包内维护；用户明确要求入库时再独立化到 docs/retrospective/patterns/ 并双向加链。

---

## 4. V 阶段：4 视角对抗审查

> 完整问题清单、裁定与回归确认见 V 审查记录 `references/adversarial-review.md`。V 门结论：4 视角全覆盖、意见 N 条（≥5）、采纳 N 条（≥2），**通过/不通过**。<一句话列出主要修正>

---

## 5. 质量门与编排记录

| 门 | 标准 | 结果 |
|---|---|---|
| G1 | 事实 ≥20、无因果词、可溯源、数字/URL 完整、口径差异显式标注 | PASS（N 条，<分组情况>） |
| G2 | 洞察 ≥3 且四元组完整、维度独立、含反常识与行动 | PASS（I-1~I-N） |
| G3 | 模式含适用边界、步骤、≥3 反模式、检验、跨域迁移、成熟度 | PASS（<模式名>，<成熟度>） |
| V 门 | 4 视角、意见 ≥5、采纳 ≥2 并回归确认 | PASS（N 条意见，N 条关闭） |
| G4 | 原子文件、可独立验证、命名与链接规范、toctree 登记 | PASS（N 个文件；脚本校验通过） |

**局限声明**：① <信源结构偏差>；② <未取证/未实测项>；③ <时点性与失效条件>；④ <复查触发器>。

```
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-YYYYMMDD-<topic> | msg=方法论编排开始：<简述> | ctx={"scenario":"knowledge","topic":"<topic>","depth":"standard"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S2 | event=CHAIN_SELECTED | session=sc-YYYYMMDD-<topic> | msg=知识沉淀链路R→I→E→V→C | ctx={"chain":"R-I-E-V-C","depth":"standard"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=G1 | event=GATE_PASSED | session=sc-YYYYMMDD-<topic> | msg=<N条事实，无因果词> | ctx={"facts":"X-001~X-NNN"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S99 | event=CHAIN_COMPLETED | session=sc-YYYYMMDD-<topic> | msg=<事实/洞察/模式/V意见/文件数摘要> | ctx={"gates":["G1","G2","G3","V","G4"],"deliverable":"docs/knowledge/<域>/<bundle-id>/"}
```

```{toctree}
:maxdepth: 1
:hidden:

concepts/00-overview
concepts/01-<question>
references/source-inventory
references/adversarial-review
```
