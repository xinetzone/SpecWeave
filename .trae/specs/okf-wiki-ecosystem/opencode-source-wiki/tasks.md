# OpenCode 2.0.32 源码 Wiki 增量扩展 - Implementation Plan

> 方法论链路：阶段 0 信源预检 → R 事实采集 → I 洞察与知识地图 → E 信源先行、分批生成 → V 独立验证 → C 模式适用性评估。
> 当前状态：用户已批准 `spec.md` 与本任务队列；按依赖顺序实施中。
> 目标：增量扩展既有 `projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/opencode/`，不新建重复 bundle。
> 源码锚点：`anomalyco/opencode@6ec56821d63100fe5bda45b759364f561c56b359`（根包版本 2.0.32，实施时复核）。

## Task 1: 阶段 0 - 固定信源与盘点既有基线
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 复核 OpenCode remote、HEAD、工作树状态、根包版本及固定 commit 可访问性。
  - 将本地 checkout 仅作为读取位置；规划中所有长期来源链接均使用固定 commit 的 GitHub URL。
  - 复核现有 bundle 文件、最大事实编号、概念/示例编号、各级 index/toctree、根元数据和日志。
  - 对照旧 `references/source.md` 与 `log.md` 标记的 2026-08-23 快照边界；列明版本敏感内容但不提前改写。
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `rule` TR-1.1: 记录的 HEAD 与 `git rev-parse HEAD` 一致，工作树状态有命令证据，根包版本与该 commit 的 `package.json` 一致。
  - `rule` TR-1.2: bundle 基线清单逐项以磁盘现状为准，并确认旧事实最大编号及新文档续接编号。
  - `rule` TR-1.3: 源码引用方案不包含本机绝对路径、`file:///` 或浮动分支引用。
- **Completion Evidence**:
  - TR-1.1: OpenCode HEAD 与批准的 `6ec56821d63100fe5bda45b759364f561c56b359` 一致，分支 `dev` 与 `origin/dev` 同步且工作树干净；remote 为 `git@github.com:anomalyco/opencode.git`；该 commit 的根 `package.json` 声明版本 `2.0.32`，且 commit 可由本地 Git 对象库解析。
  - TR-1.2: awesome-okf-xs 工作树干净；既有 bundle 有 80 条事实（F-001～F-080）、5 篇概念（00～04）、1 篇示例（01）、1 篇源码参考；根及 spec/concepts/examples/references 索引已检查，父级 `ai-agent/index.md` 已挂载 `opencode/index`。旧根 index 为 `0.1.0`，日志标记旧快照日期为 2026-08-23。
  - TR-1.3: 新信源采用固定 commit 的 GitHub blob URL；本机绝对路径只用于读取，不进入面向读者的新文档。旧日志中的本地路径保留为历史记录，不作为活动信源。
  - G0: 以不可变 commit 坐标登记信源；不新增或移动源码 checkout，不修改 OpenCode 源码。

## Task 2: R - 建立包地图并采集版本化源码事实
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 从根工作区配置与实际包清单建立完整包/子系统目录图，逐项记录纳入、合并或排除的依据。
  - 按层深读各主要子系统的入口、接口与代表性实现，重点追踪包边界和至少一条端到端执行/数据流。
  - 检查 CLI/运行时、会话与 Agent 执行、模型/provider、工具与权限、MCP/插件、Server/API/Protocol/Client SDK、TUI/UI、桌面端/Web、持久化、构建发布和测试边界在该快照中的实际存在与关系。
  - 在目标 bundle 的 `spec/facts-2.0.32.md` 中记录新增 F-081 起的编号事实；为数量事实保留可重复计数脚本或命令、对象定义和统计口径。
  - 事实只记录源码可证实内容；架构解释和价值判断留给 I 阶段。
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `rule` TR-2.1: 新事实编号从基线最大编号后续接且无重复；每条均有路径、commit 固定来源和可定位证据。
  - `rule` TR-2.2: 包地图覆盖根工作区配置列出的全部包；未纳入深读的包仍在地图中出现并注明覆盖方式。
  - `rule` TR-2.3: 数量类事实不以人工枚举作为唯一证据，计数对象与口径明确。
  - `rubric` TR-2.4: 事实覆盖度；0 = 仅零散文件，1 = 包地图不完整，2 = 全包地图与主要子系统事实齐全，3 = 达到 2 且关键调用路径和边界均有多点源码证据；阈值 `>= 2`；证据为事实清单与覆盖矩阵。
