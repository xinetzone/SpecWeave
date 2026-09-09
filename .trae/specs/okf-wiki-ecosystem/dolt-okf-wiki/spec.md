---
title: "Spec：Dolt 博文 → OKF 知识包"
status: "draft"
---

# Dolt 博文 → OKF 知识包 - 产品需求文档（PRD）

## Overview

- **Summary**：将微信公众号「开源日记」博文《数据库也能像 Git 一样进行 fork、branch 和 merge 吗？》（https://mp.weixin.qq.com/s/ES_KncqKLiQxIzaEZ-58gg ）转化为 OKF v0.2 知识包（bundle），归属 `jishu/data/` 分组，bundle 名 `dolt`。博文介绍 Dolt——从存储层原生支持 Git 式版本控制的 SQL 数据库（行级历史、分支/合并、MySQL 协议兼容、DoltHub/DoltLab/Hosted Dolt 产品矩阵、MCP Server 与 AI Agent 安全操作等）。
- **Purpose**：按 blog-article-to-okf-wiki 七阶段工作流（敏感度预检→骨架判定→归属决策→F 编号事实采集+P0 权威核验→三层知识拆分→信源先行生成 bundle→对抗审查与索引收尾），把单篇博文中的事实、观点与洞察沉淀为可溯源、带时效管理的可信知识库条目；以 seven-concepts-cmd 方法论编排（场景 4 知识沉淀：R→I→E→V→C）串联质量门 G1-G4。
- **Target Users**：技术学习者、数据库工程师、数据分析师、AI 应用开发者、技术管理者；以及 OKF 文档库的后续读者与智能体。

## Goals

- G1：完整、忠实地提取博文全部事实性声明（产品名、版本、数字、日期、功能、命令、限制），F 编号登记双份一致
- G2：对 P0 级声明（GitHub Stars、开源协议、TPC-C 性能数据、数据量阈值、端口/兼容性、产品矩阵、MCP Server 等）逐项做官方权威交叉核验，产出勘误四张清单
- G3：按操作可复现性两问决定骨架（是否设 examples/），按主线实体优先原则落位 `jishu/data/dolt/`
- G4：三层知识拆分（发布事实层→机制原理层→边界与趋势层），事实与作者观点显式分层
- G5：信源先行生成 bundle（references/ → concepts/ → 各级 index），frontmatter 符合 OKF v0.2 + 子项目 Sphinx 构建规范
- G6：V 阶段四视角对抗审查 + 8 项机械门禁全过，三级索引（组/域/总）接入且计数同步
- G7：C 阶段原子提交（子模块→主仓库 spec→子模块指针），Conventional Commits、不 push

## Non-Goals

- 不安装、部署或实测 Dolt（无本地运行验证；命令类内容仅在官方文档可溯源时引用）
- 不阅读 Dolt 存储引擎源码（prolly tree 等机制仅依据官方文档/博文，标注信源层级）
- 不做 Dolt 与 Liquibase/Flyway/Neon/其他版本化数据方案的 exhaustive 对比（仅在博文或官方源涉及时呈现）
- 不翻译博文全文；不保留营销叙事原文
- 不为单篇博文新建顶级分组
- 不生成配图（除非 E 阶段判定确有必要；默认无图）

## Background & Context

- 博文信源：微信公众号「开源日记」，属第三方综述/开源项目介绍类（信源距离③），含作者转述的官方数据
- 历史上下文：本会话此前已对同一博文做过网页学习分析（spec 见 `.trae/specs/retrospectives-insights/web-content-analysis/spec.md`），但当时提取的 article.md 已不在工作区；本任务重新提取并以 OKF 规范产出
- 目标库：`projects/awesome-okf-xs`（git submodule），OKF v0.2，Sphinx + myst_parser 构建；子项目 AGENTS.md 路由与 frontmatter 规范已读取
- 归属先例：`jishu/data/` 分组现有 `pydata/` 子组（9 束 Python 数据科学生态库），分组定位明确包含"高性能数据存储"；Dolt 为版本化 SQL 数据库（数据存储设施），主线实体落此分组；`dolt/` 为组内直挂束（与 pydata 子组同级），不构成新建分组
- 幂等检查：全库 Grep `dolt|Dolt` 无命中，目标 bundle 与 spec 目录均不存在，属全新创建
- 微信反爬：`mp.weixin.qq.com` 对 WebFetch 确定性拦截（13/13），R 阶段直接使用 browser_use 子代理提取 `#js_content` innerText

