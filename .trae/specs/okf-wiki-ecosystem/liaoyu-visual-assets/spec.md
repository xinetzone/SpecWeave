---
title: "艺术疗愈六束视觉资产增补（配图 + Mermaid）"
status: "draft"
---

***

type: Spec
title: 艺术疗愈六束视觉资产增补（配图 + Mermaid）
okf\_version: "0.2"
generated: { by: "agent:main", at: "2026-09-02T16:30:00+08:00" }
----------------------------------------------------------------

# 艺术疗愈六束视觉资产增补（配图 + Mermaid） - Product Requirement Document

## Overview

- **Summary**: 为 `projects/awesome-okf-xs/doc/bundles/yishu/liaoyu/` 知识组（艺术疗愈：总览 + 美术/音乐/舞动戏剧/表达性艺术/中国艺术疗愈共 6 束、约 60 个 Markdown 文件）增补两类视觉资产：① 使用 seedream（GenerateImage）生成 7 张统一风格的主题配图（6 束封面各 1 张 + 组首页 1 张）；② 在高叙事价值位置配置 8–12 张 Mermaid 结构图（时间线、谱系、流程、决策树、分层、循环等）。全部产出遵循 OKF v0.2 既有先例与 Mermaid 安全编码六规则。

- **Purpose**: 该组目前零配图、零 Mermaid，纯文字密度高；艺术疗愈主题天然适合视觉化，且组内存在大量"一图胜千言"的结构性内容（六层术语、六阶段时间线、组织合并谱系、情志相胜循环、四问决策树等）。视觉资产可降低阅读门槛、强化结构记忆，并与同域 meitong 束（已有 3 张解剖配图）的体验对齐。

- **Target Users**: OKF 文档库读者（艺术疗愈学习者、临床执业向读者、学术研究向读者）及后续维护该束的 AI 智能体。

## Goals

- 为 6 束各配 1 张统一暖调编辑插画风格的封面配图，组首页配 1 张总览图，共 7 张，存放路径与引用方式严格遵循 meitong 束先例。

- 在 6 束中配置 8–12 张 Mermaid 图（每束 ≥1 张），覆盖：术语分层、历史时间线、职业化合并谱系、理论模型结构、决策树、情志相胜循环等最高价值结构。

- 视觉资产**只做增量**：不改动任何事实陈述、frontmatter、免责声明、toctree 与既有结论。

- `invoke build`（sphinx-build）零警告、`invoke gates.all`（utf8/toctrees/bundles）全绿。

- 按 seven-concepts 方法论执行：R（事实采集/视觉点盘点）→ I（洞察高价值可视化点）→ E（萃取产出图与图注）→ V（对抗审查）→ C（交付闭环，不提交 git）。

## Non-Goals (Out of Scope)

- 不新增、改写、删改正文事实、数据、信源与结论（视觉资产是表达层增量，不是内容修订）。

- 不新增束/分组、不调整目录结构、不改 toctree、不动 frontmatter。

- 不执行 git add/commit（用户未要求提交；C 阶段以门禁验证 + 交付报告闭环）。

- 不使用外部图床 URL（图片一律落本地 `_static/`，保证 RTD 构建与离线可用）。

- 不为 facts.md / references/sources.md 等登记类文档配图（叙事性 concepts/index/examples 才是配图位置）。

- 不生成含文字的信息图（AI 图内文字不可靠；结构性信息一律由 Mermaid 承载）。

## Background & Context

- **目标内容结构**：`liaoyu/` 组含 6 束——`liaoyu-overview`（枢纽束，含 insights.md）、`art-therapy`、`music-therapy`、`dance-drama-therapy`、`expressive-arts`、`china-art-therapy`；组索引 `liaoyu/index.md`。

- **图片先例（同库）**：`doc/_static/bundles/yishu/vocal/meitong-yanyin-pedagogy/images/` 下 3 张图（.png/.jpg），正文以 `![alt 文本](/_static/bundles/.../images/xxx.png)` 引用（见该束 concepts/01-singing-physiology.md）。