- **Completion Evidence**:
  - TR-2.1: `facts-2.0.32.md` 包含 F-081～F-114 共 34 条连续且唯一编号事实；对固定 commit 的 143 个 GitHub 源码引用逐个核对文件存在与行号上界，无无效引用。修正了 F-092 插件存储命名空间的 UTF-16 code unit 编码描述，并将 F-105 的 SDK 生产依赖与开发依赖分列。
  - TR-2.2: 39 行覆盖矩阵与五个 workspace glob 实际匹配到的 39 个 package manifest 名称集合完全一致；逐项标注包角色线索及“深读”6 个、“入口/接口读取”4 个、“清单级”29 个的覆盖等级和未深读边界。`github/package.json` 与 `sdks/vscode/package.json` 作为不匹配 workspace glob 的边界另行说明。
  - TR-2.3: workspace 清单以五个 glob 分组记录 29/1/4/2/3 个 manifest，并用独立 Python `Path.glob` 重计总数与名称集合；迁移目录的 50 个 `.ts` 文件及生成文件中的 50 个默认迁移导入另有采集口径。会话 endpoint 总量未作断言。
  - TR-2.4: 事实覆盖度 rubric 得分 **3/3**。证据包括 workspace 包边界、core 会话协调至 LLM/tool/persistence 路径、Protocol→Server→Client/SDK 接口边界、CLI/UI/desktop 入口，以及 test/publish workflow；各路径均有固定 commit 的多点源码引用，且矩阵显式区分深读、入口读取与清单级覆盖。

## Task 3: I - 提炼洞察并确定增量知识地图
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 基于版本化事实提炼 3～5 条核心架构洞察，确保各条关注不同层面。
  - 为每条洞察记录陈述、F 编号证据、反常识点和对读者/文档组织的行动含义。
  - 将新概念、示例与参考文档按学习依赖排序，注明每篇覆盖的事实编号及与现有章节的关系。
  - 将洞察和知识地图写入 `spec/insights-2.0.32.md`；避免仅为追求篇数拆分主题。
- **Acceptance Criteria Addressed**: AC-3, AC-5
- **Test Requirements**:
  - `rule` TR-3.1: 有 3～5 条洞察，且每条具备完整四元组并引用本轮事实编号。
  - `rule` TR-3.2: 知识地图中的每篇新增文档均有主题、学习顺序、事实覆盖和来源规划。
  - `rubric` TR-3.3: 学习路径质量；0 = 无路径，1 = 排序无依据，2 = 从总览到机制递进且章节职责清楚，3 = 达到 2 且新旧快照关系和读者分层明确；阈值 `>= 2`；证据为洞察文件和知识地图。
- **Completion Evidence**:
  - TR-3.1: `spec/insights-2.0.32.md` 包含 5 条互不重复的洞察；每条均有陈述、事实编号证据、反常识点和行动建议。机械核对发现 40 处事实编号引用，均可在本轮 F-081～F-114 清单中找到。
  - TR-3.2: 学习地图列出 5 篇概念和 1 篇示例，逐篇记录顺序、主题、事实覆盖、前置关系及固定信源登记计划；旧概念/示例编号与历史快照关系明确。
  - TR-3.3: 学习路径质量 rubric 得分 **3/3**。路径从 workspace 包图进入会话主链，再分解模型/工具与 API 边界，最后收束到产品入口/工程交付，并以 prompt 追踪示例串联；旧版章节保留且明确了新旧快照边界。

## Task 4: E - 先登记固定源码信源
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 新增 `references/source-code-map-2.0.32.md`，记录上游仓库、固定 commit、已核验包版本、工作区地图、关键源码路径与事实编号映射。
  - 将来源 URL 固定到指定 commit；不把本机 checkout 路径写入长期文档。
  - 先创建信源文件，再生成引用它的概念、示例和事实文档；参考目录索引在全体内容定稿后统一更新。
- **Acceptance Criteria Addressed**: AC-2, AC-4
- **Test Requirements**:
  - `rule` TR-4.1: 版本化信源登记先于引用它的新增教程文件落盘，且每个引用均指向已存在的登记项。
  - `rule` TR-4.2: 仓库与 commit 坐标、版本声明及文件路径可对照 GitHub 固定快照核验。
