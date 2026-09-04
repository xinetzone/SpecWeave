# 艺术疗愈六束视觉资产增补 - The Implementation Plan (Decomposed and Prioritized Task List)

> 方法论链路（seven-concepts，场景4 知识沉淀 + V 对抗）：R（盘点）→ I（视觉点洞察）→ E（配图与 Mermaid 产出）→ V（对抗验证）→ C（交付闭环，不 commit）。
> 工作目录：`d:\spaces\SpecWeave\projects\awesome-okf-xs`（git submodule）；图片落 `doc/_static/bundles/yishu/liaoyu/...`；文档在 `doc/bundles/yishu/liaoyu/...`。
> 全部子任务委托子代理执行，一次只推进一个任务；每任务完成后更新本文件状态。

## [x] Task 1: R+I 阶段——六束通读与视觉资产方案设计
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 通读 `doc/bundles/yishu/liaoyu/` 下 6 束全部文件（index.md、concepts/、examples/、insights.md、facts.md 可抽样核对），梳理每束叙事骨架与可可视化结构。
  - 产出方案文件 `d:\spaces\SpecWeave\.trae\specs/okf-wiki-ecosystem/liaoyu-visual-assets\visual-plan.md`，含两张表：
    1. **配图表（7 行）**：束名、图片文件名（kebab-case 英文）、落盘目录（`doc/_static/bundles/yishu/liaoyu/<bundle>/images/`，组首页图用 `doc/_static/bundles/yishu/liaoyu/images/`）、插入目标文件与位置（束 index.md 导语段之后）、中文 alt 文本、seedream 英文 prompt（统一风格前缀：warm muted palette, soft paper-textured editorial illustration, gentle healing mood, no text, no words, no letters；各束主题元素：总览=多艺术形态环绕、美术=画架画笔与曼陀罗、音乐=竖琴/聆听场景、舞动戏剧=舒展舞姿与戏剧面具、表达性=颜料乐器诗稿舞鞋多媒介、中国=古琴水墨与宣纸、组首页=六分支艺术疗愈意象）、image_size（landscape_16_9）。
    2. **Mermaid 表（8–12 张，默认 10 张，候选见 spec FR-4）**：编号 M1–Mn、目标文件绝对路径、插入章节锚点（## 标题）、图类型（flowchart/timeline 等）、**完整可用的 Mermaid 源码草案**（严格遵循六规则：无空行、非纯英文标签双引号、禁 "1. "/"− " 列表触发、换行 `<br/>`、subgraph `ID ["标题"]`、边标签 `-->|"x"|`）、图前引导句草案、每个节点事实内容的来源文件标注。
  - G1 事实门：Mermaid 中所有人名、年份、组织名、模型名、阶段名必须能在对应束正文/facts 中找到出处；方案表中加"事实来源"列，禁止新造事实或因果演绎。
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-1.1: visual-plan.md 存在且包含 7 行配图表与 8–12 行 Mermaid 表；每行 Mermaid 含目标文件路径（文件真实存在）、源码块、来源列。
  - `programmatic` TR-1.2: Mermaid 源码草案静态扫描——无空行、含中文标签均带双引号、无 `\n`、无 `"数字. ` / `"- ` 触发模式。
  - `human-judgement` TR-1.3: 主代理审核——图位选择确属高叙事价值位置（每束 1–2 张），prompt 主题与束定位匹配，无医疗疗效暗示。
- **Notes**: 方案完成后主代理审核通过才进入 Task 2；候选图位可据通读结果微调，但总数保持 8–12。

## [x] Task 2: E 阶段（图）——seedream 生成 7 张配图（完成：7 张 .jpg 全部落盘，363–482 KB，实际文件名已回写 visual-plan.md）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 按 visual-plan.md 配图表，使用 seedream GenerateImage 工具逐张生成 7 张图；path 参数不带扩展名，落盘到方案指定 `doc/_static/bundles/.../images/` 目录（目录不存在则先建）。
  - 每张生成后核对：文件真实落盘、画面无文字/乱码、风格与统一前缀一致、主题匹配；不合格的重生成（同一图最多重试 2 次）。
  - 记录每张图的实际文件名与扩展名（.png/.jpg），回写 visual-plan.md 的"实际文件名"列，供 Task 3 引用。
- **Acceptance Criteria Addressed**: AC-1, AC-7
- **Test Requirements**:
  - `programmatic` TR-2.1: 7 个图片文件存在于方案指定目录，文件大小 > 50KB（非空图）。
  - `human-judgement` TR-2.2: 逐图查看——暖调纸感编辑插画、无文字、与束主题匹配、无疗效暗示；7 图风格统一。
- **Notes**: 若子代理环境不可用 GenerateImage，立即停止并回报，由主代理直接生成；不得用占位图或外部 URL 替代。

