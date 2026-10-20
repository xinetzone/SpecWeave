# VISTA 视觉 Harness 博文 → OKF 知识包 - Implementation Plan

> **方法论**：seven-concepts 知识沉淀（R→I→E→V→C），与 blog-article-to-okf-wiki 七阶段工作流对齐。按信源预检 → 事实 → 洞察 → 分批生成 → 导航 → 核验 → 交付顺序推进。
> **内容敏感度**：公开内容（微信公众号文章，无访问控制参数）→ 标准工作流。
> **目标位置**：`projects/awesome-okf-xs/doc/bundles/jishu/ai/models/vista-visual-harness/`。

## Task 1: 敏感度预检与信源登记
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 判定内容级别：`mp.weixin.qq.com/s/3S5OW6ytgz27zrq4UgCkgQ` 无 `code=`/`token=`/邀请码 → 公开内容 → 标准工作流。
  - 登记公众号身份与发布时点：量子位（`alias=QbitAI`）、作者 henry、`var ct="1791513671"` → 2026-10-09 10:41 北京时间；访问时点 2026-10-20。
  - 登记全部权威源坐标：arXiv abs/HTML、项目页、GitHub、ARC Prize 方法学、ARC-AGI-3 论文、Anthropic 博文；标注各自角色与边界。
  - 记录采集停止规则与未采集项（私有/半私有游戏环境不在公开仓库）。
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-1.1: 信源分类、所有权信号、发布与访问时点、停止规则均可复核；evidence 为 `references/source-manifest.md`。
- **Completion Evidence**: `references/source-manifest.md` 记录主信源 12 项元数据字段、8 个权威源坐标、4 类未采集项及原因。

## Task 2: R 阶段采集编号事实
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 按"博文事实 / 权威核验补充事实"两段登记，使用连续 F 编号。
  - 对 P0 声明（数字、日期、官方表态、成效数字、术语归属）逐项对照 arXiv 全文、项目页、GitHub、ARC 官方方法学取证。
  - 差异单列勘误，不静默照搬；作者观点显式标注。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4
- **Test Requirements**:
  - `rule` TR-2.1: 每条事实含来源定位且不含动机推断；evidence 为 `facts.md` 与 `references/article-source.md` 逐条对照。
  - `rule` TR-2.2: 事实编号连续无跳号，双份登记集合相等；evidence 为正则集合比对脚本输出。
- **Completion Evidence**: F-001~F-085（F-001~F-044 博文事实，F-045~F-085 权威核验补充事实）；双份各 85 条，集合完全相等、无跳号、无未登记引用。

## Task 3: I 阶段形成洞察与知识地图
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 骨架判定（操作可复现性两问）：博文无读者可照做的安装/配置/实测流程 → 不设 `examples/`。
  - 形成 5 项洞察（四元组：陈述 / 证据 / 反常识 / 行动），每项挂 F 编号。
  - 规划 6 篇 concepts 与三层知识拆分（事实层 / 机制层 M1~M5' / 迁移层 T1~T5）。
- **Acceptance Criteria Addressed**: AC-3, AC-6
- **Test Requirements**:
  - `rubric` TR-3.1: 洞察与知识地图质量；1 = 无事实引用或无可用顺序，3 = 覆盖主要主题但依赖关系不足，5 = 洞察均引用事实并能决定连贯的读者路径；threshold >= 4；evidence 为 `insights.md` 与 facts 对照。
- **Completion Evidence**: `insights.md` 5 项洞察均含四元组与 F 编号证据；骨架判据与理由显式留痕于 spec 与 bundle 索引。

## Task 4: 信源先行生成 references
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 先生成 `references/article-source.md`（F 编号双份登记之一）、`references/verification.md`（P0 核验报告 + 勘误）、`references/knowledge-map.md`（三层知识）、`references/source-manifest.md`（信源与边界）。
  - 后生成 `references/index.md`，含隐藏 toctree。
