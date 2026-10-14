# HWE Bench 源码精读 OKF 教程束 - Implementation Plan

> 方法论：seven-concepts 场景 4（R→I→E→V→C）；Spec Mode 五阶段。所有事实 pin `4a137bb1378834ca3664a1c971684777eb5f364a`。

## Task 1: R-0~R-3 事实采集（只读）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 固定信源 HEAD、clean 校验；4 路并行子代理分区精读（A 编排/agent/沙箱、B 验证门/契约/CoreMark、C bench 方法学/数据/V2、D RTL 核/研究叙事）；共回收 A-001~058、B-001~064、C-001~070、D-001~073 原始事实 265 条。
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-1.1: 四区事实均含相对路径#L起-L止 锚点；HEAD=4a137bb1 经 git rev-parse 核实。
  - `rule` TR-1.2: 计数类事实（文件数/行数/log 74 行/16 模型目录/41 rep 等）由子代理机械计数。
- **Completion Evidence**:
  - 四个子代理事实登记已回收入主会话（2026-10-14）；矛盾清单 6 类已移交 I 阶段。

## Task 2: I 阶段洞察冻结

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 写 references/insights.md：I-1 验证器即工件、I-2 接受规则塑造搜索、I-3 防作弊即基准工程、I-4 形式验证的分层与空过、I-5 测量口径即结论、I-6 自治 harness 可靠性。每条四元组（现象+根因+影响+建议）并标注消费事实号。
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `rule` TR-2.1: 6 条洞察四元组字段齐全（G2）；每条引用 ≥3 个 F 编号。
  - `rule` TR-2.2: 6 类口径矛盾在洞察或事实勘误中有裁决位。

## Task 3: E-0 references 四件套 + 两个 index

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - references/source-code-map.md（G0、模块地图、C01-Cxx 计数台账、阅读路径）；references/facts.md（F-001 起十组 A-J，含勘误段）；references/insights.md；references/verification.md（V 骨架占位）；references/index.md（无 frontmatter）。
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `rule` TR-3.1: 每条事实 pinned 链接 hash=40 字符；计数台账与 R 取证一致。
  - `rubric` TR-3.2: 可审计性；1-5；1=流水账，3=可查但分组混乱，5=十组清晰、编号连续、勘误独立成段；阈值 ≥4。

## Task 4: E-1~E-4 concepts 17 篇

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 00 定位与循环 / 01 假设 schema 与五类 / 02 一轮编排四角色 / 03 worktree 与沙箱 / 04 RVFI NRET 契约 / 05 formal 与 ALTOPS / 06 cosim 对拍 ISS / 07 FPGA 与 fitness / 08 CoreMark 评测口径 / 09 接受规则与三结果类 / 10 baseline CPU 走读 / 11 v1 进化史与十连胜 / 12 scribe 与经验积累 / 13 V1 bench 方法学 / 14 V1 排行榜与失败模式 / 15 V2 演进与 E3 holdout / 16 harness 可靠性工程；加 concepts/index.md。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-4.1: 每篇 frontmatter 完整、正文只 `##`、结尾「相关概念/示例」束内 `/`-根导航。
  - `rule` TR-4.2: 6 类口径矛盾在 14/15/11/05/13 中按 AC-2 覆盖。
  - `rubric` TR-4.3: 单篇教学质量（是什么/怎么实现/为什么/边界）；1-5；阈值 ≥4。

## Task 5: E-5 examples 3 篇 + index

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 00 一个假设的生命周期（r1s0 失败→r6s0 Cold DIV +15.7%）；01 Opus 5.5 983 rep 拆解；02 失败样本集（sandbox 越权×3、−73.25% 回归、random 135 formal_failed）；examples/index.md。
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-5.1: 每个数字可回链 facts/log.jsonl 行号；示例不引入新事实编号之外的主张。
  - `rubric` TR-5.2: 可独立走读；1-5；阈值 ≥4。

## Task 6: 根 index/log + 三级索引注册

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - hwe-bench/index.md（性质声明+分层导航+toctree）、log.md（G0→C 全程）；注册 iot/index.md（表格+toctree+描述）、jishu/index.md（束数列）、doc/bundles/index.md（frontmatter 计数+计数行+域节标题+组表行）。
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `rule` TR-6.1: check-bundles-index.py rc=0；束总数五面一致。
  - `rule` TR-6.2: iot/jishu 两级 toctree 含 hwe-bench/index。

## Task 7: V 门 fresh-context 独立验证

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 全新子代理只读执行 G1 结构（29 文件）、G2 符号抽核（≥10%，P0=0）、G3 计数复核、G4 链接枚举+两门 rc=0、G5 Sphinx dummy；回填 verification.md 与 24 个内容文件 verified.at。
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-5
- **Test Requirements**:
  - `rule` TR-7.1: P0=0 且抽核命中率 ≥98%；两门禁与 dummy 输出粘贴 verification.md。
  - `rule` TR-7.2: 发现的问题修复后复扫全绿。

## Task 8: C 门 fresh-context 独立评审与收口

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 另一全新子代理独立评审（自核 HEAD、自写枚举器、复跑门禁），写 review.md；fail 则建 issue→修复→复审至 pass；最终汇报，不 commit。
- **Acceptance Criteria Addressed**: AC-1~AC-6
- **Test Requirements**:
  - `rule` TR-8.1: review.md 每条 AC 有独立证据，终态 Result=pass。
  - `rubric` TR-8.2: AC-4 教学质量独立分 ≥4。
