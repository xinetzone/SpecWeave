---
type: Spec
title: 《医心方》研读束配图与 Mermaid 视觉增强 PRD
source: 用户 /goal 指令（2026-09-02，seven-concepts-cmd 场景4 知识沉淀链路 R→I→V→C）
---

# 《医心方》研读束配图与 Mermaid 视觉增强 — Product Requirement Document

## Overview
- **Summary**：为 `projects/awesome-okf-xs/doc/bundles/yixue/medicine/ishinpo-reading/`（《医心方》阅读教程束，17 篇 Markdown）增补两类视觉资产：①Seedream AI 生成的氛围配图 9 张，存放于 `doc/_static/bundles/yixue/medicine/ishinpo-reading/images/`，以 `/_static/...` 绝对路径引用；②Mermaid 图表 5 张，以 ```mermaid 围栏直接内嵌（Sphinx `myst_fence_as_directive` 原生渲染）。
- **Purpose**：该束为纯文字文献学教程，三十卷结构、版本流传谱系、辑佚链路、阅读路线等时空/层级关系纯文字表达认知负荷高；配图营造古典医籍阅读氛围，mermaid 把结构与谱系可视化，落实"先立地图、再入原典"的束定位。
- **Target Users**：通过 Sphinx 站点（Read the Docs / GitHub Pages）阅读该束的普通读者与中医文献爱好者。

## Goals
- 为束首页与 6 篇 concepts、2 篇 examples 共 9 个文档各配 1 张风格统一的 AI 氛围图（references/ 信源登记页与 facts/insights/log 工作文档不配图）。
- 为 4 篇核心文档嵌入 5 张 Mermaid 图：三十卷结构（01）、辑佚链路（02）、版本流传谱系（03）、研究史时间线（04）、阅读四阶段路线（examples/02）。
- 全部视觉元素事实有据：mermaid 每个节点/边可回溯到 facts.md 的 F-编号；配图仅作氛围表达，不承载事实断言。
- `invoke gates.all` 三门全绿、`invoke build` Sphinx 构建无警告。

## Non-Goals (Out of Scope)
- 不新增/删除/重命名任何 Markdown 文档，不改动 toctree 结构与总索引计数。
- 不修改 facts.md / insights.md 的事实与洞察正文（视觉元素仅增量插入）。
- 不做真实书影/文物图像（版权与准确性不可控）；AI 图一律为写意插画，不模拟具体国宝文物。
- 不执行 git commit / push（按全局规则，提交由用户显式指令触发；共享子模块存在并行会话竞态）。
- 不为 references/、facts.md、insights.md、log.md 配 AI 图。

## Background & Context
- **配图先例**：`doc/_static/bundles/yishu/vocal/meitong-yanyin-pedagogy/images/` 已有 3 张配图，引用语法为 Markdown 图片 + 站点根绝对路径 `/_static/bundles/<域>/<组>/<束>/images/<file>`。
- **Mermaid 先例**：`doc/conf.py` 配置 `myst_fence_as_directive = ["mermaid"]`，sphinxcontrib-mermaid（≥0.9，CDN 渲染 mermaid 11.4.1）在 doc 依赖组中。
- **内容底色**：《医心方》为日本平安时代丹波康赖 984 年撰进的三十卷医方类书，征引隋唐以前中国医籍 204 种、万余条，大量亡佚引书（房中五书、《小品方》《养生要集》等）赖此保存；版本分御本—半井家本、宇治—仁和寺本、医家本三系统；安政本（1860）→ 杨守敬清末回传 → 现代整理本。
- **内容安全**：卷二十八房内主题涉及性文化，配图必须写意含蓄（闭卷、卷轴、书斋意象），禁止任何露骨人物呈现。
- **用户视觉偏好**：暖灰纸感、米白卡片、阅读优先；禁止纯黑/高对比深色。配图风格定为"暖纸底色水墨淡彩插画"。

## Functional Requirements
- **FR-1**：在 `doc/_static/bundles/yixue/medicine/ishinpo-reading/images/` 下生成 9 张 PNG 配图，文件名 kebab-case 英文，每张对应一个目标文档（见 tasks.md T1 设计稿）。
- **FR-2**：9 张图以 Markdown `![描述性alt](/_static/bundles/yixue/medicine/ishinpo-reading/images/<file>)` 语法插入对应文档开篇（H1 与首节之间或首节内），alt 为中文描述句。
- **FR-3**：5 张 Mermaid 图以内嵌 ```mermaid 围栏插入：三十卷结构分组图（concepts/01 §三）、亡佚—保存—辑佚链路图（concepts/02 §四）、版本流传谱系图（concepts/03 篇首或 §一）、研究史时间线图（concepts/04 篇首）、阅读四阶段路线图（examples/02 篇首）。
- **FR-4**：每张 Mermaid 图前配一句引导语，图后不做事实扩写（不新增未经 facts.md 支撑的陈述）。
- **FR-5**：log.md 追加 2026-09-02 工作日志条目，记录配图与 mermaid 增补、验证结果。