- **Acceptance Criteria Addressed**: AC-2, AC-4
- **Test Requirements**:
  - `rule` TR-4.1: references 在所有引用它的概念文档之前存在；evidence 为文件清单与 sources 解析。
  - `rule` TR-4.2: 勘误 E-1~E-9 全部在 verification.md 声明并在正文落实；evidence 为勘误表与正文段落对照。
- **Completion Evidence**: 4 份 references + 索引；勘误 9 项（E-3 为论文局限未述的重大遗漏，E-9 为独立复核新增的 effort/协议混淆）。

## Task 5: 生成概念文档
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 按学习路径生成 6 篇 concepts：00 总览 / 01 三组件机制 / 02 记忆与上下文 / 03 ARC-AGI-3 结果口径 / 04 跨基准验证 / 05 局限与实践。
  - 每批不超过 7 个文件；全部具体声明挂 F 编号；事实、作者观点、执行者解读三层分离。
  - 最后生成 `concepts/index.md`（含隐藏 toctree 与快速入口表）。
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-6
- **Test Requirements**:
  - `rule` TR-5.1: concepts 中每个数字/模型名/组件名均可回溯到已登记事实；evidence 为全量 F 引用解析脚本输出。
  - `rubric` TR-5.2: 教程覆盖质量；threshold >= 4；evidence 为覆盖矩阵与独立 Review 评分。
- **Completion Evidence**: 6 篇 concepts；85 条事实全部被正文引用（0 条未引用），无未登记引用。

## Task 6: 最后生成 bundle 索引并挂载父级导航
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 内容定稿后生成 bundle 根 `index.md` 与 `log.md`。
  - 更新 `jishu/ai/models/index.md`（9→10 束，新增导航行与 toctree 条目）、`jishu/ai/index.md`、`jishu/index.md`、`doc/bundles/index.md`（总数 656→657、jishu 486→487、ai 255→256）。
  - 计数按官方 gate 口径（目录树为地面真值）核对，不凭记忆写数字。
- **Acceptance Criteria Addressed**: AC-1, AC-5
- **Test Requirements**:
  - `rule` TR-6.1: 新 bundle 从父级导航与文档根可达，所有目录索引覆盖本目录内容，未改写其他 bundle；evidence 为导航 diff 与 toctree gate。
  - `rule` TR-6.2: 总束数/分组数/技术域数与目录树一致；evidence 为 `check-bundles-index.py` 输出。
- **Completion Evidence**: `check-toctrees.py` 与 `check-bundles-index.py` 均通过（9 域 / 63 组 / 657 束，五面一致）。

## Task 7: 机械门禁与构建验证
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 执行 F 编号双份一致性、相对链接可达、frontmatter 完整、敏感路径零残留四项机械检查。
  - 运行子模块三项质量门；执行定向 Sphinx 构建验证渲染与引用。
  - 核对 Mermaid 块在本子项目的既有惯例（子模块无 mermaid gate，`<br/>` 为既有 bundle 通用写法）。
- **Acceptance Criteria Addressed**: AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-7.1: 本次变更相关质量门全部通过或经证据确认零命中；evidence 为命令输出。
  - `rule` TR-7.2: 链接、frontmatter、F 编号、敏感路径检查零失败；evidence 为检查脚本输出。
- **Completion Evidence**: 三项 gate 全部 exit 0；F 编号 85=85 完全一致、无跳号、0 未登记引用；相对链接 0 断链；frontmatter 齐备（`log.md` 依 OKF 保留名约定无 frontmatter）；敏感路径 0 命中；定向 Sphinx 构建 exit 0 且无引用告警。

## Task 8: 独立对抗审查（V 阶段）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 由全新上下文的独立审查代理复核 26 项高风险声明、四视角对抗审查、内部一致性。
  - 按 P0~P3 分级处理；P0 与 P1 在同轮修订中关闭。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-6
- **Test Requirements**:
  - `rule` TR-8.1: 独立审查的 P0/P1 发现全部闭环；evidence 为修订 diff 与复测记录。
  - `rubric` TR-8.2: 全面性/准确性/可学习性/口径表达四项评分 >= 4；evidence 为独立 Review 评分。
