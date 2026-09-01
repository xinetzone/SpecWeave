---
id: "daojia-canon-okf-wiki-retrospective-20260901"
title: "道家著作全谱系 OKF Wiki（daojia-canon-okf-wiki）里程碑复盘"
date: "2026-09-01"
completion_date: "2026-09-01"
type: "Report"
description: "以七概念方法论 R→I→E→V→C 对道家著作全谱系 OKF 知识包从调研到 P0/P1/P2 三批次十九束全部建成流程复盘：P2 九束 126 文件、frontmatter 统一 60 处、V 阶段修正断链/编号/计数、gates.all 五面一致 347/69/15、双仓原子提交。萃取两条可迁移模式（谱系计数口径与两仓门控重建/共享索引原子提交竞态防护）。"
status: "stable"
source:
  - ".trae/specs/daojia-canon-okf-wiki/"
  - "projects/awesome-okf-xs/doc/bundles/think/daojia/"
milestone-name: "daojia-canon-okf-wiki（道家著作全谱系 OKF 知识包）"
time-range: "2026-08-30 ~ 2026-09-01"
methodology: "七概念方法论（R→I→E→V→C 链路，里程碑复盘场景 + daojia-canon-okf-wiki 规格）"
quality-gates:
  G1: "facts.md 编号事实纯客观无因果词 ✅（P0/P1/P2 各束 facts 零推断）"
  G2: "洞察四元组完整 ✅（insights.md 现象/根因/影响/建议）"
  G3: "判读模式 ≥3 落地 ✅（托名三层判读/双源逐字核读/传本谱系重建）"
  V: "四视角对抗审查 + 独立评审 ✅（断链/F编号/R键/计数/frontmatter 修正）"
  G4: "原子提交 ✅（子模块 3a52c2f4 + 主仓 d788c50de，暂存集核验零夹带）"
tags: ["里程碑复盘", "七概念", "OKF", "知识包", "道家", "诸子", "玄学", "道教", "frontmatter", "原子提交"]
generated:
  by: "process:seven-concepts-cmd"
  at: "2026-09-01T19:00:00+08:00"
verified:
  by: "process:seven-concepts-v"
  at: "2026-09-01T19:30:00+08:00"
stale_after: "2027-09-01"
---

<!-- meta_type: retrospective -->

# 道家著作全谱系 OKF Wiki（daojia-canon-okf-wiki）里程碑复盘

> **方法论编排**：七概念 R→I→E→V→C 链路（里程碑复盘场景）
> **复盘对象**：`.trae/specs/daojia-canon-okf-wiki/` → `projects/awesome-okf-xs/doc/bundles/think/daojia/`
> **session**：sc-20260831-daojia-p2
> **拖动日期**：2026-09-01（P2 九束子模块提交 3a52c2f4、主仓 gitlink d788c50de，未推送）

---

## 一、交付规模总览

| 维度 | 值 |
|------|----|
| 规格目录 | `.trae/specs/daojia-canon-okf-wiki/`（spec/tasks/checklist/insights/patterns/structure-proposal/facts） |
| Bundle 根目录 | `projects/awesome-okf-xs/doc/bundles/think/daojia/` |
| 归属 | think 域 · daojia 分组（四段谱系伞形导航） |
| 四段结构 | zhuzi（先秦诸子）/ huanglao（黄老之学）/ xuanxue（魏晋玄学注疏）/ daojiao（道教经典） |
| 建成束数 | **19 束**（P0 三束 + P1 七束 + P2 九束，每束 14 文件 = 266 + 索引文件） |
| P2 新增文件 | 9 束 × 14 = 126 文件 + 6 索引改动 |
| frontmatter 统一 | 子内容页补 60 处（type: Concept/Example/Reference/Index） |
| 权威性分级 | A/B/C 三级（出土＋传世双印证 / 传世为主 / 辑佚·托名争议） |
| V 阶段修正 | 断链 2 + F 编号 15 + R 键 2 + log 计数 1 + frontmatter 统一决策 |
| 质量门 | gates.all 全绿：UTF-8（7039 文件）+ toctree + bundles 索引五面一致（15 域/69 组/347 束） |
| 提交 | 子模块 `3a52c2f4`（132 文件 +7668/−15）+ 主仓 `d788c50de`（gitlink 1 文件） |

---

## 二、R 阶段：客观事实清单

