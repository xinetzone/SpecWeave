---
title: "知乎变现执行工作区（projects/monetize/zhihu-monetization）Tasks"
status: "draft"
date: "2026-09-23"
updated: "2026-09-23"
source: "派生自本目录 spec.md（AC-1~AC-10）；内容源：docs/retrospective/reports/competitive-analysis/zhihu-monetization-path-20260923/ + projects/awesome-okf-xs/doc/bundles/sheke/industry/zhihu-monetization/"
---

# Tasks — 知乎变现执行工作区（projects/monetize/zhihu-monetization）

> 派生自 [spec.md](spec.md) 验收标准 AC-1 ~ AC-10。状态取值：pending / in_progress / blocked / completed / cancelled。
> 任务标题不含状态标记；本地验证失败保持 `in_progress`，不设 `failed`。
> 审查产物 `review.md` 由 Task 7（V 门，F 后强制）产出，遵循 TRAE-spec-mode 命名规范（禁 `checklist.md`）。

## Task 1: 工作区骨架与入口页（README + .gitignore + local/）

**Priority**: high
**Status**: completed
**Depends On**: None
**映射 AC**: AC-1, AC-4, AC-5
**内容**: 创建 `projects/monetize/zhihu-monetization/`；写入 `.gitignore`（`local/*` + `!local/README.md`）与 `local/README.md`（隔离区机制说明：什么该放、什么禁入库）；撰写 `README.md`（frontmatter：`source` 双源 + `rule_snapshot` + `status: flagged` + `stale_after: 2026-12-31`；正文：定位与防画饼声明、链接矩阵（docs 四篇 + bundle 总览与关键篇目）、每日用法、数据隐私说明、时效复核）。

- [x] Subtask 1.1: 目录 + `.gitignore` + `local/README.md`
- [x] Subtask 1.2: `README.md` 入口页（链接矩阵 + 每日用法 + 时效声明）

**Test Requirements**:
- TR-1.1 (rule): 本任务三项产出存在；对 `local/` 下探测文件执行 `git check-ignore` 命中（local/README.md 除外）
- TR-1.2 (rule): README 链接矩阵含 docs 四篇与 bundle ≥4 个目标；frontmatter 五要素（source/rule_snapshot/flagged/stale_after + title）齐备
- TR-1.3 (rubric): 入口可读性（AC-8 的入口维度代理）；scale 1-5；anchors 1/3/5 = 需跨三处无顺序 / 需多次跳转 / 5 分钟内直达当日动作；阈值 ≥4；evidence = README 结构核对

**Completion Evidence**:
- TR-1.1 (rule): 三文件落盘（README.md 71 行 / local/README.md 30 行 / .gitignore 3 行）；`git check-ignore -v` 实测：`local/earnings/demo.csv` 命中 `local/*`、`local/README.md` 由 `!local/README.md` 负向规则放行（Task 6 复验）
- TR-1.2 (rule): 链接矩阵 9 目标（docs 4 + bundle 5）逐条 Test-Path 通过；frontmatter 8 字段齐备（含 flagged/stale_after 2026-12-31）
- TR-1.3 (rubric): 入口可读性 = 4/5——定位/执行/回写三步清晰、可点击链接化（主代理微修正：每日用法链接化 + 固定门表述回正）；V 阶段复核

## Task 2: 执行台账 tracker.md

**Priority**: high
**Status**: completed
**Depends On**: None（与 Task 1 并行；各自幂等建目录，互不写同一文件）
**映射 AC**: AC-1, AC-3, AC-7
**内容**: 按 spec FR3 撰写：关键时间锚点 / 第 1 周（W1-1~W1-6 + 9.29 Go/No-Go + 9.30 收官）/ 第 1 月（M1-1~M1-6、O-6）/ 持续期周期节奏 / 退出降频触发器 / 发布前固定门 / 复核锚点；每条 = 编号 + 动作短句 + 回链 + 勾选位与日期戳位；顶部固定勾选纪律与中断处置（指向 records.md）；frontmatter `source` 指回 docs todo 与主路径。