- **Completion Evidence**:
  - TR-4.1: 已先创建 `references/source-code-map-2.0.32.md`；当前尚未写入概念或示例文件。洞察地图为后续各篇规划了 `/references/source-code-map-2.0.32.md` 来源。
  - TR-4.2: 登记文件记录仓库、完整固定 commit、根包版本和 workspace 范围；其中 27 个 commit-pinned GitHub 文件链接已核对存在，引用路径不含本机绝对路径或浮动分支。

## Task 5: E - 分批撰写概念与示例
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3, Task 4
- **Description**:
  - 依据已批准的知识地图，新增 `concepts/` 文档并从当前最大编号之后续接；新增 `examples/` 文档亦续接现有编号。
  - 每批最多生成 7 个文件；每篇文档聚焦一个主题，引用相关 F 编号及固定源码信源。
  - 覆盖包职责、主要组件协作、关键边界和端到端执行路径；对旧版已有主题采用增量补充，不复制整篇旧内容。
  - 对版本敏感的旧内容，只在源码对照确认差异后进行最小修订，并把修订理由与证据记入 `log.md`。
  - 代码/API 示例以源码和测试事实为准；不可运行的片段明确标注为示意。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-5
- **Test Requirements**:
  - `rule` TR-5.1: 新文件编号不重排现有文档，且每批文件数不超过 7。
  - `rule` TR-5.2: 新文档中的技术断言能回溯到本轮事实/信源；无来源支持的断言被删除或明确限定。
  - `rule` TR-5.3: 概念、示例文件均使用合规 YAML frontmatter，含准确的 `sources` 和 `type`。
  - `rubric` TR-5.4: 教程质量；0 = 与源码矛盾或无法学习，1 = 章节存在但事实链/路径断裂，2 = 架构、示例与证据链一致且可循序学习，3 = 达到 2 且对版本边界、限制和反直觉设计解释充分；阈值 `>= 2`；证据为新文档和 F 编号映射。
- **Completion Evidence**:
  - TR-5.1: 按学习地图新增 5 篇连续概念文档（`05`～`09`）及示例 `02`，旧 `00`～`04` 与示例 `01` 未重排；本轮 E 批次共 6 个文件，未超过 7 个上限。
  - TR-5.2: 新文档覆盖包图、prompt 接纳与执行生命周期、模型/工具/MCP/插件边界、Protocol/Server/Client/SDK 契约、产品入口与交付，以及一条 session prompt 源码追踪。每篇均标注关联 F 编号和固定版本边界；所引用的事实编号均可在 `facts-2.0.32.md` 中找到。
  - TR-5.3: 6 篇文档均包含 `type`、`title`、`description`、`tags`、`generated`、`verified`、`status`、`stale_after`、`sources`；`sources` 均指向已存在的 `/references/source-code-map-2.0.32.md`。机械核对确认 bundle 内部链接目标全部存在，且每篇均有“相关概念”章节。
  - TR-5.4: E 阶段内容 rubric 暂评 **3/3**：各篇沿 F 编号回溯固定 commit，说明 1.18.21 与 2.0.32 的快照边界，明确 manifest 清点不等同实现深读、`resume: false` 不等于输入永不执行、tool-call 不等于副作用已完成；示例标注为源码导读而非可运行代码。独立 V 阶段仍按 Task 7 执行。

## Task 6: E - 收尾导航、元数据和版本日志
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 在全部内容文档定稿后，最后更新根 index、`concepts/`、`examples/`、`references/`、`spec/` 索引及 `log.md`。
  - 根和受影响的子目录 index 同步更新人类可读清单与隐藏 `{toctree}`，不遗漏 F、洞察或新参考文档。
  - 更新 bundle 描述及版本元数据，使其同时表达旧基线和本轮新增快照；不改写既有日志历史条目。
  - 仅当门禁证明现有父级索引未挂载该 bundle 时，才在最小必要范围补入口，并先检查该文件是否已有他人变更。
- **Acceptance Criteria Addressed**: AC-1, AC-4
- **Test Requirements**:
  - `rule` TR-6.1: 每个受影响 index 同时具有完整人类导航和 toctree 条目；索引与实际文件集合相等。
  - `rule` TR-6.2: `log.md` 以追加方式记录本轮日期、来源坐标、文件增量和已验证的旧内容修订。
  - `rule` TR-6.3: 未修改无关父索引；若必须修复导航入口，变更仅限该入口且有门禁证据。
