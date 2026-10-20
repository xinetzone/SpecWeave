# OpenCode 2.0.32 源码 Wiki 增量扩展 - Independent Review

## Review Checkpoints

- [x] CP-R1: 目标 bundle 与源码快照符合批准范围；既有提交例外未扩大
  - **Type**: `rule`
  - **Covers**: AC-1, TR-1.1, TR-1.2
  - **Evidence**: R2 `pass`。源码 checkout 仍为批准的固定 commit 且工作树干净；AC-1 已明确接受既存子项目聚合提交 `7a219626fdeb0f9b9cb2f12e47666074ee550323` 和父仓库指针提交 `baedea3361db75749a34cfcd812f362d92546bf2` 作为唯一例外。未发现例外之外的后续本地提交；本轮未执行 Git 历史或远端操作。

- [x] CP-R2: 固定 commit 的来源、事实编号、关键源码符号与引用均可核验
  - **Type**: `rule`
  - **Covers**: AC-2, TR-1.3, TR-2.1, TR-4.2, TR-7.1
  - **Evidence**: `pass`。源码仓 HEAD 为 `6ec56821d63100fe5bda45b759364f561c56b359`，根包版本为 `2.0.32`；独立核验确认 F-081～F-114 连续，源码地图 171 条固定 commit 引用涉及 74 个源码文件，文件与行号边界有效。核验记录见 [facts](../../../../projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/opencode/spec/facts-2.0.32.md) 与 [source map](../../../../projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/opencode/references/source-code-map-2.0.32.md)。

- [x] CP-R3: workspace 全量清点、数量口径和覆盖分层有独立证据
  - **Type**: `rule`
  - **Covers**: AC-3, TR-2.2, TR-2.3
  - **Evidence**: `pass`。独立计数核对 39 个包（深读 6、入口/接口读取 4、清单级 29），五组 glob 为 29/1/4/2/3；迁移文件和默认导入各 50。口径与边界见 `facts-2.0.32.md`。

- [x] CP-U1: monorepo 工作区与核心架构覆盖度达到要求
  - **Type**: `rubric`
  - **Covers**: AC-3, TR-2.4
  - **Scale**: 0-3
  - **Anchors**: 0 = 仅单包或旧版描述；1 = 包图不全或缺少关键调用路径；2 = 完整包图、主要子系统和端到端路径齐全；3 = 达到 2，且接口边界、版本差异和未覆盖区域均有证据说明
  - **Pass Threshold**: >= 2
  - **Evidence**: `pass`，**3/3**。包地图、会话端到端执行路径、接口边界、版本差异与覆盖限制均有事实支撑；示例特别限定 `resume: false` 的含义。见 [concepts index](../../../../projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/opencode/concepts/index.md)、[insights](../../../../projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/opencode/spec/insights-2.0.32.md)。

- [x] CP-R4: 洞察四元组与学习地图完整、排序有据且新旧快照边界清楚
  - **Type**: `rule`
  - **Covers**: TR-3.1, TR-3.2
  - **Evidence**: `pass`。洞察与知识地图具备要求的证据和学习次序；旧 F-001～F-080 与新 F-081～F-114 分层明确。见 [insights](../../../../projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/opencode/spec/insights-2.0.32.md) 与 bundle 的 `spec/index.md`。

- [x] CP-U2: 教程学习路径、事实表达和读者可验证性达到要求
  - **Type**: `rubric`
  - **Covers**: AC-5, TR-3.3, TR-5.4
  - **Scale**: 0-3
  - **Anchors**: 0 = 零散且无法学习；1 = 章节存在但边界或证据链不清；2 = 从全景到机制递进、主题独立且可回溯事实；3 = 达到 2，且示例、反常识说明和局限帮助读者验证与迁移
  - **Pass Threshold**: >= 2
  - **Evidence**: `pass`，**3/3**。内容从全景递进到执行机制与 API/扩展边界；教程可回溯事实，示例注明为源码导读并保留验证限制。见 [concepts index](../../../../projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/opencode/concepts/index.md) 与 [prompt trace](../../../../projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/opencode/examples/02-session-prompt-trace.md)。

- [x] CP-R5: 源码地图先于教程创建，登记坐标和引用路径准确
  - **Type**: `rule`
  - **Covers**: TR-4.1
  - **Evidence**: `pass`。源码地图登记的仓库、commit、版本和文件路径可核验；任务日志记录了先登记信源、后生成教程的顺序。见 [source map](../../../../projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/opencode/references/source-code-map-2.0.32.md)。

- [x] CP-R6: 新文档编号、事实追溯、frontmatter、内部链接和数量复核无遗漏
  - **Type**: `rule`
  - **Covers**: AC-2, AC-4, AC-5, TR-5.1, TR-5.2, TR-5.3, TR-7.2
  - **Evidence**: `pass`。新增章节/示例编号连续，frontmatter 与 `sources` 合规，内部链接可达；数量声明有独立复核口径。见目标 bundle `concepts/05`～`09`、`examples/02` 和 facts 文件。

- [x] CP-R7: 根/子索引、toctree、更新日志与父级入口符合增量边界
  - **Type**: `rule`
  - **Covers**: AC-4, TR-6.1, TR-6.2, TR-6.3, TR-7.3
  - **Evidence**: `pass`。目标 bundle 各索引、toctree 和日志一致，父级入口原已存在。早期全仓 toctree 运行报告的 11 项 XERJ 问题属于并行 WIP；该并行提交完成后，Reviewer 对当前子项目快照执行 `python -B scripts/check-toctrees.py` 通过。

