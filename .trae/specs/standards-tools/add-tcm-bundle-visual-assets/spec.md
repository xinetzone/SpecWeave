---
title: "为 tcm 域生成配图与 Mermaid 图表 — 产品需求文档"
status: "draft"
---

***

type: Spec
title: "为 tcm（中医经典与理论）域生成配图与 Mermaid 图表"
status: pending-approval
created: 2026-09-02
methodology: seven-concepts（场景5 创新突破：R → F → 生产 → V → C）
target: projects/awesome-okf-xs/doc/bundles/yixue/tcm/
------------------------------------------------------

# 为 tcm 域生成配图与 Mermaid 图表 — 产品需求文档

## Overview

- **Summary**：为 OKF 知识包库 `yixue/tcm`（中医经典与理论）域的 1 个分组、5 个知识包（tcm-overview / nanjing / shanghan-zabinglun / shennong-bencaojing / waijing-weiyan，共 60 篇内容文档）从零建立视觉资产体系：以 Seedream AI 生图提供意象性封面/氛围配图（6–10 张），以 Mermaid 提供事实性结构图表（12–18 张），并通过 Sphinx 构建、质量门与对抗审查验证。

- **Purpose**：tcm 域当前 60 篇文档纯文字、零视觉资产，典籍谱系、成书时序、六经框架、三品分类、辑本源流等高度结构化的知识仅以表格/ prose 呈现，读者建立全景坐标的成本高；中医典籍主题也缺少文化意象层面的阅读氛围。视觉资产用于：① 一图胜千言地呈现谱系/时序/分层/框架；② 提供与典籍主题契合的素雅阅读氛围。

- **Target Users**：tcm 域的五类读者（零基础爱好者、临床从业者/中医院校学生、文献学研究者、AI 智能体/知识库构建者、专题兴趣读者），以及通过 Read the Docs 阅读在线文档的所有用户。

## Goals

- G1：为 tcm 域级入口与 5 个束入口各提供 1 张统一风格的意象性封面配图（共 6 张），并按内容需要增补 0–4 张章节意象图，**总量 ≤ 10 张**。

- G2：为 5 个束的高信息密度页面提供 12–18 张 Mermaid 事实图表（谱系/时序/分层/框架/流程/关系），每束 2–4 张。

- G3：全部视觉资产通过 Sphinx 构建（`invoke build` 无新增警告）、OKF 质量门（`invoke gates.all` 全绿，束/组/域计数不变）与 Mermaid 安全编码六规则检查。

- G4：通过 V 阶段对抗审查：Mermaid 图表事实与正文一致、配图不违反医疗免责与文献诚实边界、引用路径全部可达。

- G5：变更可追溯：更新域 `changelog.md` 与各束 `log.md`。

## Non-Goals (Out of Scope)

- ❌ 不新增、不删改、不重写任何正文知识内容（视觉资产是**增强**，插图位置的衔接文字除外，但不得改变事实表述）。

- ❌ 不生成任何**精确医学图解**：经络穴位图、脏腑解剖图、舌诊/脉诊图、人体部位图、方药植物"鉴真式"图谱一律禁止（AI 生图无法保证医学准确性，违反"非医疗建议"边界与"不构拟"原则）。

- ❌ 不为 60 篇文档逐篇配图（"适度"原则：单页视觉资产 ≤ 2 个，references/ 簿录层与存目索引页不配图）。

- ❌ 不修改 Sphinx 配置、不引入新扩展、不改变 OKF frontmatter 规范。

- ❌ 不自动执行 git commit（按全局规则，仅交付变更集与原子提交建议；子模块存在并行会话竞态，提交由用户决定）。

- ❌ 不处理 think 域《黄帝内经》教程（交叉引用对象，非本域资产）。

## Background & Context

- **目标域结构**：`doc/bundles/yixue/tcm/` 含域级文档（index.md / guide.md / changelog.md）与 `classics/` 分组，分组下 5 束：

  - `tcm-overview`：典籍谱系三层分层、四大经典导读、版本学常识（异文五分法）、托名五问法、书目分级、3 个阅读模式；

  - `nanjing`：81 难结构、独取寸口、成书五说、吕广/杨玄操/滑寿/徐大椿注家谱系；

  - `shanghan-zabinglun`：成书流变、四版本系统、六经辨证框架、398 条索引、金匮 25 篇存目；

  - `shennong-bencaojing`：四辑本系统（卢复/孙星衍/顾观光/森立之）、三品分类、序录 13 句、363 药存目；

  - `waijing-weiyan`：著录/托名/文本三层分离、九卷八十一篇、命门水火、颠倒顺逆、1697→1980 流传时序。

- **图片先例**（全库唯一先例）：`doc/_static/bundles/yishu/vocal/meitong-yanyin-pedagogy/images/` 存图，Markdown 以 `![alt 文本](/_static/bundles/yishu/vocal/meitong-yanyin-pedagogy/images/xxx.png)` 引用（站点根绝对路径）。