- **Mermaid 先例**：`doc/conf.py` 已启用 `myst_fence_as_directive = ["mermaid"]`（sphinxcontrib-mermaid 11.4.1，CDN JS 渲染，零构建依赖）；全库 30+ 束文件已在用 \`\`\`mermaid 代码块。

- **Mermaid 安全编码六规则**（docs/tech/references/development-standards.md）：① 代码块内禁空行；② 非纯英文标签一律双引号包裹；③ 标签内禁止 Markdown 列表触发格式（"1. "、"- " 开头，改中文冒号/去空格）；④ 换行用 `<br/>` 禁用 `\n`；⑤ subgraph 用 `subgraph ID ["标题"]`（ID 英文标识符）；⑥ 带标签边用 `-->|"标签"|`。

- **子模块约束**：awesome-okf-xs 是 git submodule，本次变更发生在子模块内；门禁命令为子模块内 `invoke build` / `invoke gates.all`（Python 环境 py314）。

- **内容敏感度**：公开内容（开源 OKF 知识库），标准工作流，规划文档存 `.trae/specs/okf-wiki-ecosystem/liaoyu-visual-assets/`。

## Functional Requirements

- **FR-1（R 阶段盘点）**：通读 6 束 index/concepts/examples/insights，产出视觉资产方案表：7 张配图的文件名/插入位置/alt 文本/seedream prompt，以及 8–12 张 Mermaid 的目标文件/插入章节/图类型/节点内容草案；图中一切事实性内容必须可溯源到束内正文或 facts 条目，禁止新造事实。

- **FR-2（配图生成）**：用 seedream GenerateImage 生成 7 张图，统一为暖调、柔和、纸感的编辑类插画风格（warm muted palette, soft editorial illustration, no text），landscape 比例；输出到 `doc/_static/bundles/yishu/liaoyu/<bundle>/images/`（组首页图放 `liaoyu-overview/images/` 或 `_static/bundles/yishu/liaoyu/images/`，方案阶段定）。

- **FR-3（图片插入）**：在每束 index.md 上部（导语之后、导航之前）插入封面图引用 + 一句中文引导句；组首页同理；alt 文本准确描述画面且与束主题相关。

- **FR-4（Mermaid 配置）**：按方案在 concepts/examples 文档中插入 Mermaid 代码块，每块前有一句引导句、块后内容与图呼应；候选图位（R 阶段可调整）：

  1. overview/concepts/00-overview：术语六层分层图（临床职业→伞式术语→跨模态模型→广义健康促进）
  2. overview/concepts/01-history：1921 心理剧→2019 WHO 报告六阶段时间线
  3. overview/examples/01-branch-chooser：四问分支选择决策树
  4. art-therapy/concepts/01-founders：Hill(1942)→Naumburg→Kramer→Ulman(1961)→AATA(1969) 先驱谱系
  5. art-therapy/concepts/03-projective-techniques：Goodenough 1926 / Buck 1948 / Machover 1949 投射技术脉络
  6. music-therapy/concepts/01-professionalization：NAMT(1950)→AAMT(1971)→AMTA(1998 合并) 谱系
  7. music-therapy/concepts/03-three-models：分析性/GIM/Nordoff-Robbins 三大模型结构图
  8. dance-drama-therapy/concepts/03-drama-therapy-models：Emunah 整合五阶段流程图
  9. expressive-arts/concepts/01-knill-intermodal：intermodal 跨模态转移循环图
  10. china-art-therapy/concepts/02-qingzhi-xiangsheng：五志相胜循环图（怒胜思/思胜恐/恐胜喜/喜胜忧/忧胜怒，以正文记载为准）

- **FR-5（日志留痕）**：每束 log.md 追加 2026-09-02 视觉增补记录（R/I/E/V 各阶段一行，遵循该束 log 既有格式）。

- **FR-6（V 阶段验证）**：独立子代理执行对抗审查——Mermaid 六规则逐条核对、sphinx-build 零警告、gates.all 全绿、git diff 审计确认无事实篡改。

## Non-Functional Requirements

- **NFR-1（事实零篡改）**：`git diff` 中除新增二进制图片、Mermaid 代码块、图片引用行、引导句与 log 行外，不得出现既有正文行的删除或改写。

- **NFR-2（构建健康）**：`invoke build` 无 warning/error（特别关注 image not readable、mermaid parse error、Malformed YAML）。

- **NFR-3（风格一致）**：7 张配图为同一视觉语言（暖灰/米白/暖赭色调、柔和纸感、无文字、无高对比深色），与用户"暖灰纸感、阅读优先"偏好一致。

- **NFR-4（适度原则）**：Mermaid 总量控制在 8–12 张，每束 1–2 张，只在结构信息确实可被图压缩的位置插入；配图每束至多 1 张封面。

- **NFR-5（编码合规）**：所有新增/修改文件 UTF-8 无 BOM；Markdown 路径引用为相对/`_static` 绝对先例形式，禁止 `file:///`。

