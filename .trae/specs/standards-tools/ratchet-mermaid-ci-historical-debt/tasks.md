# Mermaid 历史债务基线与 CI 增量门禁 — 实施计划

## Task 0: Mermaid 门禁现状取证
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 核对 2026-07-20 规则 8 接入提交、规则文档、全仓扫描器及 CI 调用链。
  - 对全仓和当前待提交旅行文档分别只读扫描，区分历史存量与新增内容。
  - 识别换行检查仍建议使用 `<br/>` 的策略不一致。
- **Acceptance Criteria Addressed**: AC-1, AC-5
- **Test Requirements**:
  - `rule` TR-0.1：调查证据包含提交 `4e345b316`、检查器入口、规则条款和 CI 调用位置。
  - `rule` TR-0.2：旅行文档单目录严格扫描为 0 错误；全仓报告数量差异记录为待基线工具复现，不硬编码为事实。
- **Completion Evidence**:
  - `git show 4e345b316` 确认规则 8 与 VS Code 检查于 2026-07-20 接入，未包含历史文档批量迁移。
  - 2026-09-30 独立扫描涉及约 687 个问题文件；待提交旅行文档独立扫描为 0 错误。
  - `common.py` 与现有测试仍期待 `\n → <br/>`，而 VS Code 规则要求单行。

## Task 1: 建立稳定的 Mermaid 违规基线模型
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 0
- **Description**:
  - 为违规定义稳定规则标识与跨平台确定的指纹，至少包含仓库相对路径、规则标识、规范化源码指纹和重复次数。
  - 支持从指定 Git 提交的已跟踪 Markdown 内容生成初始基线，排除工作区修改和未跟踪文件。
  - 增加基线比较与显式缩减能力；默认操作不得自动新增历史豁免。
  - 检查共享脚本库及现有 JSON/CLI 模式，复用已有机制。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4
- **Test Requirements**:
  - `rule` TR-1.1：同一 Git 提交重复生成基线结果确定，且行号漂移不改变违规身份。
  - `rule` TR-1.2：未跟踪文件和工作区修改不会进入指定提交的初始基线。
  - `rule` TR-1.3：新指纹或相同指纹超出基线次数会被识别；减少或消除发现不会被误报为新增。
  - `rule` TR-1.4：普通检查不写基线；显式更新只可移除已消失发现，不能静默新增豁免。
- **Completion Evidence**:
  - `python -m pytest .agents/scripts/tests/test_mermaid_baseline.py .agents/scripts/tests/test_checks_mermaid.py -q` 覆盖稳定身份、行号漂移、指定提交隔离、重复次数超限、已解决发现和单调缩减；总测试结果见 Task 4。
  - 基线由 `git archive` 从提交 `0aff6f36790fe417f5145cd63595ee909019860d` 构建，结果为 5,019 条历史错误；测试确认工作区修改和未跟踪 Markdown 不进入结果。
  - 显式 prune 的测试确认只移除/降低已登记项，新增发现不会写入基线；局部目录 prune 返回错误且原文件字节不变。
  - 稳定 ID 迁移前，两次独立 CLI 生成结果均为 1,787,773 字节，SHA-256 均为 `DC1D3A273F6824C69718779C5CC9BDBDB46A1F36B3B87CB7B079A93C3AAF920A`，并与当时仓库初版基线逐字节一致；该 hash 已由 Issue I-2 的稳定 ID 迁移取代。

## Task 2: 统一 Mermaid 换行诊断、修复与测试
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 0
- **Description**:
  - 统一 `\n` 检查器、修复器和各图表类型实现，使诊断建议与 VS Code 单行策略一致。
  - 更新现有公共函数与 fixer 测试，覆盖不会重新生成 `<br/>` 的端到端修复。
  - 为 VS Code 兼容层补齐正向、负向和注释/子图边界测试。
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `rule` TR-2.1：含 `\n` 的违规诊断建议使用空格压平，且自动修复结果不含 `<br/>`。
  - `rule` TR-2.2：`<br/>`、圈号、中文方括号与嵌套 direction 的 VS Code 兼容检查均有针对性测试。
  - `rule` TR-2.3：原 Mermaid fixer/common 测试及新回归测试全部通过。
- **Completion Evidence**:
  - `python -m pytest .agents/scripts/tests/test_checks_mermaid.py .agents/scripts/tests/test_mermaid_common.py .agents/scripts/tests/test_mermaid_fixers.py .agents/scripts/tests/test_mermaid_baseline.py -q`：164 passed。
  - 测试覆盖 `\n` 诊断/修复压平为空格且不生成 `<br/>`，以及 VS Code 兼容检查边界；完整命令结果记录于 2026-10-01 本次验证。

