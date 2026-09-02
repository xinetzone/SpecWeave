# 为 tcm 域生成配图与 Mermaid 图表 — 实施计划（任务分解与优先级）

> 七概念链路：**R（Task 1 勘察）→ F（设计原则已固化于 spec.md）→ 生产（Task 2 生图 / Task 3–7 逐束实施）→ V（Task 8 对抗审查）→ C（Task 9 收尾）**
> 约束：一次只推进一个任务；子代理只读/写 tcm 域与 `doc/_static/bundles/yixue/tcm/` 路径；正文事实表述不得改动。

## [x] Task 1: [R] 逐束视觉勘察与《视觉资产清单》设计 ✅ 2026-09-02
- **交付**：[visual-plan.md](visual-plan.md)（Mermaid 17 张 M1–M17、配图 8 张 I1–I8；事实风险点 6 条）
- **主会话验收**：5 项关键数字抽查（1689 系年/六经条数 178-84-10-8-45-56-7/三品 146-114-103=363/四大经典 1955-1964-1979/难经六部 22+7+18+14+7+13=81）与正文逐字吻合；references/ 零资产；单页资产 ≤2。
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 通读 `doc/bundles/yixue/tcm/` 全域 60 篇文档（域级 index/guide/changelog + classics/ 下 5 束的 index/log、concepts/、examples/、references/），重点读各束 concepts/ 全部与 examples/ 路线图类文档。
  - 产出清单文件 `.trae/specs/standards-tools/add-tcm-bundle-visual-assets/visual-plan.md`，含两部分：
    1. **Mermaid 清单（12–18 张）**：每张给出 `编号 | 目标文件（相对路径） | 插入章节（标题锚点） | 图表类型（flowchart/timeline/flowchart 分层等）| 承载事实要点（逐条，须能在正文中定位）| 备注`。候选方向（最终以正文事实为准）：tcm-overview 谱系三层分层图/四大经典成书时序/托名-文本-辑复三层分离/阅读路径分流；nanjing 81 难结构分组/难经-内经关系/注家谱系时序；shanghan 六经传变框架/版本流变时序/398 条结构；bencaojing 辑本系统谱系/三品分类；waijing 三层分离考辨/1697→1984 流传时序/命门水火关系。
    2. **配图清单（6–10 张）**：每张给出 `文件名（kebab-case）| 存放绝对路径（_static 下）| 生图 prompt（中文，含统一风格后缀：中国传统水墨/工笔淡彩、暖纸色米白基调、素雅、画面无任何文字、无人物、无人体部位、横向构图）| alt 文本（中文描述性）| 插入文件与位置`。域级 1 张 + 5 束各 1 张为保底，增补 0–4 张须说明理由。
  - 清单须遵守配额：单页视觉资产 ≤2；references/ 与存目索引页不安排任何视觉资产；诸说并列的事实在 Mermaid 中同样并列。
  - 同步在 `.trae/specs/standards-tools/README.md` 看板登记本 spec（按该 README 既有表格格式追加一行，状态🔧进行中）。
- **Acceptance Criteria Addressed**: AC-6, NFR-1, NFR-3
- **Test Requirements**:
  - `programmatic` TR-1.1：visual-plan.md 存在；Mermaid 条目 12–18 条、配图条目 6–10 条；每条目标文件路径真实存在（用文件系统核对）。
  - `programmatic` TR-1.2：清单中无任何目标文件落在 references/ 目录（簿录层豁免）；无单页 >2 个视觉资产。
  - `human-judgement` TR-1.3：审查者抽 5 张 Mermaid 候选的"事实要点"，均能在指定正文段落定位依据；配图 prompt 全部含"无文字/无人体"约束且题材为意象类（书影/书案/山水草木/纹样），无医学图解题材。
- **Notes**: 子代理须先读 `projects/awesome-okf-xs/AGENTS.md` 与 tcm 域 `guide.md` 建立全貌；事实要点引用正文时标注文档与章节名，供 V 阶段复核。