## Functional Requirements

- **FR-1（R·信源获取）**：用 browser_use 提取博文全文（含标题、公众号、发布时间、正文、代码块），保存为 spec 工作区原文；正文长度异常（<500 字）时判定取错节点并重取
- **FR-2（R·事实登记）**：F-001 起编号登记全部事实性声明至 spec `facts.md`；作者观点显式标注"作者观点"；数字/版本/日期/产品名/命令/成效数字一条不漏
- **FR-3（R·信源距离预判）**：对每条声明标注信源距离（①官方发布/②一手实测/③第三方综述/厂商自宣）；厂商/作者自述的成效数字默认 P0
- **FR-4（R·P0 核验）**：P0 声明逐项 WebSearch/官方源（github.com/dolthub/dolt、docs.doltdb.com、dolthub.com 官方博客等）核验，过勘误四张清单：①日期/版本表 ②成效数字溯源表 ③口径对照表 ④引文逐字核对表；核验补充事实续编 F 编号
- **FR-5（R·勘误管理）**：源文错误不静默照搬——新增 F 编号记录正确值与差异；核心声明核验失败 → bundle `status: flagged` + verification.md 顶部明示 + index 已知边界；非核心失败可 stable 但勘误完整；无法核验标"仅博文单源"，禁止硬编 URL
- **FR-6（I·骨架判定）**：回答操作可复现性两问（①有读者可照做的安装/配置/代码/调用流程？②经作者实测、有版本/输入输出/步骤顺序？），两问皆"是"才设 `examples/`；判定结论与理由写入 facts.md/spec
- **FR-7（I·三层拆分）**：发布事实层（What/Who/定位/产品矩阵/数据）→ concepts 首篇；机制原理层（Why/How：行级版本、分支合并、MySQL 兼容、MCP/AI 工作流）→ 中部；边界与趋势层（性能限制、适用场景、行业趋势、选型启示）→ 尾篇；作者洞察与事实分层呈现
- **FR-8（E·信源先行）**：先写 `references/article-source.md`（F 编号双份登记）与 `references/verification.md`（核验报告+勘误），再写 concepts/，各级 index.md 与 log.md 最后写
- **FR-9（E·正文规范）**：所有具体声明引用 F 编号或权威信源；伪代码/推导显著标注"非官方"；frontmatter 含 okf_version（仅根 index）/type/title/description/tags/generated/verified/status/stale_after/sources（博文+核验权威双信源）；中文正文、kebab-case 英文文件名
- **FR-10（V·机械门禁）**：UTF-8 strict roundtrip、双份 F 编号集合一致且连续、三级 toctree 完整且条目文件存在、相对链接全可达且无 `file:///`、三级计数同步、敏感路径零残留、frontmatter 完整、勘误在正文落实
- **FR-11（V·索引接入）**：更新 `jishu/data/index.md`（导航表+toctree+束数）、`jishu/index.md`（data 行束数）、`bundles/index.md`（total_bundles/域束数/组束数/正文计数）；计数先读现值再 +1；优先跑 `invoke gates.toctrees`/`gates.bundles`/`gates.utf8`，依赖不可用时执行手动等效清单并在 log.md 注明
- **FR-12（C·原子提交）**：用 `.agents/scripts/git-commit-utf8.py` 显式文件列表提交；顺序①子模块（bundle+组/域/总 index）②主仓库 spec ③主仓库子模块指针；不 push

## Non-Functional Requirements

- **NFR-1（可溯源）**：正文任何数字/版本/产品声明均可回溯到 F 编号或 sources URL；无信源转述零容忍
- **NFR-2（时效管理）**：设 `stale_after`（产品资讯类至 2026 年末，即 2026-12-31）；价格/版本/Stars 等时点值在正文标注时点
- **NFR-3（结构合规）**：通过子项目 toctree/bundles/utf8 三质量门（或手动等效验证），Sphinx 可构建不断链
- **NFR-4（可读性）**：中文表达流畅，表格/列表/Mermaid（如需要）组织清晰；概念文档单篇聚焦、长度适中
- **NFR-5（观点分层）**：作者观点、核验事实、编辑者洞察三类内容可区分，不把观点固化为"官方结论"

