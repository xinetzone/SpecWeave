# Mermaid 历史债务基线与 CI 增量门禁 — Independent Review

## Review Checkpoints

- [x] CP-R1: 初始基线仅反映指定 Git revision 的已跟踪 Markdown，且重复生成确定
  - **Type**: `rule`
  - **Covers**: AC-1, TR-1.1, TR-1.2
  - **Evidence**: R4 确认基线由 `git archive` 提取指定 revision；隔离测试覆盖工作区修改、未跟踪文件，并对同一 revision 两次构建经 `write_baseline` 序列化后的文件字节逐一比较，相等。

- [x] CP-R2: 新增指纹或既有指纹次数增加会阻断，行号漂移不会产生新增发现
  - **Type**: `rule`
  - **Covers**: AC-2, TR-1.3, TR-3.2
  - **Evidence**: R4 重验真实 `repo_check.main()` 子目录入口、动态圈号身份、行号漂移和新增/超额发现测试；同一违规继续识别为 known，新增及超额发现仍阻断。

- [x] CP-R3: CI 使用只读基线门禁，默认严格扫描仍对存量违规失败
  - **Type**: `rule`
  - **Covers**: AC-3, NFR-3, TR-3.1, TR-3.3, TR-4.1, TR-4.2
  - **Evidence**: R4 重验 PowerShell/Shell CI 基线接线、基线只读比较与默认严格模式测试。全量 CI 未在本轮执行；既有记录如实说明其在范围外 filename 门禁处停止。

- [x] CP-R4: 显式 prune 单调缩减基线，局部扫描不得缩减全仓基线
  - **Type**: `rule`
  - **Covers**: AC-4, TR-1.4
  - **Evidence**: R4 重验 `prune_baseline` 只保留或减少已有身份/次数，CLI 拒绝局部 prune，测试确认拒绝时基线字节不变。

- [x] CP-R5: Mermaid 换行诊断和修复压平为空格，不生成 `<br/>`
  - **Type**: `rule`
  - **Covers**: AC-5, TR-2.1, TR-2.2, TR-2.3
  - **Evidence**: R4 重验四个 fixer 摘要、换行诊断和真实 CLI subprocess 测试；退出码、检查输出及最终文件均符合空格压平策略且不含 `<br/>`。

- [x] CP-R6: 用户文档、Spec 证据与看板登记没有误述验证结果或纳入范围外内容
  - **Type**: `rule`
  - **Covers**: TR-3.4, TR-4.3
  - **Evidence**: R4 确认全量 CI 在第 1/22 阶段被范围外 filename 门禁阻断、后续阶段未运行，文档没有声称全量通过；旅行目录保持排除，未扩大修复范围。

- [x] CP-U1: 实现与验证证据对批准范围的覆盖完整、可追溯
  - **Type**: `rubric`
  - **Covers**: AC-1–AC-5, TR-1.1–TR-4.3
  - **Scale**: 1-5
  - **Anchors**: 1 = 关键验收缺少实现或证据；3 = 主路径可验证但有明显证据/边界缺口；5 = 每条验收均有独立、可复现证据且边界清楚
  - **Pass Threshold**: >= 4
  - **Evidence**: R4 score 4/5，达到阈值；AC-1 至 AC-5 均有独立证据。扣除的一分对应本轮未重跑全量 CI，且其既有范围外阻塞仍准确记录。

## Review History

### Review R1
- **Result**: `fail`
- **Evidence**:
  - 独立审查者对照 spec.md、tasks.md、实现 diff、基线数据、CI 调用点与相关测试进行只读检查。
  - Mermaid 四组专项测试的既有证据为 164 passed；本轮未重跑全量 CI。
  - 全量 CI 的 filename 门禁阻塞与链接检查历史问题均准确记录，未把范围外内容混入修复。
- **Checkpoint Results**:
  - CP-R1 (`rule`): `pass`
  - CP-R2 (`rule`): `fail`
  - CP-R3 (`rule`): `pass`
  - CP-R4 (`rule`): `pass`
  - CP-R5 (`rule`): `pass`
  - CP-R6 (`rule`): `pass`
  - CP-U1 (`rubric`): `fail`; score 3/5; 两个可复现身份问题使证据覆盖未达到阈值