- **Completion Evidence**: 独立审查结论为 **PASS-WITH-FINDINGS**：0 项事实性错误、1 项 F 溯源缺陷（P0-1，新增 F-077 并改正 5 处引用）、3 项需补限定（P1-1 ARC Prize 官方榜政策 / P1-2 effort 与协议混淆 / P1-3 成本口径）、6 项结构改进（P2）、6 项建议（P3）。P0 与 P1 已全部落实；P2 中 P2-1~P2-6 已落实，P3-1~P3-6 已落实。四维度评分 4/4/4/4，均达阈值。

## Task 9: C 阶段交付核对
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 8
- **Description**:
  - 核对子模块与主仓两处 status/diff，确保不含无关或并行 WIP 文件。
  - 按显式文件列表执行原子提交：① 子模块内 bundle + 四级索引；② 主仓 spec 三件套 + 子模块指针。
  - 不 push。
- **Acceptance Criteria Addressed**: AC-1, AC-5
- **Test Requirements**:
  - `rule` TR-9.1: 交付清单仅含本任务文件且与目标路径一致；evidence 为两仓库 status/diff。
  - `rule` TR-9.2: 提交信息符合 Conventional Commits，中文主体，无乱码；evidence 为提交记录。
- **Completion Evidence**: 子模块提交仅含 `doc/bundles/jishu/ai/models/vista-visual-harness/` 13 个文件与四级索引的追加行；并行 WIP `doc/bundles/jishu/iac/sst/` 的既有改动未被纳入。主仓提交仅含本 spec 三件套与子模块指针。

## Task 10: 源码轮阶段 0——信源稳定性门预检（G0）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 9
- **Description**:
  - 识别新信源：`github.com/joshhhhhan/VISTA`（MIT License）。GitHub API 查询确认**无任何 release tag** → 按 Skill 规范固定到 commit hash，禁止浮动 `main`。
  - 固定坐标 `c97c354f0a8948256545a3e8850a1848f8e5b8c1`（2026-10-04）；本地只读检出置 `external/libs/joshhhhhan/VISTA/`（`external/` 已被根 `.gitignore` 忽略）。
  - 引用规则：bundle 内一律使用 GitHub `blob/<commit>/<path>#Lx-Ly` 形式；**不写入任何本机绝对路径**、不使用 file 协议绝对路径。
  - 清理前扫描与持久性 audit：`check-source-path-stability.py --target`（零引用放行）与 audit 模式（本次用于确认本束零命中）。
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-10.1: 信源固定到不可变 commit 且记录 tag 查询结论；evidence 为 GitHub API 查询与 `git rev-parse HEAD`。
  - `rule` TR-10.2: bundle 内零本机路径、零 file 协议引用；evidence 为全量路径扫描脚本输出。
- **Completion Evidence**: F-086 登记无 tag 事实与 commit 坐标；本地检出 HEAD 一致；GATE-SPS audit 全库扫描 24,227 个 Markdown，**本束零命中**（红项均为他目录既有欠债）；机械扫描 `sensitive path hits: none`。

## Task 11: 源码轮 R 阶段——源码事实采集与脚本计数
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 10
- **Description**:
  - 全量盘点目录结构、模块、符号、工具、CLI 参数、环境变量、入口点；**数量类事实一律脚本计数**，不以人工枚举为唯一依据。
  - 登记源码事实 F-086~F-130，并补登 F-131~F-140（为计数类声明补独立背书）。
  - 记录两处口径差（ARC 动作空间、上下文窗口）与三处论文未述细节（像素量化、history 粒度、压缩分叉）。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-6
- **Test Requirements**:
  - `rule` TR-11.1: 每条源码事实指向 `文件:行` 或固定 commit 坐标；evidence 为逐条来源映射。
  - `rule` TR-11.2: 数量事实附计数口径（原始匹配数 vs 去重名数；递归 vs 非递归）；evidence 为计数脚本与独立复算。
- **Completion Evidence**: F-086~F-140 共 **55** 条源码/论文事实；双份登记与 Spec `facts.md` 集合完全相等（140 = 140，无跳号、无未登记引用）。