## Constraints

- **Technical**：微信反爬必须 browser_use；WebSearch 需能访问官方源；不运行 Dolt；Windows 环境（UTF-8 strict 编码检查用 PowerShell）
- **Business**：产出归入 awesome-okf-xs 子模块公共知识库；公开内容标准工作流
- **Dependencies**：browser_use 子代理（博文提取）、WebSearch（P0 核验）、子模块 invoke gates（可选，缺失时手动等效）、`.agents/scripts/git-commit-utf8.py`
- **Methodology**：seven-concepts-cmd 场景 4 链路 R→I→E→V→C；G1（事实无因果词）/G2（洞察四元组）/G3（模式/结构可迁移）/G4（行动项原子化）质量门逐道记录

## Assumptions

- 博文为公开可访问内容（无 token/邀请码），敏感度级别 Public
- 博文中的性能数据（如 TPC-C 为 MySQL 54%、数据量阈值等）为作者转述官方/社区口径，须以官方源复核；若官方源无对应口径，标"仅博文单源"
- 读者具备基础 SQL/MySQL 与 Git 概念
- 初步预判骨架为"技术综述/产品介绍"（index + concepts/ + references/ + log，不设 examples/）；最终以 R 阶段读到的博文实测内容为准（两问判据）

## Acceptance Criteria

### AC-1：bundle 结构完整（rule）

- **Type**：`rule`
- **Given**：E 阶段完成
- **When**：检查 `projects/awesome-okf-xs/doc/bundles/jishu/data/dolt/`
- **Then**：存在 index.md（含 okf_version frontmatter + toctree）、log.md、concepts/index.md（含 toctree）+ 概念文档、references/index.md（含 toctree）+ article-source.md + verification.md；examples/ 仅在两问皆"是"时存在
- **Pass Condition**：上述文件/目录全部存在，且每个非保留 .md 含可解析 frontmatter 与非空 type
- **Evidence**：目录清单 + 各文件 frontmatter 摘录

### AC-2：双份 F 编号一致（rule）

- **Type**：`rule`
- **Given**：R 与 E 阶段完成
- **When**：正则 `^\|\s*F-(\d{3})\s*\|` 分别提取 spec `facts.md` 与 bundle `references/article-source.md` 的编号集合
- **Then**：两集合相等、编号连续无跳号（跳号须有显式注记）；V 阶段补充事实若不回转须在 log.md 注记原因
- **Pass Condition**：集合比对输出一致
- **Evidence**：正则提取结果与比对记录

### AC-3：P0 声明逐项核验（rule）

- **Type**：`rule`
- **Given**：R 阶段完成
- **When**：审查 verification.md
- **Then**：全部 P0 声明（Stars/协议/性能数字/阈值/端口/产品矩阵/MCP Server/日期版本）逐项有 ✅/⚠️/❌ 结论、核验信源 URL 与勘误四清单记录；无硬编 URL（每个官方 URL 经 WebSearch 实际访问确认）
- **Pass Condition**：P0 项 100% 覆盖核验；❌ 项按 FR-5 管理（flagged 或勘误落实）
- **Evidence**：verification.md 核验表 + WebSearch 结果摘录

### AC-4：正文无 facts 之外的编造（rule）

- **Type**：`rule`
- **Given**：E 阶段完成
- **When**：逐篇审查 concepts/ 与 index.md
- **Then**：所有数字/版本/产品名/API/命令均带 F 编号或 sources 脚注；作者观点与编辑者洞察有显式分层标注；伪代码/推导标注"非官方"
- **Pass Condition**：抽查无 F 外事实声明
- **Evidence**：正文 F 编号引用清单与 facts.md 交叉核对

### AC-5：三级 toctree 与索引计数（rule）