- **Findings**:
  - R1-01: `actionable`; P2; 子目录基线比较使用扫描目录相对路径，导致仓库基线中的既有发现被误报为新增并同时显示已解决。以 `--path docs` 对仍存在的 `docs/guide.md` 违规执行比较，可复现 `known=0, new=1, resolved=1`；预期为 `known=1, new=0, resolved=0`。
  - R1-02: `actionable`; P2; `_rule_id` 由诊断文案归一化产生，同一规则匹配 `①` 和 `②` 会得到不同 rule_id，文案改写也会改变历史身份。预期是规则身份与展示文案及动态匹配值解耦。
  - R1-03: `advisory`; P3; DocGen 主题自动看板只统计 checkbox，不识别 Spec Mode `Status` 字段，故本 Spec 的自动行显示“待启动”；这是既有生成器状态模型限制，不属于 Mermaid 门禁阻断缺陷。
- **Recommended Issues**:
  - Issue I-1：保持子目录基线比较使用仓库相对路径；priority `medium`；覆盖 AC-2、TR-1.3。
  - Issue I-2：将稳定规则 ID 与诊断文案解耦；priority `medium`；覆盖 AC-2、TR-1.3。

### Review R2
- **Result**: `fail`
- **Evidence**:
  - 全新上下文审查者只读检查 spec、tasks、R1 记录、实现、基线、CI 调用点、相关文档与测试；未写入审查文件、未触碰 `docs/topics/travel/`，也未重跑全量 CI。
  - Mermaid 专项测试为 169 passed；审查者进一步使用真实入口复现子目录身份问题，并比较同一显式规则下动态源码值变化前后的基线身份。
  - 范围外 filename 门禁如实保留为独立问题，不作为 R2 失败原因。
- **Checkpoint Results**:
  - CP-R1 (`rule`): `pass`
  - CP-R2 (`rule`): `fail`
  - CP-R3 (`rule`): `pass`
  - CP-R4 (`rule`): `pass`
  - CP-R5 (`rule`): `fail`
  - CP-R6 (`rule`): `pass`
  - CP-U1 (`rubric`): `fail`; score 3/5; AC-2 有两项身份缺陷，AC-5 另有摘要不一致及端到端测试缺口
- **Findings**:
  - R2-01: `actionable`; P2; `repo-check.py --path docs` 将扫描目录作为 `project_root`，同一仓库发现路径变成 `guide.md`，可复现 `known=0, new=1, resolved=1`；预期保留 `docs/guide.md` 并得到 `known=1, new=0, resolved=0`。R1 的 I-1 单元/CLI 层证据不足以覆盖该真实入口边界。
  - R2-02: `actionable`; P2; 同一 `mermaid.vscode.circled_digit` 规则从 `①` 改为 `②` 时，显式 `rule_id` 虽相同，原始 `source` 仍参与身份，可复现 `known=0, new=1, resolved=1`；预期动态值变化不把同一规则历史发现判为新增，同时保留区分不同违规的源码身份。
  - R2-03: `actionable`; P3; flowchart、state diagram、class diagram、ER diagram 四个 fixer 的摘要仍声称 `\\n→<br/>`，与实际空格压平行为相反；预期摘要与输出一致。
  - R2-04: `actionable`; P2; AC-5 要求端到端 CLI 验证，但现有测试只覆盖函数、修复器或 `_process_file`，没有实际 CLI 执行断言；预期检查输出、退出结果及最终文件共同证明换行压平为空格且不生成 `<br/>`。
- **Recommended Issues**:
  - 重开 Issue I-1：修复真实 `repo-check.py --path` 子目录比较身份，并增加覆盖该入口的回归测试。
  - 扩展 Issue I-2：稳定基线身份不仅要解耦诊断文案，也要处理同规则动态源码值变化；增加比较结果回归。
  - Issue I-3：修正四个 fixer 的过时换行摘要并测试摘要语义。
  - Issue I-4：新增真实 CLI 端到端换行修复测试，覆盖 AC-5。