## Non-Functional Requirements
- **NFR-1（风格统一）**：9 张图共享同一视觉母题——暖米色宣纸底、水墨淡彩、平安/江户东亚古典书斋氛围；无任何文字/字符出现在图内（AI 文字渲染不可靠）；无露骨内容。
- **NFR-2（Mermaid 安全）**：遵循安全编码六规则（无空行、中文文本双引号、节点 ID 英文、`<br/>` 换行、subgraph `EN_ID ["中文"]` 格式、边标签 `-->| "标签" |`）；围栏小写 `mermaid`；单图节点 ≤20、subgraph 嵌套 ≤2 层。
- **NFR-3（事实零臆造）**：mermaid 中所有年代、人名、书名、版本名必须与 facts.md F-编号逐条对应；分歧数据（如引书 204/280 种）不在图中裁断，采用束正文已采用的表述。
- **NFR-4（构建门禁）**：`invoke gates.all`（utf8/toctrees/bundles）全绿；`invoke build` 无 warning/error（含图片路径可解析、mermaid 指令合法、frontmatter 不受影响）。
- **NFR-5（最小侵入）**：对现有 Markdown 的改动仅为插入行（图片引用、mermaid 块、引导语、log 条目），不删改正文句子。

## Constraints
- **Technical**：图片生成仅能使用主控会话的 GenerateImage（Seedream 插件）工具；子代理无此工具。图片落盘路径须在子模块 `doc/_static/` 内。构建环境为子模块 `pyproject.toml` 的 doc 依赖组（sphinxcontrib-mermaid 已声明）。
- **Business**：内容为公开知识包（Public），标准工作流；Spec 三件套存主权区 `.trae/specs/ishinpo-reading-figures/`。
- **Dependencies**：Seedream GenerateImage 配额；子模块 Python 构建环境（invoke/sphinx/myst）；SpecWeave 根 `check_mermaid.py` 可作 mermaid 语法快速自检。

## Assumptions
- 9 图 5 图的"配适度"判断：每个内容文档至多 1 张 AI 图 + 关键结构文档配 mermaid，总数克制；用户审批本 spec 即认可此数量。
- AI 图为写意氛围图而非史实复原图，故不做图内事实核验；事实表达全部由 mermaid 与正文承担。
- 子模块构建环境已安装 doc 依赖组（既往束交付均经 `invoke build` 验证）；若缺失则 T4 记录并先安装。

## Acceptance Criteria

### AC-1: 配图资产齐备且路径可解析
- **Given**：9 张目标文档各需 1 张配图
- **When**：检查 `doc/_static/bundles/yixue/medicine/ishinpo-reading/images/` 与各文档引用
- **Then**：9 个 PNG 文件存在、文件名与引用一一对应、引用路径为 `/_static/bundles/...` 语法；`invoke build` 无 "image not readable"/"non-readable path" 警告
- **Verification**: `programmatic`

### AC-2: 配图风格统一且内容安全
- **Given**：9 张 AI 生成图
- **When**：人工逐张查看
- **Then**：均为暖纸底水墨淡彩古典风格、图内无文字、无露骨/现代穿帮元素、与各文档主题语义相关
- **Verification**: `human-judgment`

### AC-3: Mermaid 五图语法与渲染合规
- **Given**：5 张内嵌 mermaid 图
- **When**：运行 `check_mermaid.py` 与 `invoke build`
- **Then**：语法检查无 error；Sphinx 构建无警告；图类型选择正确（结构/链路/谱系/时间线/路线）
- **Verification**: `programmatic`

### AC-4: Mermaid 事实零臆造
- **Given**：5 张图的全部节点、边、标签、年代
- **When**：对抗审查子代理逐条对照 facts.md（F-编号）与所在文档正文
- **Then**：每条事实可回溯；无 facts.md 之外的新人名/年代/数字；分歧数据未被图中裁断
- **Verification**: `programmatic`（清单式逐条核验）

### AC-5: 门禁与最小侵入
- **Given**：全部改动完成
- **When**：运行 `invoke gates.all` 并 `git diff --stat`
- **Then**：utf8/toctrees/bundles 三门全绿；改动仅含新增图片文件、图片引用行、mermaid 块、引导语与 log 条目；无正文句子删改
- **Verification**: `programmatic`

### AC-6: 工作日志可追溯
- **Given**：log.md
- **When**：查看 2026-09-02 条目
- **Then**：记录配图 9 张、mermaid 5 张的清单与验证结果
- **Verification**: `programmatic`

## Open Questions
- 无（数量、风格、路径、提交策略均已按先例与用户偏好确定；审批后直接执行）。