## [x] Task 2: [生产-生图] 用 Seedream 批量生成配图 ✅ 2026-09-02
- **交付**：8 张配图全部落盘于 `doc/_static/bundles/yixue/tcm/`（域级 1 + 束级封面 5 + 章节意象 2）。
- **通道说明**：seedream 插件脚本需 `ARK_API_KEY`（本机未配置），改用 TRAE 内置 `GenerateImage` 通道（豆包 Seedream 模型族后端）；实际扩展名为 **.jpg**（非清单初拟的 .png），Markdown 引用一律以 .jpg 为准。
- **主会话验收**：逐张目检——无文字/书法/印章/人物/人体部位/经络脏腑；水墨工笔淡彩、暖纸米白基调统一；I5 草木为写意不可辨识具体品种；8 文件 Glob 确认存在。
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 由主会话使用 GenerateImage（Seedream 插件）按 visual-plan.md 配图清单逐张生成；路径与文件名严格按清单，图片尺寸统一 `landscape_16_9`（封面横向构图）。
  - 每张生成后核验文件落盘存在；生成失败或画面出现文字/人体/医学图解元素时重生成（同一 prompt 最多重试 2 次，仍不合格则回到 Task 1 调整 prompt 或取消该图）。
  - 不在此任务修改任何 Markdown（引用插入在 Task 3–7 进行）。
- **Acceptance Criteria Addressed**: AC-1, NFR-5
- **Test Requirements**:
  - `programmatic` TR-2.1：清单中 6–10 个目标路径全部有图片文件存在且非空、单张 ≤2MB。
  - `human-judgement` TR-2.2：逐张目检——风格统一（水墨淡彩/暖纸色系）、画面无文字、无人物特写、无人体/经络/穴位/脏腑/药草鉴真元素；不合格者已重生成或剔除。
- **Notes**: GenerateImage 为主会话工具（子代理不可用），本任务由主会话直接执行；生图 prompt 以 visual-plan.md 为唯一依据，不即兴发挥。

