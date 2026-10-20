---
id: tasks
title: Kaggle SAE OKF Wiki 教程实施计划
created: 2026-10-19
---

# Kaggle SAE OKF Wiki 教程实施计划

## Task 1: 建立来源事实登记并核验关键声明

- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 重读 Kaggle 博文和官方 SAE Skill，建立连续 F 编号事实登记，区分文章陈述、官方操作规则、作者观点和分析推论。
  - 对题目数量、评测维度、流程、计时/提交限制、API key 安全和用户授权等关键声明核验官方来源；无独立佐证时标注证据状态。
  - 记录 SAE 页面验证码导致的当前可用性核验限制；不调用注册、考试或提交端点。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-6
- **Test Requirements**:
  - `rule` TR-1.1: 事实登记编号连续且每条关键声明均含来源与证据状态；证据为事实登记逐项检查。
  - `rule` TR-1.2: 所有数字、日期、操作限制与安全约束均可在引用的官方来源中定位；证据为来源逐项回验。
  - `rule` TR-1.3: 当前可观察的 bundle 与 remediation/review 记录不包含真实凭据，也不把 SAE 注册、开始考试或提交答案描述为已实测操作；当前轮操作保持只读，并明确没有独立、持久的早期执行历史可供审计。通过仅表示上述当前证据与限制披露满足要求，不证明完整历史上绝无 API 请求；证据为 bundle 内容、当前轮操作记录和本任务的历史证据边界说明。

- **Completion Evidence**:
  - 2026-10-19：读取 Kaggle 博文 S1 与官方静态 Skill S2，建立 F-001–F-022 登记；另记录公开 SAE 落地页 reCAPTCHA 阻止只读核验的限制，当前服务状态标为 `UNVERIFIED`。
  - F 编号连续，条目区分文章时点、Skill 文档规则、来源差异、作者定位与未核实主张；关键数字、日期、安全规则均登记来源位置。未调用注册、考试或提交 API，未处理凭据。

## Task 2: 生成最小充分的 SAE OKF bundle

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 在 `projects/awesome-okf-xs/doc/bundles/jishu/ai/practice/standardized-agent-exams/` 创建独立 bundle；评测分组通过交叉链接保持可发现性。
  - 先完成 `references/article-source.md` 与 `references/verification.md`，再撰写 `concepts/`；最后生成各级 `index.md` 和 `log.md`。
  - 解释 SAE 定位与评测问题、官方考试/结果流程、操作安全和评测边界；所有具体声明绑定 F 编号。
  - 不创建 `examples/`，除非来源证据同时满足可复现操作与经验证流程两项判据；本 Spec 当前不预期满足该例外。
  - 标注文章时点、Skill 核验时点和当前可用性未知边界，并与通用 Agent 评测、评测方法论专题互链。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-6
- **Test Requirements**:
  - `rule` TR-2.1: Bundle 路径与 Spec 一致，所有概念页有可解析且符合子项目约定的 OKF frontmatter；证据为文件清单及 frontmatter 检查。
  - `rubric` TR-2.2: 解释完整度；scale 1-5；anchors 1 = 以无来源转述为主，3 = 覆盖主体但关键边界不清，5 = 产品定位、流程、结果信号、安全与局限完整且有来源支撑；threshold >= 4；证据为逐页内容审阅。
  - `rule` TR-2.3: 任一具体数字、日期、产品规则或安全声明均可映射至 F 编号；证据为概念正文与事实登记的双向核对。
  - `rule` TR-2.4: 根索引与各子目录索引的 toctree 覆盖所有实际内容文件；无未满足判据的 `examples/`；证据为 toctree 检查。
- **Completion Evidence**:
  - 2026-10-19：九个 Markdown 文件组成 bundle，含 3 篇 concepts、references 与各级索引/toctree；无 `examples/`，未提供未实测操作教程。
  - TR-2.1/2.3/2.4：OKF frontmatter、概念页事实引用及 22 条事实编号已核对；Task 3 已完成导航、链接和全库 toctree 验证。
  - TR-2.2：解释完整度自评 4/5；已覆盖产品定位、考试/结果文档描述、用户授权、API key 安全及评分/效度限制，且保留来源时点与未核实边界。

## Task 3: 接入导航、执行 V 审查并完成门禁验证

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 在 practice 人类可读导航和 toctree 中增量接入独立 bundle；evaluation 索引保留交叉链接。更新受影响的 bundle/分组/领域计数，并保留与两个相邻专题的分工说明。
  - 编辑共享索引前重新核对 `awesome-okf-xs` 工作树；将现有 WorkBuddy 变更视为基线，只追加本任务必要内容，不覆盖、回滚或清理。
  - 从事实溯源、OKF/toctree 结构、导航可达、时间/当前可用性、操作安全与计数一致性进行 V 审查；修复发现后在 `references/verification.md` 与 `log.md` 留痕。
  - 运行可用的 `invoke gates.toctrees`、`invoke gates.utf8`、`invoke gates.bundles` 及文档构建；缺依赖时执行并记录手工等效检查。
  - 本任务不创建提交、不推送；最终报告实际变更和未能执行的门禁。
