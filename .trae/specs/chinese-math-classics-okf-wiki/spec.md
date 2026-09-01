---
name: chinese-math-classics-okf-wiki-spec
version: 1.0.0
created: 2026-08-30
source: "中国传统数学典籍公共领域知识（《算经十书》、宋元明清数学著作）；信源：ctext.org 中国哲学书电子化计划、维基百科、权威点校本与学术研究"
methodology: seven-concepts 场景4（知识沉淀）R→I→E，V 对抗审查由 Spec Mode 独立审查门承载
content-sensitivity: Public（汉唐至明清数学典籍原文均属公共领域，无访问控制）
target-repo: projects/awesome-okf-xs（git submodule，用户明确指定在其内生成）
---

# 中国数学典籍 OKF Wiki 教程 — 产品需求文档

## Overview

- **Summary**：在 awesome-okf-xs 文档库 `doc/bundles/think/` 域下新建 `suanxue`（算学）分组，并在其中创建 `suanjing-reading`（算经阅读教程）知识包，系统整理中国先秦至明清数学著作的原文与现代解读，形成符合 OKF v0.2 规范的中文教程。
- **Purpose**：将中国传统数学（算学）这一与古希腊数学平行的独立数学传统的公共领域知识，按 OKF 三层结构（concepts/examples/references）系统化沉淀，使学习者能"读到原文、看懂算法、理解体系、找到信源"。
- **Target Users**：对中国数学史与古典算法感兴趣的中文学习者；具备基础数学知识但无古文训练的理工科读者；需要可信信源索引的研究者。

## Goals

- 全面覆盖中国数学史三大阶段：汉唐《算经十书》体系、宋元数学高峰、明清中西会通。
- 以"著作"为纲：每部重要算经有独立或专节导读，含成书背景、内容结构、历史地位。
- 以"原文+解读"为特色：核心术文与经典算题引录公共领域原文片段（注明底本），配白话译文与现代数学符号对照（LaTeX 公式）。
- 信源先行：所有事实、原文引注可溯源到 references/ 中登记的稳定公开信源（ctext.org 扫描底本、权威点校本、学术研究）。
- 通过 awesome-okf-xs 全部质量门（UTF-8、toctree 完整性、Sphinx 构建）。

## Non-Goals

- 不做中国数学史的学术专著级 exhaustive 考证（如异文校勘、版本源流谱系），定位为入门→进阶教程。
- 不复制大段古籍全文（仅精选关键术文/算题片段，遵循精选引录原则）。
- 不修改 awesome-okf-xs 的构建配置（doc/conf.py）与 .agents/ 规范。
- 不自动提交 git（C 阶段产出原子提交方案，经用户确认后执行；子模块内提交需用户明确指令）。
- 不覆盖少数民族数学、日本和算等周边传统（仅在比较处提及）。

## Background & Context

- awesome-okf-xs 是 OKF v0.2 知识包文档库（Sphinx + myst_parser 构建），现有 13 域 32 组 280 束；`think/` 域（思想与理论）含 `psi/`、`laozi/` 两个分组，《老子》帛书阅读教程（boshu-reading）是最接近的人文经典教程先例。
- 文档工程已启用 `dollarmath`/`amsmath`（支持 `$...$`、`$$...$$` LaTeX 公式）与 mermaid 围栏图。
- 信源可行性已预验证：ctext.org 藏《周髀算经》《九章算术》《海岛算经》《孙子算经》原文（底本为《四部丛刊初编》《钦定四库全书》扫描件）；《算经十书》有钱宝琮点校本（中华书局）、郭书春点校本（辽宁教育出版社/江苏人民出版社）等权威版本。
- 环境验证：`python scripts/check-toctrees.py` 可直接运行（当前通过）；Sphinx 9.1.0 + myst_parser 已安装；`invoke` 因缺 `invocations` 包不可用，质量门以直接运行 scripts 与 sphinx-build 替代。
- 方法论：seven-concepts 场景4 知识沉淀链路 R（事实采集，G1 门：无因果词）→ I（洞察四元组，G2 门）→ E（萃取为三层文档，G3 门：可迁移模式）；V（对抗审查）由 Spec Mode 独立只读审查执行。

## Functional Requirements

