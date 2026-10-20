# VISTA 视觉 Harness 博文 → OKF 知识包 - Independent Review

> 审查方式：全新上下文的独立审查代理（read-only），对照 arXiv:2610.02200 全文与 LaTeX 源码包、官方项目页、GitHub README、ARC Prize 官方方法学、ARC-AGI-3 技术报告与 Anthropic 博文复核 26 项高风险声明，并执行四视角对抗审查与内部一致性机械核对。

- [x] CP-R1: 信源坐标、发布时点、事实溯源与数量口径准确
  - **Type**: `rule`
  - **Covers**: AC-2, AC-3, AC-6; TR-1.1, TR-2.1, TR-2.2, TR-7.1, TR-7.2
  - **Evidence**: 独立复核 26 项声明全部实质正确（0 项与权威源矛盾），含 ARC-AGI-3 主结果与动作数（7,302 vs 17,135）、RHAE 官方计分公式、四个基准数字与各自口径、消融阶梯、竞争系统表、论文 §6 局限、ARC-AGI-3 数据集构成与官方榜政策、GitHub 运行要求与两条示例命令、F 编号双份一致性（85 = 85，无跳号、无重复、无未登记引用）。
  - **Findings & Closure**: 首轮发现 1 项 P0（竞争系统成绩误引 F-065，实为 F-079 的消融阶梯）→ 新增 **F-077** 并改正 5 处引用；40.68 的引用由 [F-064] 改为 [F-047][F-077]。P1-1/P1-2/P1-3、P2-1~P2-6、P3-1~P3-6 均在同轮修订中落实。

- [x] CP-R2: 勘误完整落实，无源文错误静默照搬，无把作者观点固化为研究结论
  - **Type**: `rule`
  - **Covers**: AC-4; TR-4.2, TR-5.1, TR-8.1
  - **Evidence**: 勘误 E-1~E-9 全部在 `references/verification.md` 声明并在正文对应段落落实——论文 §6 数据污染局限置于 [03 成果与局限] 显著位置；ARC Prize 官方榜政策作为"限定四件套"第 ④ 条；effort/协议混淆标注为 E-9 并给出严格同条件对照（Sol max 13.33 → 99.00）；成本口径（F-080）补入 [03] 与 [05]；BabyVision 39 题按论文精确表述；项目页与论文两套数字差异标注来源；代码开源与运行要求补入。全部作者观点（F-013、F-033、F-041 等）显式标注为"作者观点"或"解读（假设）"。
  - **Findings & Closure**: 独立审查指出 E-1 的**理由**被夸大（论文 §3.1/摘要确实使用 actively 一词）与 E-6 的**前提**被误述（博文原文已写"选取的 39 道"）→ 两条勘误理由均已收窄为准确表述。

- [x] CP-R3: bundle 结构、frontmatter、导航、链接与计数合规
  - **Type**: `rule`
  - **Covers**: AC-1, AC-5; TR-6.1, TR-6.2, TR-7.1
  - **Evidence**: bundle 含 13 个 Markdown（根 index + log + 6 篇 concepts + 5 篇 references）。`check-toctrees.py` 通过（全部 index 引用有效、内容文档均可达）；`check-bundles-index.py` 通过（9 域 / 63 组 / 657 束，frontmatter、计数行、节标题、分组表、toctree 五面一致）；`check-utf8.py` 通过（11,971 文件）。相对链接 0 断链（跨分类链接按 `../../../practice/...` 深度校正）；frontmatter 必填字段齐备（`log.md` 依 OKF 保留名约定无 frontmatter，与同组既有 bundle 一致）；敏感路径 0 命中。
  - **Findings & Closure**: 首轮链接检查发现 6 处深度错误（`../` 少一层 / 跨分类路径未上溯三级）与 22 处 bundle-absolute `/references/...` 写法 → 已全部改为可解析的相对路径并复测归零。定向 Sphinx 构建 exit 0，无引用告警。

- [x] CP-R4: 交付边界、并行 WIP 隔离与未完成项如实记录
  - **Type**: `rule`
  - **Covers**: AC-1, AC-5, AC-6; TR-7.2, TR-9.1, TR-9.2
  - **Evidence**: 子模块工作树中的并行 WIP（`doc/bundles/jishu/iac/sst/log.md`、`verification.md`）在本任务前后均未被修改，也未被纳入本任务提交；`doc/bundles/index.md` 等共享索引的 diff 仅含本任务所需的计数与导航追加行。未复现论文实验（需付费 API + Docker + 算力）、未采集 ARC-AGI-3 私有/半私有游戏环境（不在任何公开仓库），二者均在 `references/source-manifest.md` 的"未采集项"与 bundle `log.md` 中显式声明。Mermaid 块使用 `<br/>` 换行——与本子模块既有 bundle 惯例一致（子模块仅含 toctree/计数/UTF-8 三项 gate，无 mermaid gate；主仓 mermaid 检查器不覆盖子模块工作树）。
  - **Findings & Closure**: 无未关闭的 P0~P2 项；未 push。

- [x] CP-U1: 全面性、准确性、可学习性与口径表达达到验收阈值
  - **Type**: `rubric`
  - **Covers**: AC-6; TR-3.1, TR-5.2, TR-8.2
  - **Scale**: 1-5
  - **Anchors**: 1 = 主题零散且关键机制/信源缺失；3 = 核心机制有覆盖但口径边界仍有明显空缺；5 = 机制/实验/局限/边界均有事实支撑，学习顺序连贯，差异表述清楚
  - **Pass Threshold**: >= 4
  - **Evidence**: **4/4/4/4，全部达标。**
    - **全面性 4**：三组件机制、记忆架构、四基准、消融、局限、未来方向、开源资产与运行要求均有事实支撑；经 P1-3/P2-2/P2-5 修订后补入成本口径、论文定位声明、ARC-AGI-3 基准规格与 `history` 工具。
    - **准确性 4**：26/26 声明实质正确、0 项事实性错误；P0-1 的 F 溯源缺陷已闭环。
    - **可学习性 4**：六篇文档路径连贯、Mermaid 图齐备、事实/假设/实践三层分离、快速入口表；经 P2-5 修订后补入 ARC-AGI-3 入门框与人类样本量标注。
    - **口径表达 4**：E-1~E-9 勘误集完整且与源文严格分离；经 P1-1/P1-2 修订后，头条对比的 effort 与协议混淆、基准方官方立场均已显式呈现，"限定三件套"升级为"四件套"。

## Review History

### Review R1
- **Result**: `pass`（带发现，发现已全部闭环）
- **Date**: 2026-10-20
- **Evidence**:
  - 全新上下文、read-only 的独立审查：26 项高风险声明逐条对照权威源取证；四视角（魔鬼代言人 / 新人 / 老板 / 未来）对抗审查；内部一致性机械核对。
  - 结论：0 项事实性错误；1 项 P0（F 溯源）、3 项 P1（口径限定）、6 项 P2（结构清晰度）、6 项 P3（建议）。P0/P1/P2/P3 全部在同轮修订中落实，复测后 F 编号 85=85、链接 0 断链、三项 gate 全通过、定向构建 exit 0。
  - 独立审查特别确认了本束最容易被略过的一点：**ARC Prize 官方明确公开集分数永不进入官方榜、且不是 AGI 进展的有效度量**——该限定已作为"限定四件套"第 ④ 条进入正文，而原博客完全未提。
- **Findings**: 无遗留的可行动项；无 P0~P2 未闭环项。
