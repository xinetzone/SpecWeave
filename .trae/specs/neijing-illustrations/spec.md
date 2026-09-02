# 《黄帝内经》阅读教程束配图与 Mermaid 图表增强 - Product Requirement Document

## Overview
- **Summary**: 为 OKF 知识包 `yixue/huangdi-neijing/neijing-reading`（《黄帝内经》阅读教程，12 概念篇 + 9 精读篇 + 4 信源）生成 6 张 Seedream AI 文化意境配图与 10 张 Mermaid 知识结构图表，并按仓库既有范式插入文档、通过门禁验证。
- **Purpose**: 该束目前全文纯文字、无一张图。读者面对 162 篇经典的版本流传链、阴阳五行/经络/运气等抽象框架时缺少视觉抓手。配图降低经典距离感、营造阅读心境；Mermaid 把版本链、五行环、十二经流注、病因分类、女七男八节律等**知识结构**精确可视化，提升教程的可读性与回查效率。
- **Target Users**: 使用 OKF 文档中心阅读《黄帝内经》教程的中文读者（零基础读者 / 有中医常识基础者 / 研究型读者三类，束内已定义）。

## Goals
- 生成 **6 张风格统一的 AI 文化意境配图**（宋代院体工笔淡彩 / 水墨浅绛，绢本暖色），存放于 `doc/_static/bundles/yixue/huangdi-neijing/images/` 并以 `/_static/...` 绝对路径引用。
- 新增 **10 张 Mermaid 图表**，覆盖：全书结构与阅读路径、五行相生相胜、十二经脉流注、病因分类、病机治则、女七男八节律、五运六气推导、查注流程、十二周计划甘特图、束知识地图。
- 全部产物通过 `check-mermaid.py` 门禁与 `sphinx-build` 构建验证（无新增警告、无断链）。
- 经独立对抗审查（V 阶段）：Mermaid 知识内容与 facts.md/原文零事实冲突；AI 图无文字乱码、无技术误导。

## Non-Goals (Out of Scope)
- **不修改任何原文转录、引文、异文双录、表格正文文字**（图与表是纯增量，插入在既有段落之间，不删改正文）。
- **不生成技术性医学插图**：不画经络穴位图、解剖图、精确针形图、舌脉诊图——AI 生成此类图像事实风险不可控，且本束反复声明"非医疗建议"。
- **不为 examples/01~08 八篇精读篇配 AI 图**（精读篇以原文逐字转录为核心，保持肃穆的文本阅读节奏；仅 examples/09 通读计划加 1 张 Mermaid 甘特图）。
- 不执行任何 `git add` / `git commit`（awesome-okf-xs 为 git submodule 且存在并行会话写竞态；交付后由用户决定提交时机）。
- 不改动束外任何文件；不新增 toctree 条目（图片在 _static，不影响 toctree）。
- 不做图片的 PDF/印刷适配、不加图号编号体系（跟随 vocal 束先例：裸 `![alt](path)` 范式）。