- [x] Subtask 2.1: 版面骨架（各区标题 + frontmatter + 勾选纪律）
- [x] Subtask 2.2: W1/M1/O 条目落地（全部编号 + 回链 + 日期戳位）
- [x] Subtask 2.3: 自检：编号清单与源 todo.md 双向比对（无遗漏、无新增）

**Test Requirements**:
- TR-2.1 (rule): 源 todo.md 全部行动项编号（W1-1~W1-6、M1-1~M1-6、O-1~O-6 及 9.29 决策、9.30 收官）在台账可检索且各带回链；反向无台账独有编号
- TR-2.2 (rule): 勾选纪律（勾选 + 日期戳、不删除条目、中断 ≥3 天回复核锚点）在顶部固定；中断处置指向 records.md

**Completion Evidence**:
- TR-2.1 (rule): tracker.md 落盘（V 门后 90 行，含 2 处 V 修订）；双向编号核对通过（W1-1~W1-6 / M1-1~M1-6 / O-1~O-6 / Go-No-Go / 9.30 收官 / 复核锚点 2 条均双侧有，无源外新增编号）；6 个唯一回链目标逐条验证存在
- TR-2.2 (rule): 勾选纪律四条置顶（勾选+日期戳 / 不删除条目 / 中断≥3天回复核锚点 / 中断登记指向 records.md 真实链接）；F 编号全部挂 article-source.md 链接，无裸写数字

## Task 3: 记录表 records.md

**Priority**: high
**Status**: completed
**Depends On**: None（与 Task 1/2 并行）
**映射 AC**: AC-1, AC-3, AC-7
**内容**: 四表模板（到账 / 周核对 / 周期复盘 / 发布自检留痕），占位显式标"示例/待填"；表头字段对齐 W1-6、M1-2/M1-3、O-6 与主路径 §五自检口径；frontmatter `source` 双源。

- [x] Subtask 3.1: 到账记录表 + 周核对表
- [x] Subtask 3.2: 周期复盘表（含 F-059 折算口径链接）+ 发布自检留痕表

**Test Requirements**:
- TR-3.1 (rule): 四表齐备；零真实数据（占位均标"示例/待填"）
- TR-3.2 (rule): 折算口径引用 F-059 且带 bundle 链接；表内零无源数字

**Completion Evidence**:
- TR-3.1 (rule): records.md 73 行；五部分齐备（到账 / 周核对 / 中断登记 / 周期复盘 / 发布自检留痕）；占位全部标「示例（待填）」；零真实数据
- TR-3.2 (rule): F-059 折算口径挂 article-source.md 链接；「建议初值 10 元/周」经回源核实为主路径 §七 L122 原文口径（非编造）；行号引用 L51 / L58-59 / L97-105 / L116-124 逐段核验准确；三问自检名称（删稿测试/占比自检/条款留痕）与 §五 L101-103 逐字一致

## Task 4: AGENTS.md（智能体入口）

**Priority**: high
**Status**: completed
**Depends On**: None（与 Task 1/2/3 并行）
**映射 AC**: AC-1, AC-5, AC-7
**内容**: 定位（主仓库直接跟踪的普通目录，非子模块）/ 文件地图与读写纪律（tracker、records 可写；`local/` 禁入库；docs 与 bundle 只读外链）/ 纪律传导（勾选纪律、三问自检、O-5 规则快照、flagged 与 2026-12-31 复核线、防画饼口径）/ 路由（知识 → bundle；定义 → docs；执行 → 本工作区）。

- [x] Subtask 4.1: 定位 + 文件地图表 + 读写纪律
- [x] Subtask 4.2: 纪律传导 + 路由表

**Test Requirements**:
- TR-4.1 (rule): 含路由三行（知识 / 定义 / 执行）与 `local/` 禁入库纪律、2026-12-31 复核线
- TR-4.2 (rule): 不重定义纪律——自检门等以"链接 + 执行方式说明"呈现，无新立规则

