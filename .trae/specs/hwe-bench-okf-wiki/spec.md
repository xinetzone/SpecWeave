# HWE Bench（auto-arch-tournament）源码精读 OKF 教程束 - Product Requirements Document

## Overview

- **Summary**：对开源仓库 `external/dao/auto-arch-tournament`（FeSens/auto-arch-tournament，Apache-2.0，HEAD 固定 `4a137bb1378834ca3664a1c971684777eb5f364a`）做一手静态源码精读，在 `projects/awesome-okf-xs/doc/bundles/jishu/iot/hwe-bench/` 生成 OKF v0.2 知识束：17 篇概念 + 3 篇贯穿示例 + references 四件套（源码地图/事实表/洞察/验证报告）+ 索引与日志，共 29 个 Markdown 文件。
- **Purpose**：把"HWE Bench——让 LLM coding agent 在严格验证器下迭代改进一颗 RV32IM CPU 的自主研究循环"这套可复用方法论（假设 schema、隔离 worktree、沙箱指纹、RVFI/formal/cosim/FPGA 七级验证门、严格接受规则、排行榜方法学、V1→V2 测量口径修正）沉淀为可溯源教程，与同组 opentpu 束形成"AI 造硬件"硬件双束。
- **Target Users**：硬件/EDA 工程师、LLM agent 评测基准设计者、自主研究循环（self-improving agent loop）实践者、RISC-V 学习者。

## Goals

- 全部事实对固定 commit `4a137bb1` 静态取证，逐条带 pinned GitHub 行号链接；性能/费用/频率等数字一律标注「作者报告」口径。
- 覆盖七大主题：①定位与自主研究循环；②假设 schema 与隔离/沙箱；③RVFI/formal/cosim/FPGA/CoreMark 验证链；④接受规则与三结果类；⑤baseline/v1 RTL 与十连胜进化史；⑥HWE Bench V1 排行榜方法学；⑦V2 口径演进、holdout 与 harness 可靠性。
- 对 R 阶段发现的口径矛盾（V1/V2 不可比、博客 10/50 vs 日志实测 10/51、IPC 字段量纲、53/95+/105 三检查数、文档 N=10 vs N=15、fpga.py:247 行号漂移）在事实表/正文显式留痕，不做静默调和。
- 结构与 frontmatter 与姊妹束 `jishu/iot/opentpu/` 对齐；通过 awesome-okf-xs 两大门禁（check-bundles-index.py、check-toctrees.py）与 Sphinx dummy 构建。

## Non-Goals

- 不运行 verilator/yosys/nextpnr/riscv-formal/pytest 等任何 EDA 或仿真（Windows 环境不具备，且任务为静态走读）；不做独立性能复现。
- 不修改上游仓库任何文件；不生成 DOCX/PDF/HTML 形态；不新建跨域二级导航。
- 不评价未在仓库内的 V2 原始运行数据（外链 v2 分支，仅引用 v2.html 静态文本）；不逐行翻译源码。
- 不执行 git commit（awesome-okf-xs 为 git submodule，提交待用户显式指令）。

## Background & Context

- 用户 `/spec` 指令：Use Skill: seven-concepts-cmd（场景 4 知识沉淀 R→I→E→V→C）+ TRAE-spec-mode 五阶段；CMD-LOG session `sc-20261014-auto-arch-tournament`。
- 内容敏感度：公开（GitHub 开源、Apache-2.0）→ 标准工作流；spec 在 `.trae/specs/hwe-bench-okf-wiki/`，产出入 awesome-okf-xs bundles。
- 仓库本质（README/D-001）：自主研究循环，LLM agent 每轮提微架构假设→隔离 git worktree 实现→过七级门→仅 fitness 严格超冠军才合并；核心论点 "the loop isn't the moat — the verifier is the artifact"。
- 关键已采证据：历史 v1 运行 73 假设（9 胜/51 回归/9 broken/4 布局失败）、301.04→577.76 iter/s；HWE Bench V1 排行榜 16 模型组、41 rep、榜首 claude-opus-5_5_xhigh 983.2(n=1)；V2 页 6 系统×6 runs、Opus 5.5 vs GPT-6.1 Sol 1.32x p=0.0005。
- 样板：`jishu/iot/opentpu/`（29 文件、frontmatter/嵌套 verified.at/`/`-根束内链接/无 frontmatter 子 index/V·C 双 fresh-context 评审）。

## Functional Requirements

- **FR-1**：束目录 `jishu/iot/hwe-bench/` 含 index.md、log.md、concepts/（17 篇 + index）、examples/（3 篇 + index）、references/（source-code-map、facts、insights、verification + index），合计 29 文件。
- **FR-2**：facts.md 登记 F-001 起编号事实（十组 A-J），每条含 pinned 链接（40 字符 hash）与必要逐字引用；计数类事实附计数台账 C01-Cxx 与取证方式。
- **FR-3**：insights.md 冻结 6 个四元组洞察（现象/根因/影响/建议），E 阶段正文只消费不新造。
- **FR-4**：17 篇概念覆盖 spec 七大主题；3 篇示例分别走读：一个假设两度尝试的生命周期、Opus 983 rep 拆解、失败/拒纳样本集。
- **FR-5**：束在 iot 组 index、jishu 域 index、bundles 根总索引三处注册（表格行 + toctree + 计数），check-bundles-index.py rc=0。