- **FR-1**：新建分组 `doc/bundles/think/suanxue/index.md`（type: group），并更新 `think/index.md` 导航表与 toctree。
- **FR-2**：新建 bundle `suanjing-reading/`，含根 `index.md`（okf_version: "0.2"）、`log.md`、`facts.md`、`insights.md` 及 `concepts/`、`examples/`、`references/` 三个子目录（各含 index.md）。
- **FR-3**：concepts/ 含 14 篇概念文档：阅读价值（00）、历史脉络（01）、筹算与记数（02）、《九章算术》结构（03）与核心术文（04）、刘徽注（05）、《周髀算经》（06）、算经十书其余八种（07）、祖冲之父子（08）、宋元高峰（09）、大衍求一/天元/四元/垛积招差算法专题（10）、明清转型（11）、中国数学特征与中西比较（12）、阅读路径与注本选用（13）。
- **FR-4**：examples/ 含 8 篇实战文档：方田与分数（01）、盈不足双设法（02）、方程术与正负术（03）、勾股测量（04）、物不知数与大衍求一（05）、百鸡问题（06）、割圆术与圆周率（07）、系统阅读计划（08）。每篇算题文档须含"原文引录（注明底本）→ 白话译文 → 现代数学解读（公式/算法）→ 延伸"四段式。
- **FR-5**：references/ 含 4 篇信源登记：核心版本（core-editions）、在线信源（online-sources）、现代研究（modern-studies）、库内交叉引用（cross-ref），每条信源含稳定标识、URL/出版信息、用途说明。
- **FR-6**：facts.md 以编号事实表登记零推测事实（著作、作者、年代、题数、关键数值），每条标注信源 id；insights.md 含不少于 4 条四元组洞察（现象/根因/影响/建议）与知识地图。
- **FR-7**：更新 `doc/bundles/index.md` 总索引（计数 280→281、32→33、think 域 5束2组→6束3组、mermaid 节点与入门路径标签、导航表新增行）。
- **FR-8**：所有内容文档使用 OKF v0.2 YAML frontmatter（必填 type，推荐 title/description/tags/status/stale_after/sources/generated/verified），正文中文、文件名 kebab-case 纯英文。

## Non-Functional Requirements

- **NFR-1（事实可信）**：关键事实（成书年代、作者、题数、π 值、算法优先权年份）须与权威信源一致；存在学术争议处（如《周髀》成书年代、《夏侯阳算经》作者）须标注争议而非武断取一说。
- **NFR-2（可溯源）**：facts.md 每条事实、正文每个原文引录均可追溯至 references/ 登记信源；脚注/行内标注 sources id。
- **NFR-3（教学质量）**：概念文档面向零基础读者，术语首次出现给出解释；算题解读现代数学部分使用规范公式与算法步骤。
- **NFR-4（构建合规）**：不引入 Sphinx 构建警告（myst 标题层级、代码块语言标注、frontmatter 日期等遵循现有规范）。
- **NFR-5（风格一致）**：与 boshu-reading、katex 等现有 bundle 的结构、frontmatter、导航风格一致。

## Constraints

- **Technical**：Windows 环境；质量门用 `python scripts/check-toctrees.py`、`python scripts/check-utf8.py`、`sphinx-build -b dummy` 直接运行（invoke 缺 invocations 依赖）；数学公式用 dollarmath；图用 mermaid。
- **Business**：产出物位于 git submodule（projects/awesome-okf-xs）内；规范要求"不直接修改子项目文件需走子项目流程"，但用户已明确指令在该路径生成，按用户指令执行，提交环节单独确认。
- **Dependencies**：公开网络信源可达（ctext.org、维基百科等）；Sphinx/myst 已安装。
- **合规**：古籍原文为公共领域；现代研究仅作信源登记与事实引用，不大段摘录受版权保护的译文。

## Assumptions

- 用户认可"全面系统型"规模：14 concepts + 8 examples + 4 references + facts/insights/log ≈ 34 个新文件。
- 分组/包命名采用 `think/suanxue/suanjing-reading`（用户已确认）。
- 原文引录采用"精选片段+逐句解读"方式（用户已确认）。

## Acceptance Criteria

### AC-1: 目录结构与导航完整性
- **Type**: `rule`
- **Given**: 任务完成后的 awesome-okf-xs 工作树
- **When**: 运行 `python scripts/check-toctrees.py`
- **Then**: 输出"toctree 检查通过"，退出码 0；suanxue 分组与 suanjing-reading bundle 的全部文档均可达、无断链、无孤立文档
- **Pass Condition**: 检查脚本退出码 0 且输出通过信息
- **Evidence**: 命令输出文本