**Completion Evidence**:
- TR-4.1 (rule): AGENTS.md 57 行；五节齐备（项目定位 / 文件地图 / 读写纪律 / 纪律传导 / 路由表）；路由三行 + local/ 禁入库纪律 + 2026-12-31 复核线在位
- TR-4.2 (rule): 纪律传导表全部为「纪律 | 出处（引用，不重定义）」结构，零新立规则；`../../AGENTS.md`、`../../README.md`、docs 四篇、bundle index 全部链接验证存在

## Task 5: 区域索引登记

**Priority**: medium
**Status**: completed
**Depends On**: Task 1（README 存在）, Task 4（AGENTS.md 入口存在）
**映射 AC**: AC-6
**内容**: `projects/README.md`「现有子项目」表与 `projects/AGENTS.md`「子项目路由表」各新增一行（如体例需要亦补「可用资产索引」条目）；注明"主仓库直接跟踪，非子模块；入口 = `monetize/zhihu-monetization/AGENTS.md`"；措辞风格对齐既有行。

- [x] Subtask 5.1: `projects/README.md` 新增行
- [x] Subtask 5.2: `projects/AGENTS.md` 新增行（路由表 + 必要时资产索引）

**Test Requirements**:
- TR-5.1 (rule): 两处新增行存在、措辞一致、含"非子模块"；`git diff` 仅新增行（既有行零改动）

**Completion Evidence**:
- TR-5.1 (rule): `git diff --stat` 实测 = `2 files changed, 2 insertions(+)`——零删除、零改写（既有行原样）；两处新增行均含「变现执行工作区」「主仓库直接跟踪的普通目录，非 git 子模块」；新增链接目标（`projects/monetize/`、`projects/monetize/zhihu-monetization/AGENTS.md`）验证存在；资产索引小节本次未动（最小变更，留待后续如需）

## Task 6: 机械验证

**Priority**: medium
**Status**: completed
**Depends On**: Task 1, Task 2, Task 3, Task 4, Task 5
**映射 AC**: AC-2, AC-3, AC-4, AC-7
**内容**: 执行六项清单：① `python .agents/scripts/check-links.py --path projects/monetize/zhihu-monetization`（或手动逐条等效）；② UTF-8 与 frontmatter 字段核对；③ `git check-ignore` 隔离生效；④ 零 `file:///` 与零本机绝对路径；⑤ AC-3 抽查 3 条回链 + 零逐字复制；⑥ AC-7 数字清点挂 F。失败修复后复跑。

- [x] Subtask 6.1: 六项清单执行
- [x] Subtask 6.2: 失败项修复后复跑至全绿

**Test Requirements**:
- TR-6.1 (rule): 六项全绿并留痕（含命令输出或手动核对记录）

**Completion Evidence**:
- TR-6.1 (rule): ① 链接——`check-links.py` 结构性不覆盖 `projects/`（`lib/constants.py` 的 `EXCLUDED_DIRS` 含 "projects"，判定"找到 0 个 Markdown 文件"），按 AC-2 走手动等效：87 条相对链接 0 断链、`file:///` 0 条、索引 3 处新增目标存在；② UTF-8——6 文件解码正常、U+FFFD=0、无 BOM，4 文档 frontmatter 字段齐备；③ 隔离——探测路径命中 `local/*`；`local/README.md` 未被忽略（稳健判据：`git ls-files --others --exclude-standard` 实测恰 6 文件含 local/README.md；check-ignore 退出码依 git 版本而异，V-08 已勘误）；④ 敏感路径——零命中；⑤ AC-3——W1-2/M1-4/O-6 回链核对通过、5 条源验收整句检索零逐字复制；⑥ 数字清点——25 个唯一 F 编号引用全部存在于 67 条登记中，修复 1 处（tracker「8 个领域标签」补 F-038 链接）后复跑通过
- 残留风险 3 项（rule_snapshot 无 F 挂靠=与上游体例一致的豁免 / F-061 假期右端=源排期口径非本区引入 / records 单句引用已标「源文原文」）移送 V 门裁决

## Task 7: V 门独立对抗审查与修复（产出 review.md）