| # | 事实 |
|---|------|
| F-001 | 本 spec 创建于 2026-08-30，change-id `daojia-canon-okf-wiki`，方法论 seven-concepts 场景4（知识沉淀），内容敏感度 Public |
| F-002 | 用户确认范围＝全谱系通览（先秦诸子→黄老之学→魏晋玄学注疏→道教经典四段谱系），落位统一 `think/daojia/` 分组 |
| F-003 | Phase 0 产出四段谱系调研清单 facts.md，逐部登记书名/托名作者/推定年代/版本体系/核心思想/权威底本注本/信源 URL/托名层与文本层标注 |
| F-004 | 权威性分级定义确立：A＝出土＋传世双重印证且整理本权威；B＝传世本为主、整理本权威或文本有争议；C＝辑佚/残本/托名争议大 |
| F-005 | 「托名层/文本层」分判成为全分组贯穿口径；有争议处并列 ≥2 种学说，不单一断言 |
| F-006 | Phase 1 确认点向用户呈现全谱系清单+结构建议+优先级，经确认后逐册入库 |
| F-007 | P0 三束建成：淮南子、黄帝四经（马王堆帛书）、抱朴子内篇 |
| F-008 | P1 七束建成：列子、文子、鹖冠子、管子四篇、河上公章句、严遵指归、太平经 |
| F-009 | P2 九束建成：关尹子、尹文子、慎到田骈、王弼、郭象、成玄英、参同契、黄庭经、清静经 |
| F-010 | 老子、庄子、阴符经以 cross-ref 纳入既有独立分组（laozi/zhuangzi/huangdi），daojia 不重复建设 |
| F-011 | 计数口径确立：门控束数只计组内直接子目录，嵌套束不改变总索引计数（daojia 恒记 4 束） |
| F-012 | 索引同步更新：think/daojia 总纲 + 四段 index（zhuzi/huanglao/xuanxue/daojiao） + think/index.md + bundles/index.md |
| F-013 | bundle 计数维持 347 束/69 组/15 域不变（daojia 记 4 束，嵌套束不入顶层计数） |
| F-014 | V 阶段对 P2 九束四视角对抗审查，成玄英束发现 2 处 zhuangzi 断链（相对路径层级错误） |
| F-015 | F 编号错配：qingjingjing 束 15 处编号与引文不对应，就地修正 |
| F-016 | R 键错配：huangtingjing 束 2 处 R4→R7，link 目标修正 |
| F-017 | log 计数错配：ember 计数 13→14，与事实登记对齐 |
| F-018 | frontmatter 统一决策：用户裁决统一为「带 frontmatter」，子代理为 6 束（wangbi/guoxiang/chengxuanying/guanyinzi/yinwenzi/shendao-tianpian）子内容页补 60 个 frontmatter |
| F-019 | 既有 P1 模板束（heshanggong/huainanzi/liezi）子页无 frontmatter，为已知历史不一致，本次未动（只对新九束统一） |
| F-020 | frontmatter 补全后 gates.all 回归全绿（15 域/69 组/347 束五面一致），frontmatter 兜底扫描 fm_check 0 问题 |
| F-021 | 子模块原子提交 3a52c2f4（132 文件、+7668/−15），add 与 commit 分两次调用、中间核对暂存集（132 文件全部限于 daojia 段，零夹带） |
| F-022 | 主仓提交 d788c50de（gitlink bump 至 3a52c2f4），提交后子模块 clean、主仓 HEAD 置位 |
| F-023 | 未推送（按既定推送闸门：待并行会话 zhouyi 束补齐使 check-toctrees 门通过后统一推送） |

---

## 三、I 阶段：洞察（四元组）

### I-1：谱系任务的门控计数必须"以其为准重算"，任何一方的数字（含远端）都不得手填采信
- **陈述**：共享索引的分组/束/域计数，若凭"觉得加了几个"手填，必然与目录树实际漂移。
- **证据**：F-013/F-020——计数以 gates.all 门控重算为准，五面一致（frontmatter/计数行/节标题/分组表/toctree），无手填数字。
- **反常识**："计数看起来对"往往掩盖索引与目录树的隐性错位；只有门控重算能逐面还原自洽。
- **行动**：任何新增/合并束后必跑 `invoke gates.bundles` 三角校验 + `gates.toctrees` 断链检查，以门控输出为唯一裁决口径。

### I-2：frontmatter 的"统一"是用户决策，但必须与既有批次的历史不一致显式隔离
- **陈述**：当用户裁决把本批次统一为带 frontmatter，而既有 P1 模板束无 frontmatter 时，正确做法是"只统一新批次 + 如实记录历史不一致"，而非顺手改动既有束。
- **证据**：F-018/F-019——60 处 frontmatter 仅补入新 6 束，P1 模板束原样保留并标注为已知历史不一致。
- **反常识**：一致性审查直觉是"把新老都统一"；但改动既有已发布束会扩大变更面、引入夹带风险。
- **行动**：跨批次格式统一前先判定"历史欠债 vs 本次增量"，只在本批次收敛；历史不一致单独立项，不并入增量提交。

### I-3：共享仓库的 git 写操作必须拆步 + 核验暂存集，杜绝"一链式"夹带他方文件
- **陈述**：awesome-okf-xs 存在并行会话写共享索引，`git add` 与 `git commit` 若在同一条链式命令一气呵成，他方新 add 的文件会被自己的提交带走。
- **证据**：F-021——P2 本次 add 与 commit 分两次工具调用，中间单独 `git diff --cached --name-only` 核对暂存集为 132 文件且全部限于 daojia 段。
- **反常识**："add 完立刻 commit"看似高效，实则是共享工作区竞态的主要触发点。
- **行动**：add 与 commit 分两次调用 + 中间核对暂存集清单；发现非己方文件则不提交、停下报告交他方处置。