- **Mermaid 先例与支持**：`doc/conf.py` 已启用 `sphinxcontrib.mermaid`（mermaid 11.4.1 CDN 运行时渲染，`myst_fence_as_directive = ["mermaid"]`），全库 bundles 已有 127 处 mermaid 代码块先例。

- **Mermaid 安全编码六规则**（development-standards.md §Mermaid 编码规范）：①代码块内禁空行；②非纯英文标签双引号包裹；③禁 Markdown 列表触发格式（`数字. `     、`- `      开头）；④换行用 `<br/>` 禁 `\n`；⑤subgraph 用 `subgraph ID ["标题"]` 格式；⑥边标签用 `-->|"标签"|` 格式。根目录 `check_mermaid.py` 可自动检测。

- **七概念方法论映射**：R（逐束勘察视觉缺口与事实依据）→ F（第一性原理推导视觉分工，见下）→ 生产（生图 + Mermaid 编写）→ V（对抗审查：事实一致性/医疗边界/构建验证）→ C（changelog/log 收尾 + 提交建议）。

### F（第一性原理）推导：视觉资产的本质分工

| 维度        | Mermaid（事实性视觉）                            | Seedream AI 生图（意象性视觉）                               |
| --------- | ----------------------------------------- | --------------------------------------------------- |
| 承载内容      | 谱系、时序、分层、框架、流程、关系——**可核验的事实结构**           | 封面、氛围、文化意象——**不承载可证伪信息**                            |
| 准确性来源     | 由文档事实逐节点核对，错了可定位可修                        | AI 生成不可核验，故不得承载事实                                   |
| tcm 域典型题材 | 典籍谱系三层图、成书时序、六经传变框架、三品分类、辑本系统、三层分离考辨、注家谱系 | 古籍书影意象、书案笔墨、山水草木、传统纹样、水墨氛围                          |
| 硬禁忌       | 节点文本不得构拟正文没有的事实                           | 禁人体/经络/穴位/脏腑/舌脉/药草鉴真；**画面不得出现文字**（AI 汉字不可靠，杜绝伪古籍文字） |

- **配图统一风格**：中国传统水墨/工笔淡彩，暖纸色（米白/暖灰）基调，素雅含蓄，无文字、无人物特写、无精确医学内容；横向构图适合页面顶部。

- **图片存放**：域级图 → `doc/_static/bundles/yixue/tcm/images/`；束级图 → `doc/_static/bundles/yixue/tcm/classics/<bundle>/images/`；引用一律 `![alt](/_static/bundles/yixue/tcm/...)`。

- **插入位置**：封面图置于束根 `index.md` 简介段之后（域级置于 `index.md` 域介绍之后）；Mermaid 置于对应概念页的相关章节内，图前有一句引导语、图后有事实说明，不孤立堆放。

## Functional Requirements

- **FR-1（R 勘察清单）**：逐束通读 60 篇文档的结构与关键事实，产出《视觉资产清单》：每张 Mermaid 的目标文件、插入章节、图表类型、承载的事实要点（须能在正文中找到依据）；每张配图的文件名、存放路径、生图 prompt 草案、alt 文本、插入位置。

- **FR-2（配图生成）**：使用 Seedream（GenerateImage 工具）按清单生成 6–10 张配图，保存至 `_static` 对应目录，文件名 kebab-case 英文。