- **Acceptance Criteria Addressed**: AC-3, AC-5, AC-6, AC-7, AC-8
- **Test Requirements**:
  - `rule` TR-3.1: 新 bundle 可沿评测分组 toctree 到达，所有 Markdown 相对链接目标存在；证据为 toctree 与链接门禁或等效逐项结果。
  - `rule` TR-3.2: 修改后的 bundle 总索引、组索引和父级导航计数与实际目录树一致；证据为 `invoke gates.bundles` 或手工对账记录。
  - `rule` TR-3.3: 当前复核时 WorkBuddy 相关修改索引和未跟踪 bundle 仍存在，且本轮 remediation/review 未修改子模块文件；证据为本轮前后 fresh status 与 WorkBuddy 路径级 diff。因缺少实施前持久化快照，本项不要求也不声称已独立证明最初实施前后的精确保留。
  - `rule` TR-3.4: V 审查发现均有处理结论，事实/结构/链接/安全及时效检查有可复核记录；证据为 `references/verification.md` 与 `log.md`。
  - `rule` TR-3.5: 仅报告实际运行并通过的门禁；未运行项目明确列出原因和替代核验；证据为命令输出及验证摘要。

- **Completion Evidence**:
  - 2026-10-19：九文件 bundle 移至 `doc/bundles/jishu/ai/practice/standardized-agent-exams/`；practice 导航接入独立束，evaluation 索引保留两个原有条目并交叉链接 SAE。旧嵌套提案因锚点束计数语义不能单独计数，故按已确认决策调整为独立 practice 束。
  - TR-3.1/3.2：`python scripts/check-toctrees.py` 通过；bundle 内 29 条本地 Markdown 链接无断链。`python scripts/check-bundles-index.py` 通过，结果为 9 域 / 62 组 / 650 束，practice 21 束 / 19 个目录、AI 252 束、jishu 481 束；WorkBuddy 的 ecosystems=99 保留。
  - TR-3.3：初次实施后复查到 WorkBuddy 的总索引/AI 索引/ecosystems 索引变更及 `workbuddy-library-practice/` 未跟踪目录仍存在；本次只对计数相关行和 SAE 导航作增量修改，未清理无关文件。此记录不能替代未保存的实施前快照，精确历史保留状态仍不可追溯。
  - TR-3.4：Spec 与 bundle 的 F-001–F-022 编号集合 22/22 同序连续；三篇 concept 的实质声明、时效、服务可用性和安全边界完成自审，结论记于 bundle `references/verification.md` 与 `log.md`。本结果是实施者自审，不是独立评审。
  - TR-3.5：`python scripts/check-utf8.py` 通过（11828 个文件）；四个指定 `invoke` 命令因缺少 `invocations` distribution metadata 无法加载，未安装依赖。`sphinx-build -b html doc _build/html` 成功，含 13 条其他页面警告，SAE 页面无警告。

## Dependencies

- Task 1 precedes Task 2 because all tutorial claims and sections depend on the fact register.
- Task 2 precedes Task 3 because navigation, cross-link, and integrity checks require the completed bundle.
- Task 3 precedes the independent Review remediation issues because the bundle and its validation evidence must exist before review.
- I-1 and I-2 must complete before a new independent Review round can close this Spec.

## Review Remediation Issues

### Issue I-1: Correct the stale Review status

- **Status**: `completed`
- **Priority**: medium
- **Depends On**: None
- **Discovered By**: Review R1, finding R1-F1
- **Description**:
  - Replace the obsolete statement that independent review was not performed with the actual Review R1 outcome and remediation state.
  - Keep the historical Review R1 result in `review.md` unchanged; the new status must not erase or rewrite review history.
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `rule` TR-I-1.1: `tasks.md` no longer says independent review was not performed, and its current status agrees with `review.md` Review R1 and the remediation queue; evidence is a text search and cross-file status comparison.
- **Completion Evidence**:
  - `rg` search found no current-state claim that independent review was not performed; the outdated trailing statement was replaced with the R1-aware Review/remediation sequence.
  - `review.md` retains the historical R1 `fail` result and required remediation references; no Review history was altered during I-1.

### Issue I-2: Strengthen evidence and state its limits

- **Status**: `completed`
- **Priority**: medium
- **Depends On**: I-1
- **Discovered By**: Review R1, recommended issue I-2
- **Description**:
  - Record the currently observable submodule status and path-scoped diff evidence for the retained WorkBuddy changes and SAE additions without editing, staging, or reverting WorkBuddy files.
  - Recheck material SAE claims against accessible public Kaggle sources, then have the next independent read-only Review spot-check the mapping; do not access authenticated or exam-action endpoints.
  - Explicitly preserve the evidence limits: no durable pre-edit status snapshot or independent execution history was captured, so current-state inspection cannot retroactively prove exact before/after preservation or past absence of API calls.