- [x] CP-R8: 四项质量命令与 Sphinx 构建结果可复核，失败已正确归因
  - **Type**: `rule`
  - **Covers**: AC-6, TR-7.4
  - **Evidence**: `pass`。`invoke gates.utf8` 与 `invoke gates.bundles` 通过；全仓 toctree 曾因并行 XERJ 未完成而报告 11 项，当前快照的 `python -B scripts/check-toctrees.py` 通过。正式 `conda run -n py314 invoke build` 退出码 0，Sphinx 报告构建成功、325 条全站警告、OpenCode 路径 0 条诊断。

- [x] CP-R9: C 阶段对新增可复用模式作出明确且有事实依据的判断
  - **Type**: `rule`
  - **Covers**: AC-6, TR-8.1
  - **Evidence**: `pass`。本轮是既有源码转 OKF Wiki 工作流在大型 monorepo 上的具体应用，没有证据表明需要新增独立方法论资产；判断记录见 [tasks.md](tasks.md) 的 TR-8.1。

- [x] CP-R10: 目标 bundle 外无本任务新增方法论资产；提交例外之外无新增提交
  - **Type**: `rule`
  - **Covers**: AC-1, AC-6, TR-8.2
  - **Evidence**: R2 `pass`。未发现目标 bundle 外由本任务新增的方法论资产，也未发现两个已接受 SHA 以外的后续本地提交。本轮没有执行提交或推送；未 fetch，因此不对实时远端状态作断言。

- [x] CP-R11: 用户接受的提交例外范围准确且未扩大
  - **Type**: `rule`
  - **Covers**: AC-1, AC-6, TR-I-1.1
  - **Evidence**: R2 `pass`。`spec.md` 与 Issue I-1 均记录用户“接受为例外（推荐）”的决定，并对应相同的子项目提交和父仓库指针提交完整 SHA；文字同时禁止未经单独授权的后续提交、推送、回滚、重置或历史改写。

## Review History

### Review R1
- **Result**: `fail`
- **Evidence**: 全新只读上下文完成 AC-1～AC-6、TR-1.1～TR-8.2 和两项 rubric 的独立审查。CP-R1 与 CP-R10 因已存在的并行聚合提交而失败；其他规则检查点通过，AC-3 与 AC-5 均为 3/3。实施会话未执行 commit、push、reset 或 revert。
- **Findings**:
  - **F-R1**: `actionable`; P1; CP-R1/CP-R10。OpenCode bundle 已包含在子项目提交 `7a219626fdeb0f9b9cb2f12e47666074ee550323` 中，主仓提交 `baedea3361db75749a34cfcd812f362d92546bf2` 已更新子模块指针，与批准的 no-commit 约束冲突。复现：`git -C projects/awesome-okf-xs show --name-status 7a219626`；预期输出包含 `doc/bundles/.../ai-agent/opencode/` 文件。此发现不构成撤销或重写其他并行内容的授权。
- **Recommended Issues**: [Issue I-1](tasks.md)；等待用户明确决定是否接受现有聚合提交作为例外。未获授权前不改写 Git 历史、不推送、不创建新提交。

### Review R2
- **Result**: `pass`
- **Checks Performed**:
  - 以独立只读上下文逐项核对 AC-1～AC-6、TR-1.1～TR-8.2 与 TR-I-1.1；确认 6/6 AC、26/26 TR 均映射到 CP-R1～CP-R11。
  - 独立核对固定源码快照、事实编号与源码引用：F-081～F-114 共 34 条连续且唯一；39 个 workspace manifest 的分组计数为 29/1/4/2/3；171 条固定 commit 源码引用涉及 74 个文件，文件与行号边界有效。
  - 检查新增教程的编号、frontmatter、事实引用和本地链接；36 个本地链接无断链。只读 toctree、UTF-8（11,922 个文件）和 bundle 总索引（9 域/63 组/654 束）门禁通过。
  - 核对 OpenCode 源码 HEAD、包版本、工作树状态，以及两个例外提交的当前本地位置；未执行 fetch，故不把本地远端跟踪状态解释为实时远端状态。
- **Evidence**:
  - CP-R1～CP-R11 均通过；CP-U1（AC-3/TR-2.4）得分 **3/3**，CP-U2（AC-5/TR-3.3/TR-5.4）得分 **3/3**。
  - Sphinx 未在 R2 重跑；R2 采用 Task 7 中已记录的 `conda run -n py314 invoke build` 成功退出（0）证据。构建记录含 325 条全站警告，OpenCode 路径诊断为 0。
  - Issue I-1 已依据用户明确决定关闭；接受范围仅为 `7a219626fdeb0f9b9cb2f12e47666074ee550323` 与 `baedea3361db75749a34cfcd812f362d92546bf2`。未发现例外之外的新增本地提交或方法论资产。
- **Checkpoint Results**:
  - CP-R1～CP-R7、CP-R9～CP-R11 (`rule`): `pass`
  - CP-R8 (`rule`): `pass`; 使用 Task 7 中已记录的构建结果，R2 未重新构建
  - CP-U1 (`rubric`): `pass`; score **3/3**
  - CP-U2 (`rubric`): `pass`; score **3/3**
- **Findings**: 无可行动发现。