### AC-2: OKF frontmatter 合规
- **Type**: `rule`
- **Given**: bundle 内所有非保留 .md 文件
- **When**: 逐文件检查 YAML frontmatter
- **Then**: 每个文件含可解析 frontmatter 且有非空 `type`；bundle 根 index.md 含 `okf_version: "0.2"`；index.md/log.md 遵循保留文件结构
- **Pass Condition**: 人工/脚本抽查全部 34 个新文件 0 违规
- **Evidence**: 文件审查记录 + toctree 脚本（含 bundle-root 检测）通过

### AC-3: 关键事实准确性
- **Type**: `rule`
- **Given**: facts.md 与正文陈述的关键事实（至少含：九章 246 题、刘徽 263 年注、祖冲之 π 上下界与密率 355/113、物不知数答 23、百鸡问题、秦九韶 1247、朱世杰 1303、《算法统宗》1592、十书 1084 年刊刻等 10 项锚点事实）
- **When**: 对照 references/ 登记的权威信源逐项核验
- **Then**: 10 项锚点事实全部与信源一致；争议事实有显式争议标注
- **Pass Condition**: 10/10 通过，争议处理 0 武断
- **Evidence**: 审查核验表（review.md 记录）

### AC-4: 原文引录与解读四段式
- **Type**: `rule`
- **Given**: examples/ 01-07 七篇算题文档
- **When**: 逐篇检查结构
- **Then**: 每篇含原文引录（注明底本来源，如 ctext 四部丛刊本）、白话译文、现代数学解读（含 LaTeX 公式或算法步骤）、延伸说明四部分；原文与 ctext/点校本可对照
- **Pass Condition**: 7/7 篇满足四段式且原文引注有信源 id
- **Evidence**: 文档审查记录

### AC-5: Sphinx 构建通过
- **Type**: `rule`
- **Given**: 完成全部文档
- **When**: 运行 `sphinx-build -b dummy -E doc _build/dummy`（或等价全量构建）
- **Then**: 构建成功，退出码 0，无新增警告/错误
- **Pass Condition**: 退出码 0 且警告数不高于任务前基线
- **Evidence**: 构建输出

### AC-6: 编码与命名规范
- **Type**: `rule`
- **Given**: 全部新增文件
- **When**: 运行 `python scripts/check-utf8.py` 并检查文件名
- **Then**: UTF-8 无 BOM；文件名 kebab-case 纯英文数字与连字符；正文中文
- **Pass Condition**: 检查通过且 0 个中文文件名
- **Evidence**: 脚本输出 + 文件清单

### AC-7: 教程系统性与可读性
- **Type**: `rubric`
- **Dimension**: 教程质量（覆盖面、教学路径、零基础友好、原文-解读衔接）
- **Scale**: 1-5
- **Anchors**: 1 = 仅资料堆砌，无路径无解读；3 = 覆盖主要著作但解读浅、路径不清；5 = 三阶段全覆盖、每书有导读、算题有完整四段式解读、index 有清晰学习路径
- **Pass Threshold**: >= 4
- **Evidence**: 独立审查评分与评语

### AC-8: 信源质量与可溯源性
- **Type**: `rubric`
- **Dimension**: references 信源（稳定性、权威性、分级、可达性）与正文溯源密度
- **Scale**: 1-5
- **Anchors**: 1 = 无信源或死链；3 = 有信源但部分不可达/不权威/溯源稀疏；5 = 信源分三级（原典底本/现代点校/学术研究）、URL 可达、facts 与原文引注 100% 可溯源
- **Pass Threshold**: >= 4
- **Evidence**: 独立审查链接抽查与溯源核对

### AC-9: 总索引一致性
- **Type**: `rule`
- **Given**: doc/bundles/index.md 与 think/index.md
- **When**: 检查计数、导航表、mermaid、toctree
- **Then**: total_bundles=281、groups=33、think 域"6 束 · 3 组"；think/index.md 含 suanxue 行与 toctree 条目；mermaid/入门路径标签更新
- **Pass Condition**: 计数与实际文件一致、导航完整
- **Evidence**: 文件 diff 审查 + toctree 通过

## Open Questions

- 无（分组命名、规模、原文引录方式均已与用户确认；提交环节待实现完成后单独确认）。
