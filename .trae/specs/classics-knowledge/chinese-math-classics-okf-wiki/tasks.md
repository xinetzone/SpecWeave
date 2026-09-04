# 中国数学典籍 OKF Wiki 教程 — 实施计划

> 方法论：seven-concepts 场景4（知识沉淀）R→I→E；V 由独立审查门承载；C 产出提交方案待用户确认。
> 目标根目录：`d:\AI\projects\awesome-okf-xs\doc\bundles\think\suanxue\`

## Task 1: R-1 调研信源并登记 references/（信源先行）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 网络调研核实信源：ctext.org 算书类目（周髀/九章/海岛/孙子原文 URL 与底本）、维基百科/维基文库条目、《算经十书》点校本（钱宝琮中华书局1963、郭书春）、学术研究（李俨、钱宝琮《中国数学史》、李约瑟 SCC 卷3、吴文俊《中国数学史大系》、Martzloff、Chemla）
  - 创建 `suanjing-reading/references/` 下 4 篇：online-sources.md、core-editions.md、modern-studies.md、cross-ref.md + index.md
  - 每条信源含稳定 ID、URL/出版信息、可达性说明、用途
  - cross-ref 登记与库内 bundle 关联（katex、sympy、psi-math、viz/3b1b、laozi/boshu-reading）
- **Acceptance Criteria Addressed**: AC-8、NFR-2
- **Test Requirements**:
  - `rule` TR-1.1: references/ 4 篇内容文档 + index.md 存在，index.md toctree 引用 4 篇；证据：文件清单
  - `rule` TR-1.2: 登记的外部 URL 全部为公开稳定信源（ctext.org/维基/出版社），无死链（抽查 ≥8 个 URL 可达）；证据：链接抽查记录
  - `rubric` TR-1.3: 信源分级质量；scale 1-5；anchors 1=堆砌无分级/3=有分级但权威弱/5=原典底本/现代点校/学术研究三级清晰；threshold >= 4；证据：独立审查

## Task 2: R-2 事实采集 facts.md（G1 门：零因果词）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 基于 Task 1 信源采集编号事实（F-xxx）：著作清单（书名/卷数/作者/年代/题数/注者/底本）、人物（生卒/贡献）、关键数值（246题、π 上下界、355/113、23、百鸡三组解等）、制度史（656 国子监算学馆、1084 刊刻、明算科）
  - 每条事实标注信源 id；纯客观陈述，禁用"因为/导致/所以"等因果词
  - 争议事实（周髀成书年代、夏侯阳作者、缀术佚失时间）并列诸说
  - 产出 `suanjing-reading/facts.md`
- **Acceptance Criteria Addressed**: AC-3、NFR-1
- **Test Requirements**:
  - `rule` TR-2.1: facts.md 含 ≥60 条编号事实，每条带信源 id；证据：文件审查
  - `rule` TR-2.2: G1 门——全文无因果推断词（因为/导致/所以/由于）扫描通过；证据：grep 扫描记录
  - `rule` TR-2.3: 10 项锚点事实（九章246题、刘徽263、祖冲之π界与密率、物不知数答23、百鸡问题、秦九韶1247《数书九章》、朱世杰1303《四元玉鉴》、算法统宗1592、1084 北宋刊刻、祖暅原理）与信源一致；证据：核验表

## Task 3: I 洞察 insights.md（G2 门：四元组完整）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 产出 `suanjing-reading/insights.md`：≥4 条核心洞察（每条含现象描述/根因分析/影响评估/改进建议四元组），主题如"算法化传统vs演绎传统"、"十书体系化与制度支撑"、"宋元高峰后的中断与会通"、"算题读法的古今转译"
  - 附知识地图 mermaid（时代-著作-算法-人物关系）
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `rule` TR-3.1: insights.md 含 ≥4 条四元组洞察 + 1 张 mermaid 知识地图且可渲染；证据：文件审查 + 构建
  - `rubric` TR-3.2: 洞察深度；scale 1-5；anchors 1=泛泛而谈/3=有观点无证据/5=反常识且有事实支撑、可指导阅读；threshold >= 4；证据：独立审查

## Task 4: E-1 concepts/ 概念文档 14 篇 + index
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 创建 `concepts/`：00-why-read-suanjing、01-history-overview、02-chousuan-numeration、03-jiuzhang-structure、04-jiuzhang-key-methods、05-liuhui-commentary、06-zhoubi-suanjing、07-suanjing-shishu、08-zu-chongzhi、09-song-yuan-peak、10-dayan-tianyuan-siyuan、11-ming-qing-transition、12-chinese-math-characteristics、13-reading-path + index.md
  - 每篇含 OKF frontmatter（type: Concept、sources 引用 references）、正文中文、必要 LaTeX 公式/mermaid
  - 著作导读类篇章含：成书与作者、内容结构、核心算法、历史地位、原文选读（注明底本）、延伸阅读
  - concepts/index.md 含全部 14 篇导航
- **Acceptance Criteria Addressed**: AC-2、AC-7、NFR-3
- **Test Requirements**:
  - `rule` TR-4.1: 14 篇 .md + index.md 齐全，文件名 kebab-case 纯英文；证据：文件清单
  - `rule` TR-4.2: 每篇 frontmatter 含非空 type 且 YAML 可解析；证据：frontmatter 审查
  - `rule` TR-4.3: 涉及原文处注明底本与信源 id；无因果词要求仅 facts.md，concepts 允许论述但事实须与 facts.md 一致；证据：抽查 5 篇事实一致性
  - `rubric` TR-4.4: 概念文档教学质量；scale 1-5；anchors 1=堆砌/3=可读但浅/5=体系清晰、术语有解释、古今对照准确；threshold >= 4；证据：独立审查

## Task 5: E-2 examples/ 算题实战 8 篇 + index
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 创建 `examples/`：01-fangtian-fractions、02-yingbuzu-double-false、03-fangcheng-negative、04-gougu-pythagoras、05-wuwuzhishu-crt、06-baiji-weng、07-geyuan-pi、08-reading-plan + index.md
  - 01-07 严格四段式：原文引录（注明 ctext/底本）→ 白话译文 → 现代数学解读（LaTeX 公式/算法步骤/与现代定理对照）→ 延伸（历史传播/优先权）
  - 08 为系统阅读计划（对标 boshu-reading 03-reading-plan）
- **Acceptance Criteria Addressed**: AC-4、NFR-3
- **Test Requirements**:
  - `rule` TR-5.1: 8 篇 + index.md 齐全；01-07 每篇含四个固定小节标题（原文/译文/解读/延伸）；证据：结构审查
  - `rule` TR-5.2: 每篇原文引录带信源 id/底本注记；数学解读含至少 1 个 LaTeX 公式或算法步骤；证据：逐篇审查
  - `rubric` TR-5.3: 古今转译准确性（盈不足=双设法、方程=高斯消元、大衍求一=CRT、割圆=极限迭代等对照无数学错误）；scale 1-5；anchors 1=有数学错误/3=对照正确但粗糙/5=对照精确且指出差异边界；threshold >= 4；证据：独立审查数学核验

## Task 6: E-3 bundle 根 index.md、log.md 与分组/总索引更新
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 4, Task 5
- **Description**:
  - `suanjing-reading/index.md`：bundle 根（okf_version "0.2"、type: OKF、sources、generated/verified、快速导航、学习路径、toctree 引用 concepts/index、examples/index、references/index、facts、insights、log）
  - `suanjing-reading/log.md`：创建日志（2026-08-30 条目，登记文件清单与方法论链路）
  - `think/suanxue/index.md`：分组索引（type: group，含 suanjing-reading 导航 + toctree）
  - 更新 `think/index.md`：域说明、导航表新增 suanxue 行、toctree 增加 suanxue/index
  - 更新 `doc/bundles/index.md`：计数（280→281 束、32→33 组、think 5束2组→6束3组）、think 导航表新增行、mermaid think 节点标签、入门路径标签
- **Acceptance Criteria Addressed**: AC-1、AC-9、NFR-5
- **Test Requirements**:
  - `rule` TR-6.1: suanjing-reading/index.md 含 okf_version 且 toctree 引用全部子 index 与工作文档；证据：文件审查 + toctree 脚本
  - `rule` TR-6.2: think/index.md 与 bundles/index.md 计数一致（281/33/6束3组）且导航表/toctree/mermaid 同步；证据：diff 审查
  - `rule` TR-6.3: log.md 存在且日期条目格式 YYYY-MM-DD；证据：文件审查

## Task 7: V-1 质量门与构建验证
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 运行 `python scripts/check-toctrees.py`、`python scripts/check-utf8.py`
  - 运行 `sphinx-build -b dummy -E doc _build/dummy`（全量构建，零新增警告）
  - 文件名 kebab-case 核查；修复全部发现的问题
- **Acceptance Criteria Addressed**: AC-1、AC-5、AC-6
- **Test Requirements**:
  - `rule` TR-7.1: check-toctrees.py 退出码 0 输出通过；证据：命令输出
  - `rule` TR-7.2: check-utf8.py 通过（无 BOM/非法编码）；证据：命令输出
  - `rule` TR-7.3: sphinx-build 退出码 0 且无新增警告；证据：构建输出
  - `rule` TR-7.4: 新增文件名 0 个含中文/空格；证据：文件清单核查

## Task 8: V-2 独立对抗审查（fresh context）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 委派一个全新上下文的只读审查者（general_purpose_task），按独立审查合同核验：AC-1~AC-9 全覆盖、事实锚点 10 项对照权威信源、四段式结构、数学转译正确性、信源可达性、frontmatter 合规
  - 审查结果写入 `.trae/specs/classics-knowledge/chinese-math-classics-okf-wiki/review.md`
  - fail 则将 actionable findings 转为 Issue 任务回 Task 修复，修复后重新审查
- **Acceptance Criteria Addressed**: AC-3、AC-7、AC-8（独立证据）
- **Test Requirements**:
  - `rule` TR-8.1: review.md 存在且每个 AC 有独立核验证据；证据：review.md
  - `rule` TR-8.2: 审查结果 pass，或所有 fail 项均已转为 Issue 并修复闭环；证据：Review History
  - `rubric` TR-8.3: 审查独立性与深度；scale 1-5；anchors 1=走过场/3=核验但未查外部信源/5=独立抽查外部信源与数学正确性；threshold >= 4；证据：审查报告质量

## Task 9: C 原子提交方案（待用户确认）
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 8
- **Description**:
  - 在 awesome-okf-xs 子模块内核对 git status/diff，给出单一职责原子提交方案建议（如 `feat(bundles): 新增 think/suanxue 算经阅读教程知识包`）
  - 不自动执行提交，待用户明确指令
- **Acceptance Criteria Addressed**: 流程闭环
- **Test Requirements**:
  - `rule` TR-9.1: 提交方案仅含本任务新增/修改文件，无误带无关变更；证据：git status 核对记录