- **Acceptance Criteria Addressed**: AC-1, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-I-2.1: Current status and path-scoped diffs identify the observed WorkBuddy and SAE paths, and no WorkBuddy file is modified by remediation; evidence is fresh `git status` and `git diff` output.
  - `rule` TR-I-2.2: The implementer rechecks material claims against accessible public Kaggle sources or marks them unverifiable, recording source URLs and claim mapping here; the fresh independent Review R2 may spot-check the mapping and must retain the same uncertainty boundaries.
  - `rule` TR-I-2.3: No historical evidence is asserted beyond what the current worktree and retained task records establish; the missing pre-edit snapshot and independent execution history remain explicit limitations.
- **Completion Evidence**:
  - 2026-10-19 source recheck used read-only retrieval of Kaggle's public [SAE blog](https://www.kaggle.com/blog/standardized-agent-exams) and [official SAE Skill](https://www.kaggle.com/static/experimental/sae/SKILL.md). Defuddle could not extract these endpoints; the permitted read-only WebFetch fallback returned the published Markdown/text. Key material mappings were checked: blog publication date and experimental/MVP positioning, first 16-question scope, Reasoning/Adversarial Safety descriptions, registration/account and result/leaderboard claims (F-001–F-009); Skill metadata, registration consent, 30-minute limit, all-answer submission, result fields, three-submission limit, API-key host/path restrictions, HTTP error handling and explicit deletion authorization (F-010–F-019). The registration wording difference in F-011 remains explicit; the article and Skill are both Kaggle sources, not independent corroboration.
  - F-020 remains `UNVERIFIED`: this recheck did not access the SAE landing page or any API. F-021/F-022 remain bounded to what the two specified documents do not establish; no scoring/validity claims or long-term rule continuity are inferred.
  - Fresh submodule status showed seven modified shared index/navigation files, including WorkBuddy-related `ecosystems/index.md` and `tencent/index.md` and SAE-related practice/evaluation/index changes; both untracked directories remain present: `workbuddy-library-practice/` and `standardized-agent-exams/`. The scoped diff showed 26 insertions and 14 deletions across the seven tracked files. This I-2 remediation edited only this SpecWeave `tasks.md`, not any submodule file.
  - Evidence limitation retained: no durable pre-edit status snapshot or independent execution history is available. Current status/diff establishes what is present now, but cannot retroactively prove exact before/after preservation or independently prove the absence of every past SAE API request. Review R2 must not upgrade these claims beyond available evidence.
  - Post-remediation checks: `python scripts/check-toctrees.py`, `python scripts/check-utf8.py` (11,828 files), and `python scripts/check-bundles-index.py` (9 domains / 62 groups / 650 bundles) passed. `sphinx-build -b html doc _build/html` succeeded with 13 warnings in unrelated existing pages; no SAE page warning was reported. The Invoke commands remain unavailable because the `invocations` distribution metadata is missing.

## Approved Acceptance-Criteria Adjustment

- **Status**: `approved`
- **Date**: 2026-10-19
- **Approval**: 用户在 Review R2 的处理选项中明确选择“调整验收标准”。
- **Scope**: 按 Spec 中记录的修订收窄 AC-6 与 AC-7，并同步 TR-1.3 与 TR-3.3。验收转为核查当前可见安全/工作区证据及其边界披露；不把缺失的历史执行日志或实施前快照视为可重建，也不声称其已被证明。
- **Review result**: Review R3 `pass`; Review R1 `fail` 与 Review R2 `blocked` 均作为历史结果保留。

### Post-Adjustment Verification (2026-10-19)

- `python -B scripts/check-toctrees.py`: passed; all index references resolve and content pages are reachable.
- `python -B scripts/check-utf8.py`: passed; 11,828 files are valid UTF-8.
- `python -B scripts/check-bundles-index.py`: passed; 9 domains / 62 groups / 650 bundles, with all five index/count views consistent.
- `python .agents/scripts/check-spec-consistency.py --path D:\spaces\SpecWeave --spec-dir .trae/specs/okf-wiki-ecosystem/create-standardized-agent-exams-okf-wiki`: not compatible with the repository's current Spec Mode artifact contract; it fails because it requires `checklist.md`, while the authoritative Spec Mode rules and spec index require `spec.md`, `tasks.md`, and `review.md` and prohibit `checklist.md`. No obsolete checklist was created to satisfy the stale checker.
- AC-6/TR-1.3 current evidence: read-only search of the SAE bundle found no real credential, request code, or `examples/` directory. This remediation round made no SAE network/API request and handled no credentials. The retained task record now explicitly says that no independent durable history exists to certify the full earlier execution history; no such historical claim is upgraded by these checks.
- AC-7/TR-3.3 current evidence: the submodule status at the start and after this remediation lists the same seven modified bundle/navigation files and the same two untracked bundle directories, including `workbuddy-library-practice/` and `standardized-agent-exams/`. The WorkBuddy-related modified indexes and WorkBuddy bundle remain present. This remediation edited only the two Spec Mode files in the root repository and made no submodule writes; the current diff was inspected. This establishes the current-round write boundary, not exact preservation from the unavailable original implementation baseline.
- Independent Review R3 passed with no actionable findings and no blocked checks. The fresh-context reviewer independently reran the three direct bundle gates; the report is appended in `review.md`. The source recheck and historical-evidence limits remain as recorded above.