### Review R3
- **Result**: `blocked`
- **Evidence**:
  - 全新只读上下文复核 R1/R2 修复、当前 Spec、基线、CI 接线、相关文档和四组 Mermaid 测试；未修改仓库文件、未读取或扫描 `docs/topics/travel/`，未重跑全量 CI。
  - 四组 Mermaid 专项测试为 173 passed；当前基线 SHA-256 为 `EC470ACA3A01A515CBB6E2D71CB0348B221B00ED6AFCEDFCAD1ABEA97EC86B6D`，revision 为 `0aff6f36790fe417f5145cd63595ee909019860d`，包含 4,861 个聚合 finding、5,019 次出现、17 个 rule ID 和 206 个规范化身份项。
  - 未发现新增实现缺陷。阻塞仅为 AC-1 证据：既有隔离测试对两次构建结果做 Python 对象相等比较；当前源码身份迁移后的基线只有单次序列化 hash 记录，尚无两次序列化字节相等的现行证据。
- **Checkpoint Results**:
  - CP-R1 (`rule`): `blocked`; 缺当前版本双次序列化字节比较证据。
  - CP-R2 (`rule`): `pass`; 子目录 CLI 仓库身份和圈号动态源码身份均有回归证据。
  - CP-R3 (`rule`): `pass`; CI 基线接线、只读比较和严格模式通过静态检查及测试。
  - CP-R4 (`rule`): `pass`; prune 单调缩减和局部 prune 拒绝通过测试。
  - CP-R5 (`rule`): `pass`; 四个摘要和真实 CLI 修复测试均符合空格压平策略。
  - CP-R6 (`rule`): `pass`; 全量 CI 的范围外 filename 阻塞及 travel 隔离记录准确。
  - CP-U1 (`rubric`): `pass`; score 4/5，达到阈值 4；AC-1 的证据缺口阻止评分为 5。
- **Findings**:
  - R3-01: `blocked`; P2; AC-1 的字节级确定性证据在最新 identity-source 基线迁移后过期。现有隔离测试仅比较两次构建的 Python 对象，当前 hash 只记录单次输出。建议在临时 Git 仓库中对同一 revision 构建两次并通过正式序列化器写出，再断言两个文件字节完全相同；审查未发现确定性实现缺陷。
- **Recommended Issues**:
  - Issue I-5：为同一 revision 的两次隔离基线构建增加序列化字节级相等断言，并记录当前迁移版本的验证证据；覆盖 AC-1、TR-1.1。

### Review R4
- **Result**: `pass`
- **Evidence**:
  - 全新只读上下文独立复核全部 AC、CP-R1–CP-R6、CP-U1 及 R3-01 修复；审查者未修改仓库文件，未读取或扫描 `docs/topics/travel/`，未运行全量 CI。
  - R3-01 已解决：临时 Git fixture 对同一 revision 调用两次基线构建，分别通过 `write_baseline` 序列化，并断言两个 JSON 文件的原始字节完全相同；同一 fixture 也验证工作区修改及未跟踪 Markdown 不进入提交基线。
  - Mermaid 四组专项测试独立复跑为 173 passed；独立序列化字节确定性测试为 1 passed。
  - 范围外 filename 门禁仍只按既有证据记录为全量 CI 阻塞，不归入本 Spec 修复范围；`docs/topics/travel/` 未纳入扫描或修改。
- **Checkpoint Results**:
  - CP-R1 (`rule`): `pass`; 基线提交隔离与当前版本字节级确定性均有独立证据。
  - CP-R2 (`rule`): `pass`; 仓库相对身份、行号漂移、动态圈号和新增/超额发现行为通过。
  - CP-R3 (`rule`): `pass`; CI 基线模式、只读行为和严格模式通过；完整 CI 不在本轮重跑范围。
  - CP-R4 (`rule`): `pass`; 显式单调 prune 与局部 prune 防护通过。
  - CP-R5 (`rule`): `pass`; 换行摘要、修复结果和真实 CLI 端到端测试通过。
  - CP-R6 (`rule`): `pass`; 验证结果及范围边界记录准确。
  - CP-U1 (`rubric`): `pass`; score 4/5，达到阈值 4；未重跑全量 CI 是唯一残余验证缺口。
- **Findings**: 无可行动或 advisory 发现。
- **Recommended Issues**: 无。
- **Residual Testing Gaps**:
  - 全量 CI 未重跑；此前运行在第 1/22 阶段被范围外 filename 门禁阻断，后续阶段未执行。此结果不影响 Mermaid 专项验收，也不代表全量 CI 通过。