- **Type**：`rule`
- **Given**：V 阶段完成
- **When**：检查 dolt/index.md、concepts/index.md、references/index.md（及 examples/index.md 如有）的 toctree 块，及 data/index.md、jishu/index.md、bundles/index.md
- **Then**：每个 toctree 条目（排除 `:` 指令行）对应文件存在；组/域/总索引计数先读现值再 +1 且三处同步；`invoke gates.toctrees`/`gates.bundles` 通过，或手动等效验证逐项完成并在 log.md 注明
- **Pass Condition**：gates 通过或手动清单 8 项全勾；计数无手工估算
- **Evidence**：gates 输出或手动验证记录 + 索引 diff

### AC-6：链接/编码/敏感信息机械门禁（rule）

- **Type**：`rule`
- **Given**：V 阶段完成
- **When**：Grep 全部新增/修改 .md
- **Then**：相对链接逐一 Test-Path 可达；`file:///` 零出现；`C:\Users\`/家目录绝对路径零出现；UTF-8 strict 解码无乱码（PowerShell `[System.Text.UTF8Encoding]::new($false,$false)`）
- **Pass Condition**：全部检查通过
- **Evidence**：检查命令与输出记录

### AC-7：骨架判定与 examples 取舍一致（rule）

- **Type**：`rule`
- **Given**：I 阶段完成
- **When**：核对两问答案与 bundle 结构
- **Then**：两问皆"是"→ examples/ 存在且命令均可溯源官方文档；任一"否"→ 无 examples/ 且根 index description 标注"非操作教程"（或等价说明）
- **Pass Condition**：结构与判定一致，判定理由有记录
- **Evidence**：facts.md/spec 中两问答案记录

### AC-8：勘误落实与时效管理（rule）

- **Type**：`rule`
- **Given**：V 阶段完成
- **When**：核对 verification.md ❌/⚠️ 项与正文
- **Then**：正文呈现正确值（非源文错误数字）并标注源文口径；flagged bundle（如有）顶部明示；所有内容文档含 stale_after（2026-12-31 或更短）与时点标注
- **Pass Condition**：无错误数字静默留存
- **Evidence**：verification.md 勘误节与正文对照

### AC-9：原子提交合规（rule）

- **Type**：`rule`
- **Given**：C 阶段完成
- **When**：检查 git log 与状态
- **Then**：子模块内先提交（bundle+索引，显式文件列表，Conventional Commits），主仓库提交 spec，主仓库更新子模块指针；工作区无遗留未提交的相关变更；未 push
- **Pass Condition**：三条提交记录存在且顺序正确，`git status` 干净
- **Evidence**：`git log --oneline` 两仓库输出

### AC-10：知识拆分与洞察质量（rubric）

- **Type**：`rubric`
- **Dimension**：知识组织与洞察深度
- **Scale**：1-5
- **Anchors**：1 = 博文复述/观点当事实/结构混乱；3 = 事实完整但三层分层模糊、洞察仅复述原文；5 = 事实/机制/趋势三层清晰，事实与观点显式分离，趋势与选型启示有分析增量（如 Git 理念向数据领域延伸、AI Agent 数据操作沙箱、版本化数据库生态定位）
- **Pass Threshold**：>= 4
- **Evidence**：concepts/ 三篇以上文档评审

### AC-11：读者可用性（rubric）

- **Type**：`rubric`
- **Dimension**：中文表达与导航体验
- **Scale**：1-5
- **Anchors**：1 = 大面积机翻/断链/无导航；3 = 可读但表格/导航/信源标注不齐；5 = 表达流畅、表格列表得当、根 index 导航完整、信源与时效边界一目了然
- **Pass Threshold**：>= 4
- **Evidence**：bundle 根 index 与 concepts 文档通读

## Open Questions

- [ ] 博文是否包含作者一手实测（安装/运行/版本/输出）？——决定 examples/ 取舍（R 阶段回答）
- [ ] 博文所述 TPC-C 性能数据（约 MySQL 54%）与数据量阈值能否在官方源找到对应口径？——决定 ✅/⚠️/❌
- [ ] 博文提及的 Dolt MCP Server 是否为官方发布组件？官方仓库/文档口径为何？
- [ ] 博文发布时点与 GitHub Stars 实时数差异如何标注（时点值 vs 现值）？