## Task 3: 接入基线 CI 门禁并更新使用说明
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**:
  - 让 `repo-check.py` 与 CI Mermaid 步骤调用基线比较模式，同时保留默认严格全量扫描。
  - 添加机器可读、可审查的历史基线；仅由已跟踪历史文件生成，不吸收当前未跟踪旅行文档。
  - 更新 Mermaid 检查使用说明及规则文档，说明严格模式、CI 基线模式、基线缩减和历史债务报告语义。
  - 更新 standards-tools 主题看板登记。
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-4
- **Test Requirements**:
  - `rule` TR-3.1：基线未变化时 CI 模式对历史债务通过并报告数量；严格模式仍因这些错误返回非零。
  - `rule` TR-3.2：向新文件或既有文件新增违规会使 CI 检查返回非零；重复新增也不能被同一指纹掩盖。
  - `rule` TR-3.3：CI 检查运行前后基线文件及工作区均无自动写入。
  - `rule` TR-3.4：相关文档和主题看板描述与实际 CLI/CI 行为一致，链接检查通过。
- **Completion Evidence**:
  - `repo-check.py all` 默认将 `.agents/scripts/data/mermaid-baseline.json` 传给 Mermaid 检查；`ci-check.ps1` 与 `ci-check.sh` 均显式传递基线；直接调用 Mermaid 检查仍保留严格模式。
  - `python .agents/scripts/repo-check.py mermaid --baseline .agents/scripts/data/mermaid-baseline.json`：扫描 7,922 个 Markdown 文件，4,942 条已知历史债务、0 新增、77 已消除、364 条既有警告，门禁通过。
  - 稳定 ID 迁移前的门禁前后基线 SHA-256 均为 `DC1D3A273F6824C69718779C5CC9BDBDB46A1F36B3B87CB7B079A93C3AAF920A`，证明当时普通检查未改写初版基线；迁移后当前基线 hash 与门禁只读证据记录于 Issue I-2。
  - 使用说明、Mermaid 规范及本主题登记已更新。链接检查覆盖 666 篇 Markdown、2,376 个本地引用，发现 75 个历史断链和 5 个目录链接警告；本次新增 Spec 链接目标存在，报告的问题均为既有内容，未自动修复范围外文件。

## Task 4: 完成回归与全量 CI 验证
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 运行 Mermaid 专项测试、基线模式测试和严格模式测试。
  - 运行完整 CI，记录门禁结果；若首个 Mermaid 门禁通过后暴露其他独立失败，先按证据判断其是否属于本规格范围。
  - 队列清空后进入独立 Review 阶段；只修复本规格引入或暴露且属于批准范围的问题。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-4.1：全量 CI 的 Mermaid 步骤不再因基线内历史项阻断。
  - `rule` TR-4.2：严格模式仍报告全部存量违规；基线模式对新增违规仍非零退出。
  - `rule` TR-4.3：完整 CI 通过，或所有后续阻塞项均被准确记录为规格外的独立问题，不以跳过步骤宣称通过。
- **Completion Evidence**:
  - Mermaid 四组专项测试共 164 项通过；其中严格模式错误返回非零、基线内债务通过、新文件违规与重复次数增加阻断、CI 基线只读及全仓 prune 防护均有回归断言。
  - 稳定 ID 迁移前的 Mermaid 基线 CI 命令通过：7,922 个 Markdown 文件、4,942 条已知历史债务、0 新增、77 已消除；当时生成基线的两次字节级复现一致。迁移后的最终基线与门禁证据记录于 Issue I-2。
  - 全量 CI 已执行，但未通过：在第 1/22 阶段的仓库合规检查中，范围外文件名门禁报告 10,831 项并终止；同阶段 Mermaid 基线门禁先行通过，后续 21 个阶段未执行。文件名债务不属于本 Spec 授权范围，未批量改名或改门禁；因此不宣称全量 CI 通过。
  - 独立 Review 属于 Spec Mode 的 Review 阶段，在本任务队列清空后执行；此处不以实施者自验替代独立审查。