## [x] Task 3: [生产] 域级入口 + tcm-overview 束视觉实施 ✅ 2026-09-02
- **交付**：I1/I2/I7 三图引用落位（tcm/index.md、tcm-overview/index.md、concepts/02）；M1–M4 四张 Mermaid 落盘（00-genealogy、01-four-classics×2、examples/four-classics-reading-plan）。
- **主会话验收**：图片 .jpg 路径正确、位置在免责声明/简介之后；timeline 与 subgraph 语法合规、代码块无空行、中文标签全双引号；图题为中性引导语；正文与 frontmatter 零改动。
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 按 visual-plan.md 在域级 `index.md`（域介绍段后）与 `classics/tcm-overview/` 相关页面插入：① 封面配图引用（`![alt](/_static/bundles/yixue/tcm/...)`，先例格式）；② 该束分配的全部 Mermaid 代码块（内嵌 ```mermaid，遵循六规则：无空行、中文标签双引号、无 `数字. `/`- ` 列表触发、换行 `<br/>`、subgraph `ID ["标题"]`、边标签 `-->|"标签"|`）。
  - 图前加一句引导语、图后加事实说明句；不改动正文事实表述与 frontmatter/toctree。
  - 自检：对照 `docs/tech/references/development-standards.md` §Mermaid 编码规范逐条核对；本束页面相对链接不受影响。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-6
- **Test Requirements**:
  - `programmatic` TR-3.1：所有图片引用路径对应 Task 2 已生成文件；Mermaid 代码块无空行、无 `\n`、无列表触发格式（grep 可验）。
  - `human-judgement` TR-3.2：Mermaid 事实与 tcm-overview 正文逐条一致；诸说并列处图表并列；插图位置自然、阅读节奏不被打断。
- **Notes**: 实施后子代理报告实际插入的文件清单与图表数量。

## [x] Task 4: [生产] nanjing（难经）束视觉实施 ✅ 2026-09-02
- **交付**：I3 封面落位 nanjing/index.md；M5（六部分区 22+7+18+14+7+13=81，三卷/五卷两说并存）、M6（三层关系）、M7（注家谱系 timeline 七节点）落盘。
- **主会话验收**：M7 timeline 语法合规；事实与正文逐字核对通过（难次区间、注家朝代人名、"补位登记，待补源"原样保留）。
- **Priority**: medium
- **Depends On**: Task 3
- **Description**: 同 Task 3 方式，实施 `classics/nanjing/` 的封面图与分配的 Mermaid（候选：81 难结构分组、难经-内经关系、注家谱系时序）。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-6
- **Test Requirements**:
  - `programmatic` TR-4.1：图片引用路径有效；Mermaid 六规则 grep 检查通过。
  - `human-judgement` TR-4.2：图表事实（81 难分组、成书五说、注家年代顺序）与正文一致，五说并列不武断。
- **Notes**: 独取寸口等涉及人体部位的内容**只用文字与 Mermaid 流程/关系图**，不生成任何人体示意图。

## [x] Task 5: [生产] shanghan-zabinglun（伤寒杂病论）束视觉实施 ✅ 2026-09-02
- **交付**：I4 封面落位；M8（成书流变 timeline）、M9（四版本系统并列+金匮玉函经虚线，无"真本/祖本"裁决措辞）、M10（六经框架 398 条验算 178+84+10+8+45+56+10+7=398）、M11（伤寒金匮同源异流）落盘。
- **主会话验收**：M10 链式边与双 subgraph 语法合规；1065/1066 年份未互换；图题含"编号为现代校注者所加"既有事实说明。
- **Priority**: medium
- **Depends On**: Task 4
- **Description**: 同方式实施 `classics/shanghan-zabinglun/`（候选：六经传变框架、王叔和→宋校订→赵开美版本流变时序、398 条/金匮 25 篇结构）。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-6
- **Test Requirements**:
  - `programmatic` TR-5.1：图片引用路径有效；Mermaid 六规则 grep 检查通过。
  - `human-judgement` TR-5.2：六经框架图与 concepts/03 正文一致；版本系统四说（宋本/成注本/桂林古本/康平本）并列呈现，不宣称"真本"。
- **Notes**: 六经传变图属理论框架图（flowchart），不画人体经络。

## [x] Task 6: [生产] shennong-bencaojing（神农本草经）束视觉实施 ✅ 2026-09-02
- **交付**：I5 封面落位；M12（辑复层累链）、M13（三品理论数 365 与孙辑实计 363 虚线分层、不作弥合）、M14（水银/雄黄两读并列不裁决）落盘。
- **主会话验收**：M13 虚线边标签"孙星衍辑本实计"正确区分两层数字；M14 四节点汇聚 CONC"不作裁决"；事实与正文逐字一致。
- **Priority**: medium
- **Depends On**: Task 5
- **Description**: 同方式实施 `classics/shennong-bencaojing/`（候选：卢复/孙星衍/顾观光/森立之辑本系统谱系、上中下三品分类、序录结构）。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-6
- **Test Requirements**:
  - `programmatic` TR-6.1：图片引用路径有效；Mermaid 六规则 grep 检查通过。
  - `human-judgement` TR-6.2：三品分类（上经 146/中经 114/下经 103、363 条口径）与正文数字一致；辑本四系统表述不构拟。
- **Notes**: 本草题材配图只作"草本植物水墨意象"（写意、非鉴真图谱），不出现可辨识为具体药材基原的写实描绘。

## [x] Task 7: [生产] waijing-weiyan（外经微言）束视觉实施 ✅ 2026-09-02
- **交付**：I6 束封面、I8 顺逆山水意象图落位；M15（流传时序 timeline，成书系年"约1689年前后·无定论"，无 1697/1698 混入）、M16（九卷主题地图）、M17（命门承应谱系，三章篇号 36/37/39，《素问》边标签含"翻转"）落盘。
- **主会话验收**：M17 最高风险点（篇号非连续、素问原指心→翻转指命门）落地正确。
- **Priority**: medium
- **Depends On**: Task 6
- **Description**: 同方式实施 `classics/waijing-weiyan/`（候选：著录/托名/文本三层分离考辨、《汉志》著录→早佚→1697 陈士铎述→1980 天津抄本→1984 影印流传时序、命门水火关系、九卷八十一篇结构）。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-6
- **Test Requirements**:
  - `programmatic` TR-7.1：图片引用路径有效；Mermaid 六规则 grep 检查通过。
  - `human-judgement` TR-7.2：真伪两派在图表中并列不裁决；年代节点与 concepts/01、03 正文一致。
- **Notes**: 本束含 facts.md/insights.md（锚点组结构），注意不遗漏这两个文件中的合适插图点（若清单安排）。

## [x] Task 8: [V] 对抗审查与全量构建验证（黑盒）✅ 2026-09-02
- **交付**：[v-review-report.md](v-review-report.md)——A 程序化合规 4/4 PASS（17 mermaid 六规则机检、8 jpg 存在且 333–555KB、references 零资产、git 变更集纯净）；B 事实对抗 8/8 PASS（6 大风险点逐字核验）；C Sphinx 构建 tcm 域零错误零告警，产物 17 mermaid 节点 + 8 img 标签分布一致；utf8/toctrees/bundles 三质量门全绿。
- **域外观察（非本任务范围）**：yishu/vocal 声乐束有 1 WARNING + 1 ERROR（并行会话文件），需转该束会话处理。
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 由独立子代理（未参与实施）执行黑盒验证：
    1. **事实对抗**：逐张 Mermaid 核对节点/边/分组事实与同束正文，列出任何"正文无据/武断裁决/因果曲解/数字不符"问题；
    2. **边界对抗**：逐张配图核查无文字/无人体/无医学图解、alt 文本合规、免责声明未被削弱；
    3. **工程验证**：在 `projects/awesome-okf-xs/` 下运行 `invoke build`（或 `sphinx-build -b html doc doc/_build/html`）确认零警告零错误；运行 `invoke gates.all`（utf8/toctrees/bundles）全绿；运行根目录 `python check_mermaid.py`（若该脚本不覆盖子模块路径，则对子模块内 mermaid 块做六规则 grep 复核）；
    4. **配额核对**：统计配图总数（6–10）、Mermaid 总数（12–18）、单页 ≤2、references/ 零插图。
  - 发现问题输出分级问题清单（P0 阻断/P1 应修/P2 建议）；P0/P1 由实施侧修复后回到本任务复验，最多 3 轮。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6, NFR-4
- **Test Requirements**:
  - `programmatic` TR-8.1：构建命令退出码 0 且输出无 mermaid/image/undefined 警告；gates 三门全绿；图片引用无断链（构建产物中对应 _static 文件存在）。
  - `human-judgement` TR-8.2：P0/P1 问题清零；Mermaid 节点事实可溯源率 100%；配图边界 100% 合规。
- **Notes**: 审查子代理须先读 spec.md 的 Non-Goals 与 F 分工表作为审查依据；构建环境若缺 invoke，按 spec A1 兜底方案执行并在报告中说明。

## [x] Task 9: [C] 变更日志收尾与变更集核对 ✅ 2026-09-02
- **交付**：tcm/changelog.md 追加 v1.2.0 条目（纯追加 +20/−0）；5 束 log.md 各追加 2026-09-02 条目（+9~11 行/束，删除行全 0）；checklist 24 检查点全勾选；standards-tools 看板更新为 ✅ 完成 100%（18/27）。
- **变更集核对**：本任务变更集 = tcm 域 24 个 .md（图表嵌入 + changelog/log 登记）+ `doc/_static/bundles/yixue/tcm/` 8 张 jpg；git status 中另有并行会话对其他域（liaoyu/vocal/daoyi/neijing/ishinpo/yangsheng 等）的改动，按共享工作区竞态纪律只报告不处置。
- **提交建议**（未执行 commit）：见主会话最终报告中的原子提交草案。
- **Priority**: medium
- **Depends On**: Task 8
- **Description**:
  - 更新 `doc/bundles/yixue/tcm/changelog.md`：新增 v1.2.0 条目（视觉资产增强：配图 N 张、Mermaid N 张、验证证据）。
  - 更新 5 束各自 `log.md`：登记本次视觉资产变更（日期 2026-09-02、变更类型、涉及文件）。
  - 运行 `git -C projects/awesome-okf-xs status` 与 `git diff --stat` 核对变更集（仅应含 tcm 域 .md、`doc/_static/bundles/yixue/tcm/` 图片、changelog/log）；产出变更文件清单与原子提交建议（提交信息草案，Conventional Commits 中文主体），**不执行 commit**（并行会话竞态防护 + 用户未要求提交）。
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-9.1：changelog 与 5 份 log 均含本次变更记录；git status 变更集无超出 tcm 域与 _static/yixue/tcm 的路径。
  - `human-judgement` TR-9.2：变更集报告完整、提交建议符合原子提交（单一职责：docs(bundles) 视觉资产增强）。
- **Notes**: 若发现并行会话混入的无关改动，只报告不处置（遵循共享工作区 git 竞态纪律）。