---

## 四、E 阶段：可迁移模式

### 模式 1：谱系计数门控重建（Lineage-Count Gate Rebuild）
- **触发**：共享知识库/文档库在新增或合并分组、束后的计数对账。
- **适用**：有 frontmatter 计数 + 计数行 + 节标题 + 分组表 + toctree 五面索引的文档体系；多会话并发写共享索引。
- **不适用**：纯新增、无计数/索引约定的独立文件。
- **核心步骤**：①以目录树实测为准（不采信任何一方含远端的数字）→ ②跑 `invoke gates.bundles` 三角校验（束/组/域）→ ③跑 `invoke gates.toctrees` 断链/孤立检查 → ④逐面核对 frontmatter/计数行/节标题/分组表/toctree 一致 → ⑤门控全绿方提交。
- **反模式**：①凭"加了几束"手填计数；②采信远端 origin 的 frontmatter 数字；③只跑一门忽略断链；④合并后不重跑门控。
- **检验**：gates.all 退出码 0 + 五面数字逐面一致 + 断链零残留。
- **迁移**：可迁移到任意"分类树 + 全局索引 + 多作者并发"的文档/代码资产治理。

### 模式 2：共享索引原子提交竞态防护（Shared-Index Atomic Commit Guard）
- **触发**：在存在并行会话的 git 汇合仓库（submodule / monorepo 共享子目录）中执行提交。
- **适用**：多个会话同时 add/commit 同一索引树；文档库高频迭代。
- **不适用**：单用户独占、无并发写风险的仓库。
- **核心步骤**：①add 与 commit 分两次工具调用 → ②中间单独 `git diff --cached --name-only` 核对暂存集 → ③确认暂存集 = 本方目标文件集合（精确匹配）→ ④`git commit -F`（UTF-8 -F 防中文乱码）→ ⑤commit 后 `git status` 验证用户区与暂存区净空。
- **反模式**：①`git add <A>; git commit` 链式一气呵成；②提交后不核对导致混入他方文件；③加 commit 都在一条命令里无法回头。
- **检验**：暂存集清单与目标集合精确一致；他人文件零混入；commit 后工作区无本方残余。
- **迁移**：可迁移到任何共享子模块、并行 CI 写同一索引、团队共用 worktree 的提交流程。

---

## 五、V 阶段：对抗审查记录

（审查意见全文见 `.trae/specs/daojia-canon-okf-wiki/` V 记录；以下为本复盘产出自身的四视角审查）

| 视角 | 攻击点 | 处置 |
|------|--------|------|
| 🔴 魔鬼代言人 | I-1「不采信任何一方数字」是否过激（本地已知自家数字准确） | 保守措辞保留：远端曾漏登 3 行导致 frontmatter/正文自相矛盾，只有门控重算可靠；保留 |
| 🟢 新人视角 | 模式 2「精确匹配暂存集」如何落地 | 已补措辞：用 `git diff --cached --name-only` 输出与目标文件集合做精确集合比较；采纳 |
| 🟠 老板视角 | 复盘是否值得与 P2 提交分离存档 | 沿既有先例（concepts/milestone/ 系列）独立归档至 .agents docs，成本低可复用；保留 |
| 🔵 未来视角 | 19 束建成后 daojia 是否已完结、有无潜在补充束 | 已在结论注明：十九束全建成属当前 spec 交付完整；道教段广度边界（义理/丹道 5 部，不含善书科仪）为待续探索点；采纳 |

---

## 六、C 阶段：原子提交

- **子模块（awesome-okf-xs）**：`3a52c2f4` `feat(daojia): 道家段P2九束建成并统一frontmatter`（132 文件 +7668/−15）
- **主仓（SpecWeave）**：`d788c50de` `chore(submodules): bump awesome-okf-xs 至道家段P2九束建成(3a52c2f4)`（gitlink 1 文件）
- 提交前预检：`invoke gates.all` 全绿 + frontmatter 兜底扫描 fm_check 0 问题；add 与 commit 分次调用、暂存集精确核验零夹带
- 本复盘报告独立归档至 `.agents/docs/retrospective/reports/concepts/milestone/`（单文件、单一职责）

---

## 七、已知边界与后续

- **推送闸门**：符合 memory 既有决定（hetu-luoshu 束待并行 zhouyi 束补齐 5 篇缺失文件使 check-toctrees 门通过后再推送），故本次未 push。
- **frontmatter 历史欠债**：P1 模板束（河上公/淮南子/列子）子页无 frontmatter 为既有历史不一致，已显式隔离不动，待独立立项处理。
- **道教段广度边界**：daojiao 现行仅限义理/丹道经典 5 部（参同契/抱朴子/太平经/黄庭经/清静经），不含善书（太上感应篇）与科仪类，为待续探索点。
- **dealte 闭环**：V 阶段 4 项实质修正（断链/F编号/R键/计数）均就地闭环，无未处理 actionable finding。