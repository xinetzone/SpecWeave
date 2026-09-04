---
type: checklist
spec: fangzhong-okf-wiki
title: 房中典籍 OKF wiki 教程 — 验收检查清单
created: 2026-08-30
---

# 验收检查清单（Checklist）

> Review 阶段逐项核验；rule 项为客观判定（pass/fail），rubric 项 0-5 分且 ≥4 通过。
> 工作目录：`projects/awesome-okf-xs`（子模块）；束路径：`doc/bundles/think/fangzhong/`。

## rule 项

- [ ] **R1 结构完整**：`doc/bundles/think/fangzhong/fangzhong-reading/` 含 index.md、facts.md、insights.md、log.md；concepts/ 含 index + 00-08 共 9 篇；examples/ 含 index + 01-03 共 3 篇；references/ 含 index + 01-04 共 4 篇；分组页 `think/fangzhong/index.md` 存在。
- [ ] **R2 frontmatter**：每个非保留 .md 有含非空 type 的 YAML frontmatter；束根 type: OKF + okf_version: "0.2" + version/source/generated/verified/status/stale_after；分组页 type: group；子页 type 为 Concept/Example/Reference。
- [ ] **R3 toctree**：束根收 concepts/index、examples/index、references/index、facts、insights、log；三个子 index 完整收录本目录全部内容；分组页收 fangzhong-reading/index。
- [ ] **R4 索引计数**：think/index.md 含 fangzhong 表格行与 toctree 条目（且保留 daoyi/buddhism 等他组注册行）；bundles/index.md 提交版=HEAD 基线+fangzhong（frontmatter total_bundles/groups 各 +1、domains 不变；正文计数句同步；think 节束/组计数与分组表含 fangzhong；两处 mermaid think 标签含 fangzhong）；不含他会话 tcm 等 WIP 内容。
- [ ] **R5 质量门**：WIP 隔离态下 `python scripts/check-toctrees.py` 退出码 0、`python scripts/check-utf8.py` 退出码 0、`invoke build` 构建成功。
- [ ] **R6 信源矩阵**：FR-2 所列全部核心文献（《汉志·方技略》、马王堆《十问》《合阴阳》《天下至道谈》、《医心方》卷28、《双梅景闇丛书》辑本、《素问·上古天真论》、《千金要方》卷27、《三元延寿参赞书》、《抱朴子内篇》、《大乐赋》P.2539）每部 ≥1 个已核验 https 全文/图像 URL；无 zysj.com.cn 域；平台缺陷（OCR/未校/卷次差异）有注明。
- [ ] **R7 辨伪分层**：托名层（素女/玄女/彭祖/容成/务成子/冲和子）显式标注；《素女经》等辑本标注"佚文辑本、非《汉志》著录原书"并说明辑出来源（医心方卷28/叶辑本）；内丹双修清修/阴阳两说并陈代表学者；现代白话演绎本与地摊"采补"读物有低权威警示条。
- [ ] **R8 学术边界声明**：束根 index.md（及示例页）含显式声明——文化史/医学史/宗教史/文献学研究用途，不构成性教育、医学或两性行为指导。
- [ ] **R9 链接与命名**：交叉引用全为相对路径、无 file:///；正文中文；新增文件名 kebab-case 英文+数字前缀；UTF-8 无 BOM。
- [ ] **R10 facts 质量**：条数 ≥100；无因果推断词（因为/导致/因此/所以/使得/从而等）；每条含可溯源信息（学者/书名/出版社/年份/ISBN/URL/卷次）；未证实信息（汉志小序卷数差、玉房秘诀撰者、高罗佩中译本版次、待核 ISBN）标"待考"或不写。
- [ ] **R11 原子提交**：子模块内提交，暂存清单恰为 fangzhong 新文件 + think/fangzhong/index.md + think/index.md + bundles/index.md；不含 daoyi 暂存文件、mozi 改动、tcm/buddhism/confucian/guiguzi/huangdi-neijing 目录；Conventional Commits 中文 subject；主仓 git 状态无变更（gitlink 不动）。
- [ ] **R12 WIP 还原**：6 个隔离目录（tcm、think/buddhism、think/confucian、think/guiguzi、think/huangdi-neijing、think/daoyi）原样还原至 doc/bundles/ 原位，文件数与 T0 记录一致；daoyi 23 文件恢复为已暂存(A)；bundles/index.md 恢复为他会话 WIP 版(M)；mozi 两文件仍为(M)。
- [ ] **R13 内容边界**：束内无露骨性行为操作性段落、无色情文学正文、无春宫/秘戏图像、无"还精补脑/采阴补阳"类功效背书表述；《素女经》《洞玄子》《房内》仅作文献学与学术史介绍，引文以目录学/养生原则/方法论概述为限。

## rubric 项（0-5，≥4 通过）

- [ ] **Q1 信源权威性与可核验性**（5=每部核心文献同时给出权威纸本整理本与已核验在线 URL、平台按识典＞维基文库＞ctext＞diancang/IDP 分级；3=多数有但分级不清；0=无信源或不可核验）：___/5
- [ ] **Q2 托名/辑佚/争议处理诚实度**（5=托名、辑佚层累、双修诠释争议全部标注年代证据与学界分歧，低权威读物显式警示，未证实说法不写入；0=真伪不辨、把辑本当原典）：___/5
- [ ] **Q3 零基础可执行性**（5=三档路径每步给出具体书名+链接+时间计划；0=仅文献清单罗列）：___/5
- [ ] **Q4 六层覆盖完整性**（5=目录著录/出土/辑佚/医家/道教/文学与现代学术六层均有概念文档且层间交叉引用；0=缺层或层间无联系）：___/5
- [ ] **Q5 原文真实性与边界得体**（5=精选段落逐字与权威本一致、篇卷出处确切、配全文链接，且选段均为学术/养生/目录学内容、无露骨段落；0=仅转述无原文，或原文错漏，或越界收录）：___/5

## V 阶段对抗审查记录

- URL 抽查（≥6，覆盖识典/维基文库/ctext/diancang/IDP）：______
- 原文逐字比对（≥3 段，注明出处篇卷与比对来源）：______
- 辑本/托名/双修两说/低权威警示核查：______
- 内容边界核查（R13：无露骨段落/无色情正文/无图像/无功效背书）：______
- 链接与命名核查（相对路径/file:///、kebab-case、frontmatter）：______
- 结论：pass / fail（fail 项回填修复）：______