**Priority**: high
**Status**: completed
**Depends On**: Task 6
**映射 AC**: AC-8, AC-9
**内容**: 以**独立子代理（新上下文）**执行四视角对抗审查：魔鬼代言人（重复源 / 断链 / 画饼残留 / 数据泄漏）、新人（入口可用性）、执行者（每日流程是否 ≤5 分钟可上手）、未来（时效与规则变动风险）；产出 ≥5 条具体发现；≥2 条采纳修正（带"【V 修订】"或等价标注，无静默改写）；审查记录落 `review.md`（检查点 CP + Review History，按 TRAE-spec-mode 模板）；修正后回归复审。

- [x] Subtask 7.1: 独立审查执行（四视角，≥5 条发现）
- [x] Subtask 7.2: 修正 ≥2 条并回归复审；`review.md` 完稿

**Test Requirements**:
- TR-7.1 (rule): `review.md` 含 ≥5 条具体发现，≥2 条有采纳 diff 证据
- TR-7.2 (rubric): 审查实质性与修复闭环（AC-9 同维度）；阈值 ≥4

**Completion Evidence**:
- TR-7.1 (rule): `review.md` 101 行（CP-R1~R8 + CP-U1/U2，覆盖 AC-1~AC-10）；9 条具体发现（P1×1、P2×4、P3×4）——5 条 adopted 共 10 处最小修复（全部带 `【V 修订·2026-09-23】`，零静默改写）；V-06 rejected 转 Recommended Issue（3 项）
- TR-7.2 (rubric): 审查实质性与修复闭环 = 5/5（CP-U2，阈值 ≥4）；CP-U1（AC-8 新人可用性）= 4/5（阈值 ≥4，通过）；关键 P1 修复 V-01：数据隔离纪律三处矛盾（原指引会把真实数据写入入库文件）已全部改为「真实数据写 `local/`」；回归：链接 87→93 条 0 断链、F 编号 26/26 命中、结构零重排

## Task 8: 原子提交与看板收尾（C）

**Priority**: medium
**Status**: completed
**Depends On**: Task 7（审查通过）
**映射 AC**: AC-10
**内容**: ① 先跑 docgen 两条命令（`python .agents/scripts/docgen.py theme-dashboards`、`update-spec-readme`），检查 diff——仅纳入与本次相关变化，无关重写回退并留痕；② 按原子性提交（spec 区与工作区+索引分笔或合并单笔，单一职责优先），使用 `python .agents/scripts/git-commit-utf8.py -m "type(scope): 中文描述" <显式文件...>`；③ 验证 `git log` / `git status` / 未 push / docs 与 bundle 零 diff。

- [x] Subtask 8.1: docgen 看板刷新与 diff 审查（不可用则留痕）
- [x] Subtask 8.2: 原子提交（显式文件清单）
- [x] Subtask 8.3: 提交验证（顺序 / 内容 / 未 push / 零意外 diff）

**Test Requirements**:
- TR-8.1 (rule): 提交信息符合 Conventional Commits 中文；变更文件清单与预期一致；未 push；docs 与 bundle 零 diff

**Completion Evidence**:
- TR-8.1 (rule): 三笔提交（提交信息均为 Conventional Commits 中文，UTF-8 bytes 通道，仅本地未 push）——
  ① `821f7cfc7` `docs(spec): 新增知乎变现执行工作区 spec 与任务队列（含 V 门独立审查记录）`：4 文件 = spec.md / tasks.md / review.md / `.trae/specs/README.md`（627 insertions / 4 deletions）；
  ② `217c54cf9` `docs(projects): 新增知乎变现执行工作区（monetize/zhihu-monetization，链接 docs 报告与 OKF bundle，数据隔离 + 执行台账 + 索引登记）`：8 文件 = 工作区六文件（README/AGENTS/tracker/records/.gitignore/local/README）+ `projects/README.md` + `projects/AGENTS.md`（326 insertions / 0 deletions，两处索引为纯新增行）；
  ③ 本笔 `docs(spec): 收尾更新任务队列（Task 8 完成记录与提交证据）`：仅 tasks.md。
  机械核验：`git status -sb` 无 `ahead`/upstream 推送记录（未 push）；`git diff --submodule` 空输出（子模块指针零变动）；docs/ 与 `projects/awesome-okf-xs/doc/bundles/` 零 diff；`git show --stat HEAD~1` 抽查提交 2 文件清单恰为上述 8 项、不含任何无关文件；提交后 `git status --short` 仅余 S1 基线既有状态，用户 4 个疑似无关文件（`apps/containers/client/.agents/archive/2026-09-15-16.md`、`2026-09-20-p1.md`、`apps/containers/client/docs/04-troubleshooting-guide.md`、`docs/tech/references/development-standards.md`）实测在基线与提交后均为 clean（无 M），全程未 add、未触碰。