## Issue I-1: 保持子目录基线比较使用仓库相对路径
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: None
- **Discovered By**: Review R1, finding R1-01
- **Description**:
  - 基线发现的 path 以仓库根为基准；真实 `repo-check.py --path <subdir>` 入口会把扫描目录设为 `project_root`，导致诊断身份相对扫描目录生成，既有发现被误报为新增并同时计为已解决。R1 的测试未覆盖该 CLI 参数解析边界。
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-I-1.1：通过真实 `repo-check.py mermaid --path docs --baseline <baseline>` 入口比较仍存在的 `docs/guide.md` 发现，报告 `known=1, new=0, resolved=0`，身份路径为 `docs/guide.md`。
  - `rule` TR-I-1.2：子目录内同指纹新增次数只报告超过基线的部分；仓库根扫描行为不变。
- **Prior Completion Evidence (R1; insufficient for the real CLI entry point)**:
  - 两条新增 CLI 回归测试先失败，复现 `known=0, new=1, resolved=1`；增加仓库根身份路径后两条均通过。
  - `python -m pytest .agents/scripts/tests/test_checks_mermaid.py -q`：59 passed。
- **Completion Evidence**:
  - 新增回归测试通过真实 `repo-check.main()` 参数解析与命令分派复现 `--path docs` 边界；修复前摘要为 `known=0, new=1, resolved=1`，修复后以 `docs/guide.md` 为身份并得到 `known=1, new=0, resolved=0`。
  - `python -m pytest .agents/scripts/tests/test_checks_mermaid.py -q`：60 passed；同指纹超额次数测试与仓库根扫描行为保持通过。

## Issue I-2: 将稳定规则 ID 与诊断文案解耦
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: None
- **Discovered By**: Review R1, finding R1-02
- **Description**:
  - 稳定 `rule_id` 已与诊断文案解耦，但基线身份仍包含原始源码；同一规则的动态匹配值从 `①` 变为 `②` 时，指纹改变并将已有债务误报为新增。需在保留足够源码区分度的前提下，为同规则动态值提供稳定的源码身份。
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-I-2.1：同一规则匹配不同动态值（如 `①` 与 `②`）时使用相同稳定 rule_id。
  - `rule` TR-I-2.2：诊断展示文案措辞变化不改变规则 ID，已有基线发现继续计为 known。
  - `rule` TR-I-2.3：同一路径、同一规则的违规仅动态匹配值变化时，基线比较仍将其识别为已知项，不新增也不同时计为已解决。
- **Prior Completion Evidence (R1; rule ID stable but source identity gap remains)**:
  - `MermaidIssue` 保持既有 `(line, level, message)` 三元组消费接口，同时显式携带稳定 `rule_id`；阻断错误缺少 ID 时基线采集立即报错，warning 不进入阻断基线。全仓门禁成功采集且未触发缺 ID 守卫。
  - 回归覆盖动态圈号 `①`/`②` 共用 `mermaid.vscode.circled_digit`，诊断文案改变后原发现仍为 `known=1, new=0`，以及无显式 ID 的错误被拒绝。
  - `python -m pytest .agents/scripts/tests/test_checks_mermaid.py .agents/scripts/tests/test_mermaid_common.py .agents/scripts/tests/test_mermaid_fixers.py .agents/scripts/tests/test_mermaid_baseline.py -q`：169 passed。
  - 从固定 revision `0aff6f36790fe417f5145cd63595ee909019860d` 重新生成稳定 ID 基线，共 5,019 条历史错误；当前基线 SHA-256 为 `19FFF0F58EDCF824FA99A80A896626A469A281C958A05305EC1591DB701AA12C`。此前的 `DC1D3A273F6824C69718779C5CC9BDBDB46A1F36B3B87CB7B079A93C3AAF920A` 是迁移前 hash，不代表当前文件。
  - 迁移后执行 `python .agents/scripts/repo-check.py mermaid --baseline .agents/scripts/data/mermaid-baseline.json --exclude docs/topics/travel`：扫描 7,922 个 Markdown 文件，4,942 条已知历史债务、0 新增、77 已消除、364 警告，门禁通过；门禁后 hash 仍为 `19FFF0F58EDCF824FA99A80A896626A469A281C958A05305EC1591DB701AA12C`，确认只读。
  - 注：以上 `19FFF0...` 与 7,922 文件数均为源码身份规范化前的历史证据，不代表当前基线或最新扫描结果。