## Task 12: 源码轮 I/E 阶段——三层拆分与增量生成
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 11
- **Description**:
  - I 阶段：新增 M6（工具即文件、文件即接口）与 M7（论文是机制层、源码是复现层）两项洞察，均含四元组。
  - E 阶段：按 source-code-to-okf-wiki §6.5 做**增量扩展**——新增信源登记 2 份、concepts 续编号 06~10、新增 examples 3 篇；**不改写第一轮已通过 V 阶段的结论**。
  - 骨架变更：仓库 README 提供完整可复现路径，故由"无 examples"改为设立 `examples/`（3 篇）。
  - 每批不超过 7 个文件；索引最后写。
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-4, AC-6
- **Test Requirements**:
  - `rule` TR-12.1: 新文档编号续接既有最大序号，既有文档结论未被改写；evidence 为 diff 与目录清单。
  - `rule` TR-12.2: references 先于 concepts 生成；evidence 为文件创建顺序与 sources 解析。
- **Completion Evidence**: 新增 references 2 份、concepts 5 篇（06~10）、examples 3 篇 + 索引；concepts 现共 11 篇；`examples/index.md` 记录骨架变更理由。

## Task 13: 源码轮 V 阶段——独立复核与闭环
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 12
- **Description**:
  - 由全新上下文的独立代理用**自写脚本**复算 13 项计数、Grep 验证约 120 个符号/常量/参数/环境变量/入口点、逐字比对 17 段引文、逐条比对 18 条命令。
  - 按 P0~P3 分级处理；P0（无）、P1、P2、P3 在同轮修订中闭环。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-6
- **Test Requirements**:
  - `rule` TR-13.1: 独立复核的 P1 及以上发现全部闭环；evidence 为修订 diff 与复测记录。
  - `rule` TR-13.2: 计数与引用精度类发现均有独立 F 编号背书；evidence 为 F-131~F-140 与正文挂接清单。
- **Completion Evidence**: 独立复核结论 **PASS-WITH-FINDINGS**：0 项 P0、2 项 P1、9 项 P2、6 项 P3，全部属引用精度而非事实错误。闭环内容：E-15（`history` 两套语义分述）、E-16（按键数 11）、F-131~F-140 补齐 9 类计数声明背书、6 项 P3 精度修正（引文近失、实现指针、同构性表述、参数名、提交数核验口径）。

## Task 14: 源码轮 C 阶段交付核对
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 13
- **Description**:
  - 核对子模块与主仓两处 status/diff，确认不含并行 WIP（`jishu/iac/sst`）与他任务文件。
  - 按显式文件列表执行原子提交：① 子模块内 bundle 新增/修改文件与索引追加行；② 主仓 spec 文件与子模块指针。
  - 不 push。
- **Acceptance Criteria Addressed**: AC-1, AC-5
- **Test Requirements**:
  - `rule` TR-14.1: 交付清单仅含本任务文件；evidence 为两仓库 status/diff。
  - `rule` TR-14.2: 提交信息符合 Conventional Commits 且中文无乱码；evidence 为提交记录。
- **Completion Evidence**: 子模块提交仅含本 bundle 的新增/修改文件与 `jishu/ai/models/index.md` 的描述行；`jishu/iac/sst/` 并行 WIP 未纳入。主仓提交仅含本 spec 文件与子模块指针。

## Task Dependencies

第一轮：Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 6 → Task 7 → Task 8 → Task 9

第二轮（源码与论文补充）：Task 10 → Task 11 → Task 12 → Task 13 → Task 14

## Quality Gates

- **G0**：信源坐标不可变、公众号所有权信号与发布时点可复核、采集停止规则留痕。
- **G1**：事实无推断词、逐条可溯源、F 编号连续且双份登记一致。
- **G2**：洞察四元组完整，知识地图与篇目均映射 F 编号。
- **G3**：OKF 文档引用稳定信源、批次 <= 7、索引最后生成、骨架判据留痕。
- **G4/V**：独立事实复核 + 四视角对抗审查 + 链接/frontmatter/toctree/计数/构建复验。