- Subtask 8.1 留痕（docgen 可用性 + diff 审查）：两条子命令均可用。`theme-dashboards` 刷新 13 个主题看板（本 spec 位于 `.trae/specs/` 顶层、无主题 README，被 docgen 跳过）。`update-spec-readme` 重生成全局看板（647 spec）。影响面审查与处置：① `.trae/specs/okf-wiki-ecosystem/README.md`（166+/160−，与本次无任何关系的整篇重排），S1 基线 clean 且仅被本次 docgen 改动 → 整文件 `git restore --` 回退；② `.trae/specs/README.md` 逐行收窄——回退 okf-wiki-ecosystem 165→171、infra-env 13/2/15→14/2/14 的计数漂移与兄弟 spec `create-zhihu-monetization-okf-wiki`（非本次产出）条目，仅保留本 spec 条目（1 spec / 0 完成 / 1 进行中）、合计 640/431/53/156（= 基线 639 + 本 spec 1，算术自洽）与生成日期 2026-09-21→2026-09-23，最终 `git diff --stat` 为该文件 10 行改动（6+/4−）；③ 零回退 S1 基线既有改动。

---

## 队列状态

**Task 1–8 全部 completed**（2026-09-23，C 门收尾完成：提交 `821f7cfc7` + `217c54cf9` + 本笔队列收尾，全部仅本地、未 push，队列已清空）。

AC 达成情况一行摘要：AC-1 六文件齐备 ✅ ｜ AC-2 链接全可达（93 条相对链接 0 断链、零 `file:///`）✅ ｜ AC-3 单一事实来源（抽查 3/3 通过、零逐字整句复制）✅ ｜ AC-4 数据隔离（`local/*` 命中忽略、`local/README.md` 正常入库）✅ ｜ AC-5 时效与风险传导（`rule_snapshot` / `status: flagged` / `stale_after: 2026-12-31` / 防画饼口径 / 复核提示）✅ ｜ AC-6 区域索引登记（两处各 +1 行、既有行零改动）✅ ｜ AC-7 溯源与事实纪律（F 编号 26/26 命中、零无源数字）✅ ｜ AC-8 执行者可用性 4/5（阈值 ≥4）✅ ｜ AC-9 V 门审查质量 5/5（阈值 ≥4）✅ ｜ AC-10 原子提交（三笔单一职责、Conventional Commits 中文、docs/ 与 bundle 零 diff、未 push）✅。

## Task Dependencies

```text
Task 1 ─┐
Task 2 ─┼─ Task 5 ─ Task 6 ─ Task 7 ─ Task 8
Task 3 ─┤      ↑
Task 4 ─┘──────┘
```

- Task 5 依赖 Task 1 + Task 4（入口链路就位后再登记）；
- Task 6 依赖 Task 1~5 全部产物；
- Task 7 依赖 Task 6（机械全绿后进入对抗审查）；
- Task 8 依赖 Task 7 审查通过（V 在 C 之前，不可倒置）；
- 任一 blocked 则队列不算清空，不得进入提交。

## Parallelizable Work

- Task 1 / 2 / 3 / 4 互不写同一文件，可并行派发（各自幂等建目录）；
- Task 5 与 Task 6 之间无并行空间（登记结果需纳入验证范围）。