# 国外物理学经典原著阅读 OKF Wiki 教程生成 - Implementation Plan

> 方法论链路：R（事实采集，G1）→ I（洞察，G2）→ E（三层拆分，G3）→ V（独立对抗审查）→ C（原子提交，G4）
> 所有内容产物路径前缀：`d:\AI\projects\awesome-okf-xs\doc\bundles\science\`
> 命令执行目录：`d:\AI\projects\awesome-okf-xs`

## Task 1: R 阶段——信源调研与 F 编号事实采集
- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 对 12 部核心元典逐部 WebSearch + WebFetch 核验：伽利略《两门新科学》(1638)、牛顿《原理》(1687)、麦克斯韦《电磁通论》(1873 + 1865 论文）、玻尔兹曼《气体理论讲义》(1896-98)、吉布斯《统计力学基本原理》(1902)、爱因斯坦 1905 五篇 + 1915/16 广义相对论、玻尔 1913 三部曲、海森堡 1925/1927、薛定谔 1926 六篇、狄拉克《量子力学原理》(1930)、费曼讲义（1964)、朗道-栗弗席兹十卷（1957-1981)
  - 核验 8+ 信源门户可达性：Project Gutenberg、Internet Archive、HathiTrust、UPenn Online Books Page、Wikisource、Einstein Papers Project、feynmanlectures.caltech.edu、Nobel Prize、Stanford Encyclopedia of Philosophy、Annalen der Physik/Wiley
  - 采集每部：外文原名、作者生卒年、首版年份/出版者/原始语言、篇章结构、PD 状态判定依据、≥1 个验证可达的权威全文 URL、权威英译本、中译本（出版社/译者/年份）
  - 登记 30+ 扩展经典（开普勒/惠更斯/拉格朗日/拉普拉斯/傅里叶/卡诺/克劳修斯/马赫/庞加莱/索末菲/玻恩/泡利/冯·诺依曼/温伯格/MTW 等）
  - 产出 `physics-classics-reading/facts.md`：F 编号事实表，G1 门——纯客观事实，无因果推断词
- **Acceptance Criteria Addressed**: AC-3, AC-4（版权状态事实基础）, AC-8（facts.md 为保留工作文档无 frontmatter 要求但需纳入 toctree）
- **Test Requirements**:
  - `rule` TR-1.1: facts.md 含 ≥60 条 F 编号事实；12 部核心著作每部 ≥4 条事实（原名/年份/语言/URL/PD 状态）；证据：facts.md 全文
  - `rule` TR-1.2: 所有外部 URL 经 WebFetch 实际访问成功且内容相符，核验结果在 facts.md 或任务完成证据中逐条登记（URL + HTTP 可达 + 内容摘要）；证据：完成证据中的 URL 核验表
  - `rule` TR-1.3: G1 门——facts.md 无"因为/导致/所以/说明了"等因果推断词；证据：grep 扫描结果
  - `rule` TR-1.4: 每部核心著作关键书目事实（作者/年份/书名）有 ≥2 独立权威信源；证据：facts.md 来源标注
- **Notes**: 不可达 URL 以同等级权威源替换并标注；禁止凭记忆写 URL

## Task 2: I 阶段——架构洞察与知识地图
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 产出 `physics-classics-reading/insights.md`：4-6 条核心洞察（四元组：现象+根因+影响+建议），候选方向：①经典语言从几何综合（牛顿）到分析代数（拉格朗日/麦克斯韦）再到抽象形式（狄拉克）的转换；②原著难度双重来源（数学工具 + 历史表达方式）；③教材与原著的知识倒置（教材按逻辑重组、原著按发现顺序展开）；④公有领域全文资源的 1929 时间断层；⑤阅读路径的"锚点著作"现象（费曼讲义作为原著与教材之间的桥）
  - 含编年 × 分支经典知识地图（mermaid 或表格）
  - G2 门：每条洞察四元组完整
- **Acceptance Criteria Addressed**: AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-2.1: insights.md 含 ≥4 条洞察，每条具备现象/根因/影响/建议四要素；证据：insights.md 全文
  - `rubric` TR-2.2: 洞察深度；scale 1-5；anchors 1=书单复述无洞察，3=有洞察但泛泛，5=洞察直接改变读者阅读策略且有事实支撑；threshold >= 4；证据：insights.md 独立审查评分

## Task 3: 脚手架——science 域、physics 分组、bundle 目录与 index 骨架
- **Status**: `pending`
- **Priority**: high
- **Depends On**: None（可与 Task 1 并行）
- **Description**:
  - 创建 `doc/bundles/science/index.md`（域级：frontmatter、域说明、分组导航表、hidden toctree 含 physics/index）
  - 创建 `doc/bundles/science/physics/index.md`（分组级：分组说明、bundle 列表表、toctree 含 physics-classics-reading/index）
  - 创建 bundle 目录树：`science/physics/physics-classics-reading/{concepts,examples,references}/`
  - 参照样板：think/index.md（域）、think/laozi/index.md（组）、boshu-reading/index.md（bundle 根，先建骨架后填充）
  - 每个目录 index.md 遵循保留文件约定
- **Acceptance Criteria Addressed**: AC-1, AC-8
- **Test Requirements**:
  - `rule` TR-3.1: 三级 index.md 存在且 toctree 引用路径正确；证据：目录树 + gates.toctrees 输出
  - `rule` TR-3.2: 域/组 index frontmatter 含 type 字段，bundle 根 index 含 okf_version: "0.2"；证据：frontmatter 检查

## Task 4: E 阶段——references/ 信源层文档（4-5 篇）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - `references/primary-sources.md`：12 部核心原著信源登记表（原名/作者/首版/语言/PD 状态/全文 URL/权威译本/中译本）
  - `references/interpretations.md`：权威解读资源（Cohen《Guide to Newton's Principia》、Pais《Subtle is the Lord》、SEP 物理哲学条目、Nobel lectures、《大学物理》费曼百年专栏、清华费曼课程等），每条标注权威等级与获取方式
  - `references/online-portals.md`：在线原文获取渠道门户（Gutenberg/archive.org/HathiTrust/UPenn/Wikisource/Einstein Papers/Caltech Feynman 等），含收录范围与使用条款
  - `references/copyright-policy.md`：版权与分级引用政策（PD 判定规则：1929 年前美国出版/作者逝世 70 年；合理使用边界；本 bundle 的引用规约）
  - `references/extended-canon.md`：30+ 扩展经典书单（按分支分组登记）
  - `references/index.md`：信源层导航
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-8
- **Test Requirements**:
  - `rule` TR-4.1: 每篇 frontmatter 含 type: Reference（或等效描述性类型值）、sources 字段；证据：文件检查
  - `rule` TR-4.2: 12 部核心著作 PD/在版权状态全部明确登记，与 facts.md 一致；证据：primary-sources.md 与 facts.md 交叉核对
  - `rule` TR-4.3: references 中全部 URL 与 Task 1 核验表一致（0 死链）；证据：链接比对

## Task 5: E 阶段——concepts/ 概念层文档（7-8 篇）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 4
- **Description**:
  - `concepts/00-why-read-originals.md`：为什么读物理学元典（教材 vs 原著价值、适用/不适用人群）
  - `concepts/01-canon-map.md`：物理学经典地图（编年 × 分支，12 核心 + 扩展谱系）
  - `concepts/02-reading-paths.md`：三条阅读路径（零基础/本科基础/研究型），具体到章节顺序与预计工时
  - `concepts/03-versions-translations.md`：版本与译本选择（原始语言版本、权威英译本、中译本分级推荐；公有领域版本 vs 现代译注本）
  - `concepts/04-math-preparation.md`：数学准备梯度（几何/微积分/矢量分析/微分方程/线性代数/张量，对应到具体著作）
  - `concepts/05-reading-geometric-style.md`：几何风格著作读法（《原理》引理-命题结构、综合几何证明策略）
  - `concepts/06-reading-papers.md`：原始论文读法（1905 奇迹年序列、1925-26 量子革命序列的论文间关系与阅读顺序）
  - `concepts/07-textbooks-and-originals.md`：教材与原著配合（费曼讲义/朗道十卷/现代教材的定位桥接）
  - `concepts/index.md`
- **Acceptance Criteria Addressed**: AC-6, AC-7, AC-8
- **Test Requirements**:
  - `rule` TR-5.1: 每篇 frontmatter 含 type: Concept + sources 归因；证据：文件检查
  - `rule` TR-5.2: 阅读路径篇（02）对每条路径给出 ≥3 个具体步骤（具体著作/章节/论文），不含"适当阅读"类空话；证据：02 篇全文
  - `rubric` TR-5.3: 教学可执行性；scale 1-5；anchors 1=书单罗列，3=有路径但环节模糊，5=路径具体到章节/论文/工时/数学前置；threshold >= 4；证据：独立审查评分

## Task 6: E 阶段——examples/ 示例层文档（3-4 篇）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1, Task 4, Task 5
- **Description**:
  - `examples/01-principia-close-reading.md`：《原理》精读示范——定义/公理（运动三定律）+ 第一卷命题Ⅰ（开普勒面积定律），含 PD 英文原文短引 + 中文解说 + 阅读方法批注
  - `examples/02-einstein-1905-walkthrough.md`：《论动体的电动力学》结构拆解（运动学/电动力学两部分、公设→同时性→变换→应用），含论文获取路径与读法批注
  - `examples/03-feynman-chapter-reading.md`：费曼讲义章节读法示范（卷一第 1 章"原子的假设"或卷二电磁章节），仅合理短引 + 官方在线版章节链接
  - `examples/04-galileo-dialogue-reading.md`（可选，时间允许时）：《两门新科学》对话体裁读法
  - `examples/index.md`
- **Acceptance Criteria Addressed**: AC-4, AC-6, AC-7, AC-8
- **Test Requirements**:
  - `rule` TR-6.1: 在版权著作引用单段外文原文 ≤50 词且标注出处；PD 著作双语引用标注出处；证据：V 阶段逐段审查
  - `rule` TR-6.2: 每篇含"获取路径 + 结构拆解 + 读法批注"三要素；证据：examples 全文
  - `rubric` TR-6.3: 精读示范可照做性；scale 1-5；anchors 1=只有内容摘要，3=有拆解但读者无法跟做，5=读者可按示范打开原文同步精读；threshold >= 4；证据：独立审查评分

## Task 7: bundle 根 index.md、log.md 与交叉链接
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 4, Task 5, Task 6
- **Description**:
  - 完善 `physics-classics-reading/index.md`：frontmatter（type/title/description/tags/version/source/generated/verified/status/stale_after/okf_version）、快速导航、快速开始（零基础/有基础两条入口）、bundle 定位表、推荐学习路径、完整 toctree（concepts/index、examples/index、references/index、facts、insights、log）
  - 创建 `log.md`：2026-08-30 创建条目（文档清单、事实数、信源数）
  - 全 bundle 交叉链接检查（bundle 内相对路径、references 归因脚注）
- **Acceptance Criteria Addressed**: AC-1, AC-8
- **Test Requirements**:
  - `rule` TR-7.1: bundle 根 index.md 的 toctree 覆盖全部内容文档与子目录 index；证据：gates.toctrees 输出
  - `rule` TR-7.2: log.md 遵循 YYYY-MM-DD 日期分组、最新在前；证据：文件检查

## Task 8: 总索引与站点首页集成
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 3, Task 7
- **Description**:
  - 更新 `doc/bundles/index.md`：frontmatter（domains 14、groups 33、total_bundles 281）、正文计数句、生态关系 mermaid（新增 science 节点及关系边：data→science? think↔science 等合理关系）、入门路径 mermaid（science 定位）、新增"十四域分组导航"science 章节（域说明 + physics 分组表行）、toctree 加 science/index
  - 更新 `doc/index.md`：计数文案（281 束/14 域/33 组）
  - 表格行/列数变动时整表替换（项目硬约束）
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-8.1: bundles/index.md 六处更新齐全（frontmatter 计数/正文数字/生态 mermaid/路径 mermaid/导航章节/toctree）；证据：逐项 diff 核对
  - `rule` TR-8.2: doc/index.md 计数与 bundles/index.md 一致；证据：grep 计数

## Task 9: 构建验证与修复闭环
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 7, Task 8
- **Description**:
  - 在 awesome-okf-xs 根目录执行 `invoke gates.utf8`、`invoke gates.toctrees`、`invoke clean && invoke build`
  - 修复全部 warning/error（常见：toctree 遗漏、frontmatter 日期、标题层级、尾随分隔线、代码块 lexer）
  - git status 核对变更仅落在预期文件
- **Acceptance Criteria Addressed**: AC-5, AC-1
- **Test Requirements**:
  - `rule` TR-9.1: `invoke gates.all` 退出码 0；证据：命令输出
  - `rule` TR-9.2: `invoke build` 0 warning/0 error；证据：命令输出
  - `rule` TR-9.3: 变更文件清单仅含 science/ 新文件 + bundles/index.md + doc/index.md（无子项目配置文件改动）；证据：git status

## Task 10: V 阶段——独立对抗审查与修复
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 9
- **Description**:
  - 以全新上下文委托一次只读独立审查（reviewer 获得：目标、spec/tasks 路径、bundle 路径、核验要求）
  - 审查维度：①物理事实硬伤（年份/作者/公式归属/术语，逐事实抽查 ≥30 条）；②版权合规（逐篇引用段落）；③URL 死链复验（抽样 ≥20 个）；④OKF 合规（frontmatter/保留文件/文件名 kebab-case）；⑤教学实用性评分（AC-6/AC-7 rubric）
  - 创建 review.md 记录检查点；fail 则将可执行发现 materialize 为修复 issue，回 Task 实现后重新审查
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-6, AC-7, AC-8
- **Test Requirements**:
  - `rule` TR-10.1: review.md 覆盖全部 AC，每个 AC 有独立证据；证据：review.md
  - `rule` TR-10.2: 物理事实 0 硬伤（发现 1 处即 fail）；证据：审查记录
  - `rubric` TR-10.3: 综合质量；scale 1-5；threshold >= 4；证据：reviewer 评分与理由

## Task 11: C 阶段——原子提交
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 10
- **Description**:
  - 在 awesome-okf-xs 子项目仓库内按单一职责拆分原子提交（建议：①feat(science) 新域+physics 分组+知识包；②docs(index) 总索引与首页集成；如审查修复产生独立变更则单独 fix 提交）
  - Conventional Commits，中文描述，提交前 UTF-8 消息编码检查
  - 不提交主权区 spec 文件到子项目；spec 工件在主权区另行处理（按用户指示）
- **Acceptance Criteria Addressed**: G4 质量门
- **Test Requirements**:
  - `rule` TR-11.1: 每个提交单一职责、`git show --stat` 验证文件范围；证据：git log/show 输出
  - `rule` TR-11.2: 提交后工作树无遗留未提交的 science 相关变更；证据：git status