## [x] Task 3: E 阶段（文）——插入图片引用、Mermaid 与 log 留痕（完成：7 处配图引用 + 10 张 Mermaid + 6 个 log 小节；改动集 23 md + 7 图，Mermaid 引擎直检 0 错误 0 警告）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 按 visual-plan.md 逐束编辑：
    - 6 束 index.md + 组 `liaoyu/index.md`：导语段之后插入 `![alt](/_static/bundles/yishu/liaoyu/.../images/<实际文件名>)` 引用行，引用前加一句中文引导句（自然衔接，不改动导语原文）。
    - 各 concepts/examples 文档：在指定章节锚点处插入 Mermaid 代码块（```` ```mermaid ```` 围栏），块前加引导句；块后原有正文保持不变。
    - 6 束 log.md：按各束既有 log 格式追加 `## 2026-09-02 视觉增补（R/E/V 阶段）` 小节，记录配图与 Mermaid 数量、位置、方法（seedream 生成 / 七概念链路）。
  - 严禁改动：frontmatter、事实正文、免责声明、toctree、facts.md、references/。
  - 引用路径严格用 `/_static/bundles/yishu/liaoyu/...` 正斜杠形式（meitong 先例）。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-6
- **Test Requirements**:
  - `programmatic` TR-3.1: grep 确认 7 处图片引用路径与落盘文件一一对应（扩展名一致）、无断链；Mermaid 围栏数量与方案一致（8–12）。
  - `programmatic` TR-3.2: `git status`/`git diff --stat` 显示改动仅限 6 束 index.md、组 index.md、concepts/examples 目标文档、6 个 log.md 与新增图片；frontmatter 区无 diff。
  - `human-judgement` TR-3.3: 引导句与上下文衔接自然，无重复贴图、无图注事实错误。
- **Notes**: Edit 时逐文件小步修改；共享索引（bundles/index.md 等）本次不触碰，避免并行会话竞态。

## [x] Task 4: V 阶段——独立对抗审查与门禁验证（完成：六项审查全 PASS——Mermaid 10 块 0 违规、事实抽查 6 束一致、diff 纯新增、MERGE_HEAD 无、聚焦构建 succeeded 且 liaoyu 0 warning、gates.all 三项全绿 9域/44组/389束）
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 由独立子代理（未参与 Task 1–3）执行对抗验证：
    1. **Mermaid 六规则逐条扫描**：对新增每个 mermaid 块核对——无空行、标签双引号、无列表触发格式、无 `\n`、subgraph/边标签格式；尝试用 mermaid CLI 或静态规则判定可解析性。
    2. **事实一致性抽查**：每个 Mermaid 块中的年份/人名/组织名/阶段名与所在束 facts.md/正文比对，至少抽查 5 束。
    3. **构建验证**：在 `projects/awesome-okf-xs` 目录执行 `invoke build`（必要时先 `pip install -e .` 或确认 py314 环境有 invoke/sphinx/sphinxcontrib-mermaid），要求零警告零错误；重点查 image not readable、mermaid 解析错误、YAML 错误。
    4. **门禁**：执行 `invoke gates.all`，utf8/toctrees/bundles 全绿。
    5. **diff 审计**：`git diff` 与 `git status` 确认无既有正文/facts/frontmatter/免责声明/toctree 被修改；新增文件仅图片与（无新增 md）。
    6. 检查 `.git/MERGE_HEAD` 不存在（无并行合并竞态）。
  - 发现问题逐项修复后重跑验证，直至全绿；修复属 Task 3 范畴的回退 Task 3 方式处理并记录。
- **Acceptance Criteria Addressed**: AC-2, AC-4, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-4.1: `invoke build` 退出码 0 且输出无 warning/error（附输出尾部日志）。
  - `programmatic` TR-4.2: `invoke gates.all` 三项全过（附输出）。
  - `programmatic` TR-4.3: diff 审计结论——被修改文件清单与预期集合完全一致，无事实正文行被改写（给出 `git diff --stat` 与抽查结果）。
  - `human-judgement` TR-4.4: 渲染后 HTML 中 Mermaid 图与图片正常呈现的人工确认（构建产物中图片路径可访问）。
- **Notes**: 若构建环境缺依赖，先安装子模块 pyproject 声明的文档依赖（doc/requirements 或 pyproject extras），不得跳过构建验证。

## [x] Task 5: C 阶段——交付汇总报告（完成：本任务收尾报告即交付物，未执行 git commit）
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 汇总：7 张图片清单（路径+主题）、Mermaid 清单（编号+所在文件+类型）、门禁与构建结果、变更文件统计、遗留项与 Open Questions 答复情况。
  - 不执行 git add/commit（用户未要求）；提示用户后续可按原子提交规范分束提交。
  - 更新 tasks.md/checklist.md 全部勾选闭环。
- **Acceptance Criteria Addressed**: AC-1~AC-7 汇总确认
- **Test Requirements**:
  - `human-judgement` TR-5.1: 报告清单与实际落盘/插入内容一致，可直接用于用户验收。
