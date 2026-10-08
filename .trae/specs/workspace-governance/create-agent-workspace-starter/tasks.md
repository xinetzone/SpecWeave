# 智能体工作区起步套件（Agent Workspace Starter）- Implementation Plan

> 方法论：seven-concepts（知识沉淀→产品化），链路 R→I→E→V→C；G1-G4 质量门强制。
> 状态字典：`pending` / `in_progress` / `blocked` / `completed` / `cancelled`。
> 关联 spec：[spec.md](spec.md)（AC-1 ~ AC-9）。

## Task 1: R-事实采集——.agents 全貌与「1 小时可消化」量化基线

- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 枚举 `.agents/` 顶层类目与候选萃取文件（含行数），形成「保留 / 剔除」候选清单
  - 建立量化基线：类目数、各类目候选代表、教程 + 演练行数预算分配表
  - 产出 `facts.md`（本 spec 目录），G1 门：事实无因果词（「因为 / 导致 / 所以」）
- **Acceptance Criteria Addressed**: AC-1, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-1.1: `facts.md` 覆盖 ≥10 个类目，每条含「文件路径 + 行数 + 保留/剔除建议」，全篇无因果词
  - `rule` TR-1.2: 行数预算表成立——教程（≤900 行）+ 演练（≤600 行）合计 ≤1500 行（NFR-1）
- **Completion Evidence**:
  - [facts.md](facts.md) 落盘：12 类目候选清单（每行含文件 + 实测行数 + 保留/精简/导览/剔除建议）
  - 因果词自查 0 命中；行数预算表 40 文件 ≤50、教程 900 + 演练 600 = 1500 行
  - 偏差勘误：`templates/agent-workspace-hub/` 实测 28 文件 / 19,918 字节（spec Background 原记 51 文件为误），已记录于 facts.md §1.4 并回改 spec.md

## Task 2: I-洞察——产品化取舍标准与体验设计

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 提炼「什么让 1 小时上手成为可能 / 不可能」四元组洞察（现象 / 根因 / 影响 / 建议，≥3 条），G2 门
  - 确定 starter 萃取清单（类目 → 代表文件映射）、60 分钟时间盒分配、演练任务体量与形态定稿
  - 产出 `insight.md`（本 spec 目录）
- **Acceptance Criteria Addressed**: AC-5, AC-6, AC-9
- **Test Requirements**:
  - `rule` TR-2.1: ≥3 条四元组洞察，每条四要素齐备（现象 / 根因 / 影响 / 建议）
  - `rule` TR-2.2: 萃取清单（类目 × 文件 × 行数）+ 时间盒分配表（10/15/25/10 分钟）产出且与 facts.md 基线一致
- **Completion Evidence**:
  - [insight.md](insight.md) 落盘：4 条四元组洞察（G2 自查通过，每条四要素齐备且引用 facts.md 实测数据）
  - 萃取清单定稿：40 文件 / 18 类目（三态分布：保留原件 16、精简改写 15、新建 9）
  - 时间盒定稿 10/15/25/10；演练选题「目录树查看器」规格驱动（含 4 项产出物 + 7 步剧本）；行数分配 900 + 600 = 1500

## Task 3: E-萃取——starter/ 最小化套件

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 创建 `apps/dev-tools/agent-workspace-starter/starter/`：根 `AGENTS.md` 最小契约（含「启动协议」锚点）+ `.agents/` 全貌导览（每类目代表文件 + 一句话导览）
  - 所有萃取文件带 `source` frontmatter 溯源；原创文件注明原创
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-6, AC-8
- **Test Requirements**:
  - `rule` TR-3.1: starter 文件数 ≤50；`AGENTS.md` 含「启动协议」关键词且启动协议结构完整
  - `rule` TR-3.2: ≥9 个类目各有 ≥1 代表文件；萃取文件 100% 带 `source` 字段
  - `rule` TR-3.3: 相对链接 0 断链（check-links 或等效验证）
- **Completion Evidence**:
  - starter/ 落地 40 文件（≤50 ✓）、内容 1429 行；18 类目覆盖（≥9 ✓）
  - 「启动协议」关键词命中 3 处；`source` 覆盖率 40/40；`x-toml-ref` 残留 0、`file:///` 残留 0
  - 独立复核（父代理复跑）：全量 142 条相对链接仅剩 3 条待建项（`../bootstrap-prompt.md` ×2、`../scripts/verify_starter.py` ×1，均属 Task 6/7 产出，非缺陷），starter/ 内部链接闭环 0 断链

