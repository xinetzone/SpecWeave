---
type: checklist
spec: daoyi-okf-wiki
title: 道医 OKF wiki 教程 — 验收检查清单
created: 2026-08-30
---

# 验收检查清单（Checklist）

> Review 阶段逐项核验；rule 项为客观判定（pass/fail），rubric 项 0-5 分且 ≥4 通过。

## rule 项

- [ ] **R1 结构完整**：`doc/bundles/think/daoyi/daoyi-reading/` 含 index.md、facts.md、insights.md、log.md；concepts/ 含 index + 00-08 共 9 篇；examples/ 含 index + 01-03 共 3 篇；references/ 含 index + 01-04 共 4 篇；分组页 `think/daoyi/index.md` 存在。
- [ ] **R2 frontmatter**：每个非保留 .md 有含非空 type 的 YAML frontmatter；束根 type: OKF + okf_version: "0.2"；分组页 type: group；子页 type 为 Concept/Example/Reference。
- [ ] **R3 toctree**：束根收 concepts/index、examples/index、references/index、facts、insights、log；三个子 index 完整收录本目录全部内容；分组页收 daoyi-reading/index。
- [ ] **R4 索引计数**：think/index.md 含 daoyi 行与 toctree；bundles/index.md frontmatter 为 287/33/13，正文同步，think 节"6 束 · 3 组"，两处 mermaid think 标签含 daoyi。
- [ ] **R5 质量门**：WIP 隔离态下 check-toctrees.py 退出码 0、check-utf8.py 退出码 0、invoke build 成功。
- [ ] **R6 信源矩阵**：FR-2 清单中每部经典 ≥1 个 https 已核验全文 URL；无 zysj.com.cn；平台缺陷（diancang 卷次/维基伤寒论未校/ctext 本草 OCR）有注明。
- [ ] **R7 辨伪两说**：中藏经、辅行诀、医道还元、扁鹊心书、华佗神医秘传五书均两说并陈（年代证据+双方代表论著）；祝守明《道医讲义》、王爱品《道医论》有低权威警示。
- [ ] **R8 非医疗声明**：束根 index.md 含显式非医疗用途声明。
- [ ] **R9 链接与命名**：交叉引用全为相对路径、无 file:///；正文中文；新增文件名 kebab-case 英文+数字前缀。
- [ ] **R10 facts 质量**：无因果推断词；每条可溯源；未证实信息标"待考"或不写。
- [ ] **R11 原子提交**：子模块内提交，暂存清单仅 daoyi 新文件 + think/index.md + bundles/index.md；Conventional Commits 中文 subject；主仓 git 无变更。
- [ ] **R12 WIP 还原**：5 个未跟踪目录原样还原至 doc/bundles/ 原位，git status 仍为未跟踪、文件数一致。

## rubric 项（0-5，≥4 通过）

- [ ] **Q1 信源权威性与可核验性**（纸本点校本+在线 URL 双轨、平台分级）：___/5
- [ ] **Q2 真伪与争议诚实度**（托名/辑佚/扶乩/伪书全标注、低权威警示、未证实不写入）：___/5
- [ ] **Q3 零基础可执行性**（三档路径、具体书名+链接+计划）：___/5
- [ ] **Q4 六层覆盖完整性**（元典根源/道门医家/道藏养生内丹/出土方技/医道流派/现代研究，层间互链）：___/5
- [ ] **Q5 原文真实性**（精选段落逐字与权威本一致、篇卷出处确切、配全文链接）：___/5

## V 阶段对抗审查记录

- URL 抽查（≥6，覆盖识典/维基/ctext/diancang/homeinmists）：______
- 原文逐字比对（≥3 段）：______
- 争议两说核查：______
- 结论：pass / fail（fail 项回填修复）：______