- **Completion Evidence**:
  - TR-6.1: 根 index 与 `concepts/`、`examples/`、`references/`、`spec/` 四个索引均已更新人类导航和 `{toctree}`；机械比对确认 concepts 10 篇、examples 2 篇、references 2 篇、spec 4 篇内容文档均被对应索引收录。根 toctree 仍挂载四个目录索引与 `log`。
  - TR-6.2: `log.md` 顶部追加 `0.2.0 — 2026-10-20` 条目，记录固定 commit、F-081～F-114、六篇教程、源码地图、导航更新和新旧快照边界；原 `0.1.0` 历史条目保留。
  - TR-6.3: bundle 根 metadata 更新至 `0.2.0` 并列出 1.18.21 与 2.0.32 两个源码快照。父级 `ai-agent/index.md` 原已挂载 `opencode/index`，本轮未修改父级或其他无关索引。

## Task 7: V - 独立核验事实、链接、数量与构建
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 对新增文档中引用的关键类、函数、方法、命令、配置键及代码示例执行源码存在性/签名核验；必要时对容易被误猜的符号做负向搜索。
  - 以独立于 R 阶段的方法复核所有数量陈述，并将不一致修复为有统计口径的值。
  - 检查 frontmatter、sources、bundle-relative 链接、各级 index/toctree、编号及新旧快照边界。
  - 运行 awesome-okf-xs 的 `invoke gates.utf8`、`invoke gates.toctrees`、`invoke gates.bundles` 和 `invoke build`；记录失败项归属，不修复无关历史欠债。
  - 将验证证据和修复记录整理到 Spec 任务证据中，供 Review 阶段复核。
- **Acceptance Criteria Addressed**: AC-2, AC-4, AC-6
- **Test Requirements**:
  - `rule` TR-7.1: 新增教程引用的关键 API/命令/配置项经固定 commit 检索核验，无虚构或未解释的不一致。
  - `rule` TR-7.2: 数量断言完成独立复核并标注统计口径；不一致项已修订且留痕。
  - `rule` TR-7.3: bundle 新增内容无断链、frontmatter 错误、toctree 遗漏或编号冲突。
  - `rule` TR-7.4: 四项项目质量命令均已运行并记录退出结果；失败有明确分类，目标 bundle 不引入新的失败项。
- **Verification Notes**:
  - 已重新核验 `external/dao/anomalyco/opencode` 的 HEAD 为批准的 `6ec56821d63100fe5bda45b759364f561c56b359`，根 `package.json` 版本为 `2.0.32`，源码仓库工作树干净。
  - 固定 commit 符号核验覆盖 `admission.admit`、`execution.wake`、`llm.stream`、`SessionRunCoordinator`、`permission.assert`、`ClientApi`、`DesktopRpcs`、`PluginHost.make` 及插件 ID 编码；此前对 143 个固定 commit 源码链接已核对文件存在和行号上界。
  - 独立计数复核确认五个 workspace glob 命中 39 个 manifest（29/1/4/2/3），路径/包名集合与事实矩阵相等；另核对迁移文件和默认导入各 50 项。
  - 机械编号比对确认 34 个事实条目连续覆盖 F-081～F-114；新增 6 篇教程引用均在本轮事实集合内，未发现浮动分支源码链接。6 篇新增教程 frontmatter、sources、相关概念章节和内部链接检查通过；OpenCode bundle 专项 toctree 检查通过。
  - `conda run -n py314 invoke gates.utf8` 通过（11,908 个文件）；`invoke gates.bundles` 通过（9 域 / 63 组 / 653 束）。`invoke gates.toctrees` 非零退出，11 项均指向并行新增的 `doc/bundles/jishu/ai/frameworks/xerj/`，与 OpenCode bundle 无关。
  - 正式 `conda run -n py314 invoke build` 完成，后台任务退出码为 0；最终日志显示 Sphinx 构建成功、HTML 输出位于 `_build/html`，全站汇总 325 条警告。按 `WARNING:`/`ERROR:` 与 OpenCode 路径交叉过滤为 0 条；本轮 OpenCode 的 7 个新增 HTML 页面均存在。
  - 本任务执行期间 `awesome-okf-xs` 工作树另有并行新增的 XERJ、OpenTUI、SST/IaC bundle 和父级索引变化；对照 diff 确认为其他主题内容，未由本任务修改。OpenCode 源码仓库仍在批准 commit 且工作树干净。本任务未执行 commit 或 push；Review R1 后续发现既有并行聚合提交 `7a219626fdeb0f9b9cb2f12e47666074ee550323` 与父仓库指针提交 `baedea3361db75749a34cfcd812f362d92546bf2`，Issue I-1 已按用户明确决定记录为例外。