## Task 4: E-萃取——60 分钟时间盒教程 guide/

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - `guide/README.md`（学习路径总览 + 时间盒表）+ `00-overview.md` / `01-bootstrap.md` / `02-first-task.md` / `03-next-steps.md` 四段教程
  - 每段含：目标、时长、步骤、完成检查点
- **Acceptance Criteria Addressed**: AC-1, AC-5, AC-9
- **Test Requirements**:
  - `rule` TR-4.1: 总览含 4 段时间盒表（10/15/25/10＝60 分钟）；四段文件齐备
  - `rubric` TR-4.2: 教程可消化度；scale 1-5；anchors 1 = 单段超 400 行且无检查点 / 3 = 总量 800-1200 行 / 5 = 总量 ≤900 行且每段有完成检查点；threshold ≥4；证据＝行数统计 + 模拟新人试走
- **Completion Evidence**:
  - guide/ 落地 5 文件 362 行（≤900 ✓；README 49 / 00 81 / 01 84 / 02 86 / 03 62）
  - 4 段时间盒表（10/15/25/10）与每段「完成检查点」齐备；链接指向产品内约定路径，无 `file:///`
  - `rubric` TR-4.2 自评 4/5：总量远低于 900 行、每段检查点齐备；「模拟新人试走」证据待 Task 8 四视角审查补强

## Task 5: E-萃取——规格驱动小任务演练剧本 walkthrough/

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 演练剧本：任务书 → 写 spec（附可照抄样例）→ 实施 → 产出物 → 验收，每步含「照抄块」与可观察验收点
  - 选题按 Task 2 定稿（候选：单文件小工具的规格驱动开发）
- **Acceptance Criteria Addressed**: AC-1, AC-5
- **Test Requirements**:
  - `rule` TR-5.1: 剧本 ≥6 个步骤，每步含可复制命令/内容 + 验收点
  - `rule` TR-5.2: 依剧本可产出具体文件级交付物；剧本总量 ≤600 行、对应 25 分钟段位
- **Completion Evidence**:
  - walkthrough/ 落地 4 文件 336 行（≤600 ✓；README 63 / step-1 99 / step-2 109 / step-3 65）
  - 参考实现 `tree_view.py` 实测（py314）：`--max-depth 2` 输出与文档样例逐字一致、退出码 0；错误路径退出码 2；临时测试目录已清理
  - 7 步导航 + 4 项产出物清单 + 每步验收点齐备；选题「目录树查看器」与 insight.md §4 定稿一致

## Task 6: E-萃取——自检脚本与装载门面

- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - `scripts/verify_starter.py`：零依赖自检（文件齐备性 / 「启动协议」关键词锚 / 相对链接可达），exit code + 中文缺项报告
  - `bootstrap-prompt.md`（一句话装载提示词：安全规则 + 幂等）+ `skill/SKILL.md`（五要素门面）
- **Acceptance Criteria Addressed**: AC-2, AC-4
- **Test Requirements**:
  - `rule` TR-6.1: py314 运行两态验证通过——完整 starter exit 0；移除任一必需文件后 exit 非 0 且列出缺项
  - `rule` TR-6.2: 提示词含 ≥6 条安全规则 + 幂等条款；SKILL.md frontmatter 完整（name/description/version）且描述触发条件
- **Completion Evidence**:
  - `scripts/verify_starter.py`（239 行）落地；独立复跑（父代理）：完整态 exit 0（40/40 文件齐备、「启动协议」关键词命中、81 条相对链接全可达）；缺失态（临时副本移除 `.agents/modules/README.md`）exit 1 且逐条列出缺项；临时目录已清理
  - `bootstrap-prompt.md`（111 行）含 8 条安全规则（S1-S8）与幂等条款；`skill/SKILL.md`（58 行）frontmatter 含 name/description/version
  - 产品全目录 174 条相对链接 0 断链（父代理独立复跑）

## Task 7: E-萃取——运营落地页与许可边界

- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 3, Task 4
- **Description**:
  - `README.md` 落地页：价值主张 / 内容清单 / 1 小时路径 / 许可与使用边界 / 获取方式（占位）
  - starter 内含简短许可说明文件
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `rubric` TR-7.1: 运营可用性；scale 1-5；anchors 1 = 无价值主张 / 3 = 有主张与清单缺许可边界 / 5 = 五要素齐备且文案可直接复用；threshold ≥4；证据＝README 逐节审查
- **Completion Evidence**:
  - 产品根 `README.md` 落盘（首版 132 行 → Task 8 修正后 133 行）；AC-9 五要素齐备（价值主张 / 内容清单 / 1 小时路径 / 许可与使用边界 / 获取方式占位）
  - `rubric` TR-7.1 自评 5/5：文案可直接复用；许可表述与 `starter/LICENSE-NOTICE.md` 口径一致；规模数据与产物一致（starter 40/1429、guide 5/362、walkthrough 4/338——A-4 修正后 +2 行）
  - 复核：README 内链接全部可达（含并行产物 `bootstrap-prompt.md`、`scripts/verify_starter.py`）；starter 内许可说明文件（LICENSE-NOTICE.md）已由 Task 3 交付并核对

## Task 8: V-对抗审查——四视角攻击并修正

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3, Task 4, Task 5, Task 6, Task 7
- **Description**:
  - 以买家 / 时间 / 新手 / 运营者四视角审查全部交付物，产出 ≥5 条具体意见并采纳 ≥2 条修正
  - 审查记录产出为 `adversarial-review.md`（本 spec 目录）
- **Acceptance Criteria Addressed**: AC-5, AC-6, AC-9
- **Test Requirements**:
  - `rule` TR-8.1: ≥5 条意见（含视角 / 问题 / 建议），采纳 ≥2 条且修正落地可查（diff 或文件内容）
- **Completion Evidence**:
  - [adversarial-review.md](adversarial-review.md) 落盘：7 条意见（四视角各 ≥1 条）、采纳 4 条修正落地（A-1 自检命令位置错误 / A-2 Apache-2.0 许可归属缺口 / A-3 Python 版本口径矛盾 / A-4 样例与 AC 不一致）、2 条记录待办（A-5 时间盒再平衡、A-7 运营占位）、1 条不采纳附理由（A-6）
  - 新手实测走查（临时目录模拟买家）：核心链路可照抄跑通、样例输出逐字一致；唯一硬卡壳（A-1）已修正；耗时估算 42~54 分钟，60 分钟时间盒成立
  - 复测：自检脚本 exit 0、全产品 175 条相对链接 0 断链、starter 40 文件 ≤50；行数微调（README 133 行、walkthrough 合计 338 行）于 Task 9 同步

## Task 9: C-原子提交——区域登记、校验与交付

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - 更新 apps/AGENTS.md 路由表 + apps/README.md 清单；运行 docgen 刷新应用清单
  - 链接检查 + 规模校验（NFR-1）；三查暂存法原子提交（Conventional Commits 中文）
- **Acceptance Criteria Addressed**: AC-7, AC-3
- **Test Requirements**:
  - `rule` TR-9.1: apps/AGENTS.md 与 apps/README.md 两处登记命中；docgen 运行成功；链接检查 0 断链
  - `rule` TR-9.2: 原子提交完成——单次提交单一职责，提交信息为 Conventional Commits 中文格式
- **Completion Evidence**:
  - 区域登记 3 处：apps/AGENTS.md 路由表与边界声明、apps/README.md dev-tools 分组清单（grep 命中）
  - docgen 运行成功（`docgen.py apps` 退出 0，无净变化——APPS_TABLE 仅列 apps/ 一级条目）
  - 校验：自检脚本 exit 0、全产品 175 条链接 0 断链、starter 40 文件 ≤50
  - 原子提交 `c8b5114f1`（60 文件 / +3668 insertions）：产品六件套 + spec 目录 + 区域登记；采用部分暂存法保护他人变更——cached diff 中 `dao-survival-guide` 命中 0；提交后他人 3 行变更完好保留为未暂存修改（父代理独立复核：HEAD 快照 dao=0 / aws=2+1，残留 diff 恰为 dao 3 行）

# Task Dependencies

- Task 2 依赖 Task 1
- Task 3 / Task 4 / Task 5 依赖 Task 2（三者写不同目录，可并行委托）
- Task 6 依赖 Task 3；Task 7 依赖 Task 3 与 Task 4
- Task 8 依赖 Task 3 ~ Task 7 全部完成
- Task 9 依赖 Task 8