## Constraints

- **Technical**：Markdown + MyST（myst-parser）；Mermaid 经 sphinxcontrib-mermaid CDN 渲染；图片为本地静态文件；子模块内用 `invoke` 任务链验证；Windows 环境，路径用正斜杠。

- **Business**：公开知识库，图片内容须健康、非医疗承诺导向（与束内免责声明口径一致，不得出现"治愈/疗效"暗示性画面）。

- **Dependencies**：seedream GenerateImage 插件（图生成）；子模块 doc 构建环境（invoke/sphinx）；Mermaid 六规则规范文档。

## Assumptions

- 7 张配图（6 束封面 + 组首页 1 张）与 10 张左右 Mermaid 构成"适度"配置；如用户在审批时希望增减，以审批意见为准。

- GenerateImage 输出格式由工具决定（.png/.jpg），引用时以实际落盘扩展名为准。

- 子模块当前工作树无他人未完成合并（执行前 V 阶段会检查 `.git/MERGE_HEAD` 与并行会话竞态）。

- 图片插入位置默认在每束 index.md 导语段之后；Mermaid 插入位置默认在对应 concepts/examples 文档的相关章节内，R 阶段方案可微调。

## Acceptance Criteria

### AC-1: 配图落盘且引用一致

- **Given**: R 阶段方案已确定 7 张图的文件名与插入位置

- **When**: E 阶段完成生成与插入

- **Then**: `doc/_static/bundles/yishu/liaoyu/` 下存在 7 个图片文件；每个文件在且仅在目标 md 中被 `![alt](/_static/...)` 引用一次；sphinx-build 无任何 image 相关警告

- **Verification**: `programmatic`

### AC-2: Mermaid 合规且渲染成功

- **Given**: 8–12 张 Mermaid 已插入各束文档

- **When**: 执行 `invoke build`

- **Then**: 构建零警告零错误；逐块核对满足六规则（无空行/标签双引号/无列表触发/`<br/>` 换行/subgraph 与边标签格式）

- **Verification**: `programmatic`

### AC-3: 视觉位置与叙事契合

- **Given**: 全部图与 Mermaid 就位

- **When**: 人工按束审阅

- **Then**: 每张图/图块前有自然引导句，图义与所在章节主题直接对应；Mermaid 内容与正文事实一致（时间、人名、组织名、模型名无错漏）

- **Verification**: `human-judgment`

### AC-4: 事实零篡改

- **Given**: V 阶段执行 git diff 审计

- **When**: 比对全部变更

- **Then**: 变更集仅包含：新增图片二进制、新增 Mermaid 块、新增图片引用行与引导句、log.md 追加行；无既有正文/facts/frontmatter/免责声明/toctree 的修改

- **Verification**: `programmatic`

### AC-5: 质量门全绿

- **Given**: 全部插入完成

- **When**: 在子模块目录执行 `invoke gates.all`

- **Then**: utf8 / toctrees / bundles 三项全部通过

- **Verification**: `programmatic`

### AC-6: 编纂日志留痕

- **Given**: 视觉增补完成

- **When**: 检查 6 束 log.md

- **Then**: 每束 log.md 含 2026-09-02 视觉增补记录（配图/Mermaid 数量与位置）

- **Verification**: `programmatic`

### AC-7: 配图风格统一且无文字

- **Given**: 7 张图生成完毕

- **When**: 人工查看

- **Then**: 七图为统一暖调纸感编辑插画、无文字/无乱码、无医疗疗效暗示、画面与束主题匹配

- **Verification**: `human-judgment`

## Open Questions

- [ ] 配图数量默认 7 张（6 束封面 + 组首页），是否需要增减？

- [ ] Mermaid 默认 \~10 张（候选清单见 FR-4），"适度"口径是否认可？

- [ ] 组首页配图存放目录：默认 `_static/bundles/yishu/liaoyu/images/`（组级），是否认可？