## Background & Context
- **配图范式先例**：`yishu/vocal/meitong-yanyin-pedagogy` 束已验证范式：图片物理存放 `doc/_static/bundles/<域>/<组>/<束>/images/`，文档引用 `![描述性alt](/_static/bundles/.../images/name.png)`。本束路径无组层，即 `doc/_static/bundles/yixue/huangdi-neijing/images/`。
- **Mermaid 范式先例**：`guoxue/yinyangjia` 等束已使用 ```mermaid 围栏 + 中文双引号标签 + `<br/>` 换行；仓库有 `check-mermaid.py` 门禁与安全编码六规则（禁空行、中文加引号、禁列表符开头、`<br/>` 换行、subgraph 英文 ID、边标签引号）。
- **内容资产**：束内 facts.md 含 137 条零推测事实（F-001~F-137），Mermaid 所有节点文本必须可溯源至 facts.md 或文档正文，禁止即兴编造。
- **工具约束**：Seedream 图像生成（GenerateImage 工具）仅主控会话可用，子代理环境无此工具——故 T1 图像生成由主控执行，其余文档任务委托子代理。
- **七概念链路**：R（束内容与约定勘察，已完成）→ F（配图分层设计，见下）→ V（独立对抗审查）→ A（按文件分片原子交付）→ C（文件级交付，不提交）。

## 第一性原理设计（F 阶段产出）

**配图的本质职责分层**——两类视觉需求不可混用同一载体：

| 层 | 载体 | 职责 | 准确性要求 |
|---|---|---|---|
| 知识结构层 | Mermaid | 时序、分类、循环、流程、推导链的**精确**表达 | 必须 100% 可溯源（facts.md/原文） |
| 文化意境层 | Seedream AI 图 | 降低经典距离感、营造阅读心境、标示篇章主题 | 不承担技术准确性；只画"意境"不画"技术" |

由此推出 AI 配图的四条铁律：
1. **无文字铁律**：prompt 必须要求 no text / no calligraphy / no seals / no readable characters——AI 生成汉字与印章文字必乱码。
2. **无技术对象铁律**：不画标准太极符号（易画错）、不画穴位经络、不画解剖、不画可辨识的精确针形；九针图定位为"古针具意境静物"而非形制图谱。
3. **风格统一铁律**：全部 6 张统一为"宋代院体工笔 + 水墨浅绛、绢本暖底、无现代元素"，保证束内视觉一致。
4. **alt 诚实铁律**：alt 文本准确描述画面，九针/运气等含技术暗示的图须在图注语境中定位为"意境图"。

## Functional Requirements
- **FR-1**：在 `doc/_static/bundles/yixue/huangdi-neijing/images/` 生成 6 张 PNG 配图（hero 岐黄问道、简牍版本流传、阴阳山水意境、九针古器静物、四季山水长卷、五运六气星象），命名与 prompt 规格见 tasks.md T1。
- **FR-2**：10 张 Mermaid 按如下分布插入：
  - concepts/02 全书结构与三级阅读路径（flowchart）
  - concepts/03 五行相生相胜环（flowchart 环形）
  - concepts/05 十二经脉气血流注环（flowchart 环形）
  - concepts/06 病因分类树（生于阴/生于阳 → 六淫/七情/饮食居处等，flowchart）
  - concepts/08 病机十九条归类与正治反治（flowchart）
  - concepts/09 女七男八生命周期节律（双列 flowchart）
  - concepts/10 天干化运/地支化气推导链（flowchart）
  - concepts/11 三级注本选用与查注五步流程（flowchart）
  - examples/09 十二周通读计划（gantt）
  - insights.md 束知识地图（mindmap）
- **FR-3**：6 张配图以 `![alt](/_static/bundles/yixue/huangdi-neijing/images/<name>.png)` 形式插入：index.md（hero，置于首要声明之后、快速导航之前）、concepts/01、03、05、09、10 各 1 张（置于该篇首节正文之后）。
- **FR-4**：每张 Mermaid 前加一行引导句（如"下图展示……"），图后正文与图互补不重复；遵循安全编码六规则。
- **FR-5**：log.md 追加本次配图增强工作记录（日期、范围、6 图 10 表清单、V 审查结论）。
- **FR-6**：所有 Mermaid 节点事实可溯源至 facts.md F 编号或文档正文；子代理须先读目标文档再制图。

## Non-Functional Requirements
- **NFR-1（准确性）**：Mermaid 中十二经流注顺序、五行相生相胜关系、女七男八年龄节点、天干化运（甲己土…戊癸火）、地支化气（子午君火…巳亥风木）、病机十九条归属等关键事实零错误。
- **NFR-2（构建）**：`python check_mermaid.py`（或 .agents/scripts/check-mermaid.py）对变更文件零 error；`sphinx-build -b html docs docs/_build/html`（awesome-okf-xs 子项目内）无新增警告、无图片断链。
- **NFR-3（适度性）**：单篇文档至多 1 张 AI 图 + 1 张 Mermaid；图表总数 6 + 10，不堆叠。
- **NFR-4（风格一致）**：6 张 AI 图画风、色调、时代感统一；无任何现代元素、无文字、无印章。
- **NFR-5（最小侵入）**：不改动正文文字与 frontmatter；图片引用与 Mermaid 均为纯增量插入。

## Constraints
- **Technical**：Markdown/MyST 文档；Mermaid 经 sphinxcontrib-mermaid 渲染；图片放 Sphinx `_static` 目录；Windows 环境，Python 门禁脚本在 WSL 或 Windows PowerShell 均可运行（优先 WSL/py314 环境按用户偏好）。
- **Business**：本束为"文献与思想史教程，非医疗建议"——所有视觉产物不得强化"可据以自疗"的暗示；Mermaid 中医内容保持归类/框架性质。
- **Dependencies**：Seedream GenerateImage（主控）、check-mermaid.py、sphinx 构建环境（docs/requirements.txt）。
- **并发**：submodule 内可能有并行会话，禁止 git 写操作；编辑前确认目标文件无冲突标记。

## Assumptions
- `doc/_static/` 已被 awesome-okf-xs 的 Sphinx 配置纳为静态路径（vocal 束先例已验证 `/_static/...` 引用可构建）。
- 每张概念篇首节之后为合适的插图点；若子代理发现更贴合的插入位置（如紧邻相关小节），可就近调整但须在报告中说明。
- Mermaid 图均为 <20 节点的简单图，走"快速生成"方案，无需 team-mermaid 协作。
- gantt 图中文日期/周次标签按 mermaid gantt 语法可渲染（若 gantt 中文兼容性差，降级为 flowchart 时间线，须在审查中确认渲染）。

## Acceptance Criteria

### AC-1: 配图文件齐备且位置正确
- **Given**：T1 完成后
- **When**：检查 `doc/_static/bundles/yixue/huangdi-neijing/images/` 目录
- **Then**：存在 6 个 PNG 文件（hero-qibo、editions-slips、yinyang-landscape、nine-needles、four-seasons、yunqi-celestial），均可正常打开、非空、非占位
- **Verification**: `programmatic`

### AC-2: 配图引用全部可达
- **Given**：图片引用已插入 6 个文档
- **When**：解析所有 `![...](/_static/bundles/yixue/huangdi-neijing/images/...)` 引用并对照物理文件，且 sphinx-build 完成
- **Then**：6 条引用与 6 个文件一一对应，构建无 image not readable / 断链警告
- **Verification**: `programmatic`

### AC-3: Mermaid 门禁全绿
- **Given**：10 张 Mermaid 已插入
- **When**：运行仓库 Mermaid 检查脚本
- **Then**：变更文件零 error（六规则：无空行、中文文本双引号、英文节点 ID、`<br/>` 换行、subgraph 英文 ID、边标签引号）
- **Verification**: `programmatic`

### AC-4: Sphinx 构建无新增警告
- **Given**：全部产物就位
- **When**：在 awesome-okf-xs 子项目执行 sphinx 构建
- **Then**：huangdi-neijing 相关页面无 WARNING/ERROR（Mermaid 渲染、图片复制、MyST 解析均通过）
- **Verification**: `programmatic`

### AC-5: Mermaid 知识内容零事实错误
- **Given**：10 张 Mermaid
- **When**：独立审查代理逐图对照 facts.md 与正文核验（十二经流注、五行生克、女七男八、天干化运、地支化气、病机十九条、版本链节点等）
- **Then**：所有节点/标签与束内权威文本一致，无编造、无错位、无张冠李戴
- **Verification**: `human-judgment`（对照文本核验，rubric：关键关系错 1 处即 FAIL）

### AC-6: AI 配图无文字乱码且风格统一
- **Given**：6 张配图
- **When**：审查代理逐张目检
- **Then**：画面无任何文字/字母/印章/可辨识字符；无现代元素；六画风统一（工笔淡彩/水墨浅绛、绢本暖调）；主题与所在篇章匹配；九针图为静物意境而非技术图谱
- **Verification**: `human-judgment`

### AC-7: 适度性与最小侵入
- **Given**：全部插入完成
- **When**：审查代理检查变更面
- **Then**：单篇至多 1 图 1 表；examples/01~08 无 AI 图；正文文字与 frontmatter 未被修改（git diff 仅新增行）；未触碰束外文件；无 git 提交发生
- **Verification**: `programmatic` + `human-judgment`

### AC-8: 工作日志追加
- **Given**：交付完成
- **When**：查看 log.md
- **Then**：追加一节记录本次配图增强（日期、6 图 10 表清单、V 审查结论）
- **Verification**: `programmatic`

## Open Questions
- [x] gantt 若中文渲染兼容性不佳，是否同意降级为 flowchart 时间线？（默认：同意，以构建通过为准）→ 已解决：gantt 一次通过门禁、无需降级
- [x] 是否需要为 concepts/04 藏象、07 诊法补 Mermaid？（默认：不补——04 重点为表格且与 03 五行环互补，07 内容线性，保持"适度"）→ 按默认执行，未补
- [x] 图片是否需要在 examples/01~08 精读篇出现？（默认：不需要，保持精读篇文本肃穆感）→ 按默认执行，未出