## Task 8: C - 评估可复用模式并完成任务闭环
- **Status**: `completed`
- **Priority**: low
- **Depends On**: Task 7
- **Description**:
  - 回顾本轮 R/I/E/V 的实际执行，判断是否产生超出既有源码转 Wiki 工作流的、可复用且有证据的新模式。
  - 将结论记入任务完成证据与用户交付摘要；若没有新模式，明确记录“本轮无须新增方法论资产”。
  - 不在此任务中向 SpecWeave 根 `docs/` 或 `.agents/` 增加方法论资产；若发现值得沉淀的候选，另行提案并等待批准。
  - 不执行 git commit 或 push。
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `rule` TR-8.1: C 阶段记录有“新增模式/无新增模式”的明确判断及其事实依据。
  - `rule` TR-8.2: 目标 bundle 以外未新增方法论文件；本任务没有执行新的提交或推送，且既有并行聚合提交仅按用户明确接受的例外记录。
- **Completion Evidence**:
  - TR-8.1: 本轮按既有源码转 OKF Wiki 链路执行 R→I→E→V→C；包地图分层覆盖、固定 commit 事实映射、增量快照边界和独立数量复核均属于当前工作流在大型 monorepo 上的具体应用，未形成超出既有流程、具备独立触发条件与步骤的新方法。结论：**无须新增方法论资产**。
  - TR-8.2: 本轮未在目标 bundle 之外新增方法论文件；本任务未执行新的 commit 或 push。Review R1 查明的并行聚合提交及父仓库指针提交按用户后续明确接受的例外处理，相关并行 bundle 与父级索引未由本任务修改。

## Issue I-1: Reconcile the parallel aggregate commit with the no-commit constraint
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Discovered By**: Review R1
- **Description**:
  - Independent Review found that submodule commit `7a219626fdeb0f9b9cb2f12e47666074ee550323` includes this OpenCode bundle together with parallel XERJ, SST/IaC, and OpenTUI work. Parent commit `baedea3361db75749a34cfcd812f362d92546bf2` advances the submodule pointer to that commit.
  - The submodule `main` is ahead of `origin/main` by 1 and the parent `main` is ahead of `origin/main` by 7. No push evidence was found. The aggregate commit is already present in shared history; reverting, resetting, or selectively rewriting it could affect unrelated parallel work.
  - No Git history or remote state has been changed during Review.
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `rule` TR-I-1.1: The user's explicit decision is recorded against the exact existing aggregate and pointer commit SHAs; no new commit, push, reset, revert, or history rewrite is performed as part of reconciling the issue.
- **Completion Evidence**:
  - TR-I-1.1: The user explicitly chose “接受为例外（推荐）” for subproject commit `7a219626fdeb0f9b9cb2f12e47666074ee550323` and parent pointer commit `baedea3361db75749a34cfcd812f362d92546bf2`. `spec.md` now narrows the exception to these already-existing commits and preserves the prohibition on further commits, pushes, rollback, reset, or history rewriting without separate authorization. No Git history or remote state was changed while closing this issue.

## Task Dependencies

```text
Task 1 (G0 baseline)
  -> Task 2 (R facts)
  -> Task 3 (I insights + knowledge map)
  -> Task 4 (E source registration)
  -> Task 5 (E concepts/examples, batches <= 7)
  -> Task 6 (E indexes/log last)
  -> Task 7 (V verification)
  -> Task 8 (C applicability assessment)
  -> Spec Mode Review gate
```

## Spec Mode Review Gate

只有 Task 1～8 全部完成且无 `pending`、`in_progress` 或 `blocked` 项后，才进入 Review 阶段并创建 `review.md`。届时由一个全新上下文执行一次只读独立审查，逐条核验 `spec.md` 中的 AC 与本文件中的 TR，rubric 均须达到阈值；有可行动发现时先回到 Implement 并登记修复项，不得以实施者自验代替最终 Review。