- **Completion Evidence**:
  - 新增基线比较回归：基线源码中的 `①` 与当前源码中的 `②` 仍匹配为同一路径、同一 `mermaid.vscode.circled_digit` 发现，结果为 `known=1, new=0, resolved=0`；原始 `source` 仍保留用于审阅，规范化后的 `identity_source` 用于身份比较。
  - `python -m pytest .agents/scripts/tests/test_mermaid_baseline.py .agents/scripts/tests/test_checks_mermaid.py -q`：70 passed；本轮四组 Mermaid 专项回归总计 173 passed。
  - 基线从固定 revision `0aff6f36790fe417f5145cd63595ee909019860d` 重新生成，记录 5,019 条历史错误；当前 SHA-256 为 `EC470ACA3A01A515CBB6E2D71CB0348B221B00ED6AFCEDFCAD1ABEA97EC86B6D`，替代修复前的 `19FFF0...`。
  - 源码身份修复后执行增量门禁并显式排除 `docs/topics/travel/`：扫描 7,923 个 Markdown 文件，4,942 条已知历史债务、0 新增、77 已消除、364 警告，门禁通过；门禁前后基线 hash 均为 `EC470ACA3A01A515CBB6E2D71CB0348B221B00ED6AFCEDFCAD1ABEA97EC86B6D`。此前记录的 7,922 是较早扫描结果；两次计数差异未能归因，故不推断具体文件来源。

## Issue I-3: 修正 fixer 换行摘要中的过时策略
- **Status**: `completed`
- **Priority**: low
- **Depends On**: None
- **Discovered By**: Review R2, finding R2-03
- **Description**:
  - flowchart、state diagram、class diagram、ER diagram 的 fixer 摘要仍显示 `\\n→<br/>`，与实际空格压平行为及 VS Code 单行策略冲突。
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `rule` TR-I-3.1：四个 fixer 的摘要明确描述以空格压平换行，不再建议或声称生成 `<br/>`；测试覆盖摘要与修复输出语义一致。
- **Completion Evidence**:
  - 四个 fixer 的换行摘要统一改为 `\n→空格`，实际修复行为保持不变。
  - 新增四类 fixer 回归测试；首次运行因实际摘要仍为 `\n→<br/>` 按预期失败，修改摘要后通过。
  - `python -m pytest .agents/scripts/tests/test_mermaid_fixers.py::test_newline_fixer_summaries_match_space_flattening -q`：1 passed；四组 Mermaid 专项测试总计 173 passed。

## Issue I-4: 补齐 Mermaid 换行修复的真实 CLI 端到端测试
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: None
- **Discovered By**: Review R2, finding R2-04
- **Description**:
  - AC-5 要求端到端 CLI 验证，但现有测试只覆盖函数、fixer 或 `_process_file`，未验证实际命令行入口与最终文件。
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `rule` TR-I-4.1：针对含 `\\n` 的 Mermaid Markdown 执行真实 CLI 检查/修复入口，断言命令结果正确、最终内容将换行压平为空格且不含新增 `<br/>`。
- **Completion Evidence**:
  - 新增 subprocess 端到端测试，真实执行 `check-mermaid.py --path <临时目录> --fix`，断言退出码为 0、CLI 输出检查通过，且最终 Markdown 中为 `one two`、不含 `<br/>`。
  - `python -m pytest .agents/scripts/tests/test_checks_mermaid.py::TestRun::test_check_mermaid_cli_fixes_backslash_newline_end_to_end -q`：1 passed；四组 Mermaid 专项测试总计 173 passed。

## Issue I-5: 补齐最新基线的字节级确定性证据
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: None
- **Discovered By**: Review R3, finding R3-01
- **Description**:
  - R3 指出最新 identity-source 基线迁移后只有单次序列化 hash；既有隔离测试比较两次构建的 Python 对象，未直接验证正式序列化输出字节相等。
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-I-5.1：在隔离临时 Git 仓库中对同一固定 revision 构建两次基线，经正式序列化器写出后，两个输出文件字节完全一致。
- **Completion Evidence**:
  - 扩展 `test_build_baseline_reads_only_the_requested_commit`：在临时 Git 仓库中对同一 revision 两次调用 `build_baseline_from_revision`，分别经 `write_baseline` 序列化，并断言两个 JSON 文件字节完全相等；原有对象相等、工作区改动和未跟踪文件隔离断言保留。
  - 定向测试 1 passed；四组 Mermaid 专项回归 `python -m pytest .agents/scripts/tests/test_checks_mermaid.py .agents/scripts/tests/test_mermaid_common.py .agents/scripts/tests/test_mermaid_fixers.py .agents/scripts/tests/test_mermaid_baseline.py -q`：173 passed。