- **FR-3（Mermaid 编写）**：按清单编写 12–18 张 Mermaid，内嵌于目标 .md 的 \`\`\`mermaid 代码块，严格遵循安全编码六规则；图中节点/标签的事实表述与正文一致（成书年代诸说并列处不得在图中武断取一）。

- **FR-4（引用插入）**：按先例格式插入图片引用与 Mermaid，衔接文字自然，不破坏现有 toctree 与 frontmatter。

- **FR-5（V 验证）**：`invoke build` 零新增警告；`invoke gates.all` 全绿；`check_mermaid.py` 通过；逐图核对事实一致性与边界合规；图片文件全部存在且引用路径可达。

- **FR-6（C 收尾）**：更新 tcm 域 `changelog.md`（新增 v1.2.0 视觉资产条目）与 5 束 `log.md`；产出变更集核对报告与原子提交建议（不自动提交）。

## Non-Functional Requirements

- **NFR-1（事实诚实）**：Mermaid 中每条事实可在同束正文中定位依据；成书/托名/辑复诸说并列处，图表同样并列呈现，不作裁决。

- **NFR-2（医疗合规）**：不出现任何可被误读为诊疗指导的视觉内容；配图 alt 与周边文字不得削弱现有免责声明。

- **NFR-3（适度性）**：配图 6–10 张、Mermaid 12–18 张；单页视觉资产 ≤ 2 个；references/ 簿录层与存目索引页不插入视觉资产。

- **NFR-4（构建兼容）**：新增图片为 PNG/JPG，单张 ≤ 2MB；Mermaid 在 mermaid 11.4.1 渲染器下可渲染；Sphinx 构建无警告。

- **NFR-5（风格一致）**：全部配图共享统一风格基调（水墨淡彩/暖纸色/无文字），视觉上属于同一套系。

## Constraints

- **Technical**：产出物在 git submodule `projects/awesome-okf-xs/` 内（子项目自治，遵循其 AGENTS.md 与 OKF v0.2 规范）；图片生成本地文件入 `doc/_static/`（Sphinx 工程要求，与 vocal 束先例一致）；正文中文、文件名 kebab-case 英文；Mermaid 遵循六规则。

- **Business**：内容为公开古籍文献（Public 敏感度，标准工作流）；医学免责声明不可弱化。

- **Dependencies**：Seedream 生图能力（GenerateImage）；Sphinx + sphinxcontrib-mermaid 已配置；`invoke build` / `invoke gates.all` 任务可用；子模块工作树可能存在并行会话改动——仅触碰 tcm 域与 `_static/bundles/yixue/tcm/` 路径。

## Assumptions

- A1：`invoke build` / `invoke gates.all` 在当前环境可运行（子模块 tasks/ 提供；若环境缺依赖，以 `sphinx-build` 与 `scripts/check-toctrees.py`、`check-bundles-index.py` 直接运行兜底）。

- A2：Mermaid 事实图表优先于配图；若配额冲突，保 Mermaid、压缩配图数量。

- A3：配图不承载事实，故 V 阶段对配图只做"边界合规 + 风格一致 + 路径可达"审查，不做"事实核对"。

- A4：封面图置于束根 index.md 不影响 toctree 解析（图片引用非 toctree 条目，先例已验证）。

## Acceptance Criteria

### AC-1：配图资产完整且引用可达

- **Given**：视觉资产实施完成

- **When**：检查 `doc/_static/bundles/yixue/tcm/` 与各束 `images/` 目录

- **Then**：清单中每张配图文件真实存在（6–10 张，kebab-case 命名，单张 ≤2MB），且每个 Markdown 图片引用路径在构建产物中可解析（无断链）

- **Verification**：`programmatic`

### AC-2：Mermaid 安全编码与渲染

- **Given**：全部 Mermaid 已写入文档

- **When**：运行 `check_mermaid.py` 与 `invoke build`

- **Then**：六规则检查通过（无空行/无列表触发/无 `\n`/引号与 subgraph 格式正确），Sphinx 构建无 mermaid 相关警告或错误

- **Verification**：`programmatic`

### AC-3：Mermaid 事实与正文一致

- **Given**：V 阶段对抗审查

- **When**：审查者逐张核对 Mermaid 节点/边/分组与同束正文

- **Then**：图中无正文不存在的事实、无武断裁决（诸说并列处保持并列）、无因果曲解；发现问题逐条修复

- **Verification**：`human-judgment`（对抗审查子代理黑盒执行，rubric：节点事实可溯源率 100%）

### AC-4：医疗与文献诚实边界

- **Given**：全部视觉资产

- **When**：审查配图内容与图表题材

- **Then**：无经络/穴位/脏腑/舌脉/人体/药草鉴真类 AI 图；配图画面无文字；无诊疗指导暗示；免责声明未被削弱

- **Verification**：`human-judgment`

### AC-5：构建与质量门

- **Given**：实施完成

- **When**：运行 `invoke build` 与 `invoke gates.all`

- **Then**：构建成功且无新增警告；utf8/toctrees/bundles 三门全绿；束/组/域计数与实施前一致（未新增束/文档）

- **Verification**：`programmatic`

### AC-6：适度性与阅读节奏

- **Given**：全部插入完成

- **When**：审查者浏览 5 束入口与插图页

- **Then**：配图 6–10 张、Mermaid 12–18 张；单页视觉资产 ≤2 个；references/ 与存目页无插图；每张图有引导语或说明文字，不孤立堆放

- **Verification**：`human-judgment`

### AC-7：变更可追溯

- **Given**：收尾阶段

- **When**：检查域 changelog 与各束 log

- **Then**：`changelog.md` 新增视觉资产版本条目，5 束 `log.md` 记录本次视觉资产变更；变更集报告列出全部新增/修改文件

- **Verification**：`programmatic`

## Open Questions

- [ ] 配图风格是否认可"水墨/工笔淡彩 + 暖纸色 + 无文字"方向？（批准 spec 即视为认可）

- [ ] 配图配额 6–10 张、Mermaid 12–18 张是否合适？

- [ ] 完成后是否需要由用户自行提交子模块（默认不自动 commit，仅给提交建议）？