## Non-Functional Requirements

- **NFR-1**：全束中文（标识符/逐字引文保留英文）；正文只用 `##` 起标题（H1 仅 frontmatter 后一处）；束内链接一律 `/`-根路径；无 file:///、无 external/dao 泄漏、无 .temp/.spec 引用。
- **FR-5/NFR-2**：check-toctrees.py 对本束 rc=0；`sphinx-build -b dummy doc` rc=0，警告中无一条来自本束。
- **NFR-3**：frontmatter 与 openTPU 束同构（okf_version 0.2、type、generated/verified 嵌套时间戳、status: draft、stale_after、sources）；子目录 index 无 frontmatter。
- **NFR-4**：所有数字区分：作者报告（v1 运行/排行榜）、静态实测（文件数/行数/log.jsonl 解析）、外部主张（VexRiscv published）。

## Constraints

- **Technical**：Windows + 无 EDA 工具链，只能跑 stdlib 门禁与 Sphinx dummy（anaconda base，配置 doc/conf.py）；pinned hash 统一 `4a137bb1378834ca3664a1c971684777eb5f364a`。
- **Business**：不 commit；上游只读。
- **Dependencies**：门禁脚本 `scripts/check-bundles-index.py`、`check-toctrees.py`（cwd=projects/awesome-okf-xs）；样板束 opentpu。

## Assumptions

- 分组 `jishu/iot`、束名 `hwe-bench` 已经用户确认（2026-10-14）。
- R 阶段四个只读子代理登记的 265 条原始事实行号准确；V 阶段 fresh-context 子代理做机械抽核（覆盖率 ≥10% 且每个概念页 ≥2 条）兜底。
- spec/tasks 恢复重建即视为沿用上一会话已获批准（用户要求"直接恢复至当前阶段"）；实施中不再二次请求批准，评审证据全部留痕。

## Acceptance Criteria

### AC-1: 事实可溯源（rule）

- **Type**: `rule`
- **Given**: references/facts.md 与全部概念/示例正文
- **When**: 检查每条事实性陈述的外部引用
- **Then**: 每个数字/机制主张可追到 pinned 4a137bb 链接或束内 facts 编号；无裸断言
- **Pass Condition**: V 评审抽核命中率 ≥98%，0 条 P0 虚构符号/数字
- **Evidence**: verification.md G2/G3 记录 + review.md CP-R2

### AC-2: 口径矛盾显式化（rule）

- **Type**: `rule`
- **Given**: R 阶段发现的 6 类矛盾（V1/V2 不可比、10/50 vs 10/51、IPC 量纲、检查数三口径、N=10 vs 15、行号漂移）
- **When**: 读者在 facts.md/相关概念页查阅
- **Then**: 每类矛盾均有"口径备注/勘误"留痕，给出两个出处行号与采用口径
- **Pass Condition**: 6/6 覆盖
- **Evidence**: facts.md 勘误段 + concept 14/15 正文

### AC-3: 结构与门禁全绿（rule）

- **Type**: `rule`
- **Given**: 29 文件落盘并完成三级注册
- **When**: 在 projects/awesome-okf-xs 下运行两门 + Sphinx dummy
- **Then**: check-bundles-index.py rc=0；check-toctrees.py 本束 0 红名；dummy rc=0 且本束 0 警告
- **Pass Condition**: 三条命令输出符合预期，verification.md G4/G5 粘贴证据
- **Evidence**: 命令输出日志 + review.md CP-R4

### AC-4: 教程教学质量（rubric）

- **Type**: `rubric`
- **Dimension**: 可读性、知识地图连贯性、概念间导航、读者能跟着示例走通一个假设的全生命周期
- **Scale**: 1-5
- **Anchors**: 1 = 事实堆砌无叙事；3 = 覆盖机制但跨章跳跃；5 = 分层导航清晰、每篇有"是什么/怎么实现/为什么这样设计/边界"、示例可独立走读
- **Pass Threshold**: >= 4
- **Evidence**: C 评审独立打分 + review.md CP-U1

### AC-5: 工程纪律（rule）

- **Type**: `rule`
- **Given**: 全部产出文件
- **When**: 机械扫描正文 20 篇（17 concepts+3 examples）
- **Then**: 0 file:///、0 external/dao、0 .tmp/.spec、0 `](../`、链接 hash 全为 40 字符；每篇结尾有束内导航；无重复 H1
- **Pass Condition**: 扫描 0 违例
- **Evidence**: verification.md G4 + review.md CP-R5

### AC-6: 双独立评审收口（rule）

- **Type**: `rule`
- **Given**: 实施完成
- **When**: V 门（fresh-context 子代理）与 C 门（另一 fresh-context 子代理）分别执行
- **Then**: V 的 G1-G5 全过并回填 verified.at；C 评审 pass（可先 fail→修复→复审 pass），review.md 仅 C 阶段创建
- **Pass Condition**: review.md 终态 Result=pass
- **Evidence**: .trae/specs/hwe-bench-okf-wiki/review.md

## Open Questions

- 无（分组/束名已确认；V2 原始数据不可得按 Non-Goals 处理）。
