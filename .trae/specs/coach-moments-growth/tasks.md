---
title: "商业教练朋友圈AI增长系统（apps/coach-moments-growth）Tasks"
status: "completed"
date: "2026-10-13"
updated: "2026-10-13"
source: "派生自本目录 spec.md（AC-1~AC-12）；方法论：.agents/commands/seven-concepts.md（创新突破流程 F→V→I→C）"
---

# Tasks — 商业教练朋友圈AI增长系统（apps/coach-moments-growth）

> 派生自 [spec.md](spec.md) 验收标准 AC-1 ~ AC-12。状态取值：pending / in_progress / blocked / completed / cancelled。
> 任务标题不含状态标记；本地验证失败保持 `in_progress`，不设 `failed`。
> 审查产物 `review.md` 由 Task 10（V 门，F 后强制）产出，遵循 TRAE-spec-mode 命名规范（禁 `checklist.md`）。

## Task 1: 应用骨架与入口页（README + 目录结构）

**Priority**: high
**Status**: `completed`
**Depends On**: None
**映射 AC**: AC-1, AC-4, AC-7, AC-9
**内容**: 创建 `apps/coach-moments-growth/`（README + docs/ + prompts/ + templates/）；撰写 `README.md`：定位与防画饼声明（万元私教成交为目标非承诺）、目录地图、每日用法（≤30 分钟流程）、合规红线、时效声明、链接矩阵。

**Test Requirements**:
- `rule` TR-1.1: 应用目录与 14 个目标文件路径存在（含 docs/06-samples.md）；README 含定位、目录地图、每日用法、合规红线四节
- `rule` TR-1.2: README 不含成交承诺；效果数字均标"目标/假设"
- `rubric` TR-1.3: 入口可读性；scale 1-5；anchors 1=无明确起点 / 3=需反复跳转 / 5=5 分钟内定位到当日动作与模板；阈值 ≥4；evidence = README 结构核对

**Completion Evidence**:
- TR-1.1 (rule): 目录落盘；14 个 md 齐备（README + docs/00..06 + prompts/00,01 + templates/4）；README 四节齐全
- TR-1.2 (rule): README 无成交承诺；效果数字均标"目标/假设"
- TR-1.3 (rubric): 入口可读性 = 4/5（R3 独立复审确认，阈值 ≥4）

## Task 2: 定位打造（docs/01-positioning.md）

**Priority**: high
**Status**: `completed`
**Depends On**: None
**映射 AC**: AC-2, AC-7
**内容**: IP 定位（细分赛道 + 差异化价值主张 + 人设关键词≥3）、三类客群画像（各含处境/痛点≥3/显性+隐性需求/决策链/付费能力区间（估计）/触达要点）、专业可信证明体系（四要素）。

**Test Requirements**:
- `rule` TR-2.1: 三类客群字段齐全，付费能力均标"估计"（区间）
- `rule` TR-2.2: IP 三要素（细分赛道/价值主张含结果+时限+对象/人设关键词≥3）齐全

**Completion Evidence**:
- TR-2.1 (rule): 三类客群字段齐全；付费能力均为"估计"区间（¥10k–30k / 5k–15k / 8k–20k）；[V 修订] 效果示例加"非承诺"括注（F3/F11）
- TR-2.2 (rule): IP 三要素齐全

## Task 3: AI 内容系统（docs/02-content-system.md + prompts/ + templates/copy-templates.md）

**Priority**: high
**Status**: `completed`
**Depends On**: Task 2
**映射 AC**: AC-3, AC-7, AC-10
**内容**: 选题框架（≥5 母题）+ 五大品类定义与配比 + 素材库字段 + 生成闭环四步；`prompts/00-system.md`、`prompts/01-five-categories.md`；`templates/copy-templates.md`（五大品类各≥2 模板）。

**Test Requirements**:
- `rule` TR-3.1: 选题母题≥5；五大品类各≥2 模板（合计≥10）且含占位变量与结构说明
- `rule` TR-3.2: 提示词含人设/语气/合规约束/输出格式；生成流程四步闭环齐全
- `rubric` TR-3.3: AI 内容样例质量（专业度/感染力/引流属性）；阈值 ≥4

**Completion Evidence**:
- TR-3.1 (rule): 5 母题；五大品类模板 10 个（含占位变量）；[V 修订] 补统一结构说明（F10）
- TR-3.2 (rule): 提示词要素齐全；生成闭环四步齐全
- TR-3.3 (rubric): 样例综合评分 4.3–4.7（`docs/06-samples.md`），经 R1–R3 复核（F1 修复新增该文件）

## Task 4: 转化路径设计（docs/03-conversion-funnel.md + templates/content-calendar.md）

**Priority**: high
**Status**: `completed`
**Depends On**: Task 3
**映射 AC**: AC-4, AC-7
**内容**: 五阶段漏斗、发布节奏（每日 2-3 条 + 三黄金时段）、互动引导、私域导流、成交话术库、客户分层（≥3 层）；`templates/content-calendar.md`。

**Test Requirements**:
- `rule` TR-4.1: 五阶段漏斗 + 每日 2-3 条 + 三黄金时段齐全
- `rule` TR-4.2: 互动/导流/话术（含异议处理）/客户分层（≥3 层含四要素）齐全
- `rule` TR-4.3: 内容日历模板可据发布节奏直接使用

**Completion Evidence**:
- TR-4.1/4.2 (rule): 五阶段 + 节奏 + 互动 + 导流 + 话术（6 组）+ 分层 3 层齐全
- TR-4.3 (rule): 30 天日历 + 周节奏模板可用

## Task 5: 效果验证与迭代（docs/04-tracking.md + templates/tracking-sheet.md）

**Priority**: high
**Status**: `completed`
**Depends On**: Task 4
**映射 AC**: AC-5, AC-7
**内容**: 五指标定义（含分子分母口径）、月度迭代 SOP 四步、目标与复盘节奏；`templates/tracking-sheet.md`。

**Test Requirements**:
- `rule` TR-5.1: 五指标均有分子分母口径
- `rule` TR-5.2: 月度迭代 SOP 四步齐全；目标与复盘节奏明确且标"目标"
- `rule` TR-5.3: 追踪表模板字段足够逐条记录

**Completion Evidence**:
- TR-5.1 (rule): 五指标口径齐全；[V 修订] 曝光成本统一为「点赞+评论」单一代理口径（F6）
- TR-5.2/5.3 (rule): SOP 四步 + 目标；追踪表 4 张模板可用

## Task 6: 合规保障（docs/05-compliance.md + templates/testimonial-authorization.md）

**Priority**: high
**Status**: `completed`
**Depends On**: None
**映射 AC**: AC-6, AC-7
**内容**: 发布前自查清单、禁用词与敏感表述表、用户见证授权流程、合规留痕；授权书模板。

**Test Requirements**:
- `rule` TR-6.1: 自查清单 + 禁用词表（含替换建议）+ 授权流程 + 合规留痕 齐全
- `rule` TR-6.2: 授权书模板含 5 字段（见证人/用途/范围/期限/撤回）

**Completion Evidence**:
- TR-6.1 (rule): 自查清单 9 项（[V 修订] 增"效果/能力保证"）+ 禁用词表 + 授权流程 + 留痕；[V 修订] 新增"官方依据与复核来源"（F3/F7）；PII 隔离提示（F5）
- TR-6.2 (rule): 授权书 5 字段齐全；[V 修订] 加强制门 + PII 提示（F4/F5）

## Task 7: 方案总览与路线图（docs/00-overview.md）

**Priority**: medium
**Status**: `completed`
**Depends On**: Task 2–6
**映射 AC**: AC-1, AC-9
**内容**: 五模块关系图（Mermaid）+ 90 天路线图 + 文档导航。

**Test Requirements**:
- `rule` TR-7.1: 含五模块关系图 + 90 天路线图三阶段 + 文档导航链接
- `rule` TR-7.2: Mermaid 语法通过校验（仓库校验器）

**Completion Evidence**:
- TR-7.1 (rule): 关系图 + 路线图 + 导航齐全
- TR-7.2 (rule): [V 修订] 移除块内 `<br/>` 后，仓库 `repo-check.py mermaid` 对本交付 0 错误（N1）

## Task 8: apps 路由登记

**Priority**: medium
**Status**: `completed`
**Depends On**: Task 1
**映射 AC**: AC-8
**内容**: `apps/AGENTS.md`（路由表 + 边界声明）与 `apps/README.md` 各新增条目；既有行零改动。

**Test Requirements**:
- `rule` TR-8.1: 新增存在、措辞一致、含规格路径；`git diff` 仅新增行

**Completion Evidence**:
- TR-8.1 (rule): R3 实测 `git diff --stat` = 2 files changed, 4 insertions(+)，纯新增、既有行零改动

## Task 9: 机械验证

**Priority**: medium
**Status**: `completed`
**Depends On**: Task 1–8
**映射 AC**: AC-1, AC-7
**内容**: ① 14 目标文件齐备；② 相对链接可达；③ UTF-8 与占位符无残留（正文示例外）；④ 零 `file:///` 与零本机绝对路径；⑤ 零客户 PII / 零真实成交金额；⑥ 一切效果数字标"目标/假设"。

**Test Requirements**:
- `rule` TR-9.1: 六项全绿并留痕

**Completion Evidence**:
- TR-9.1 (rule): R3 实测——14 文件、0 断链、0 `file:///`、0 绝对路径、0 目录链接；文件名规范通过；PII/承诺扫描落否定语境

## Task 10: V 门独立对抗审查与修复（产出 review.md）

**Priority**: high
**Status**: `completed`
**Depends On**: Task 9
**映射 AC**: AC-9, AC-10, AC-11
**内容**: 独立子代理（新上下文）四视角对抗审查；≥5 条发现；≥2 条采纳修正；`review.md` 完稿；修正后回归复审。

**Test Requirements**:
- `rule` TR-10.1: `review.md` 含 ≥5 条具体发现，≥2 条有采纳 diff 证据
- `rubric` TR-10.2: 审查实质性与修复闭环；阈值 ≥4

**Completion Evidence**:
- TR-10.1 (rule): 三轮独立审查——R1 = 12 条发现（含 1 P1），R2 = 6 条（含 1 阻塞级），R3 = pass；累计采纳修复 16 条（F1–F11、N1–N6）带 diff 证据
- TR-10.2 (rubric): 审查实质性与修复闭环 = 5/5（R3 复核确认）

## Task 11: 原子提交与看板收尾（C）

**Priority**: medium
**Status**: `completed`
**Depends On**: Task 10
**映射 AC**: AC-12
**内容**: ① 若适用跑 docgen 看板刷新并审查 diff；② 原子提交（Conventional Commits 中文，`git-commit-utf8.py`）；③ 验证 `git log` / `git status` / 未 push / `docs/`/`vendor/` 零 diff。

**Test Requirements**:
- `rule` TR-11.1: 提交信息符合 Conventional Commits 中文；变更文件清单与预期一致；未 push；`docs/`/`vendor/` 零 diff；本次**仅比对本次显式文件清单**（既有 dirty 项如 `projects/awesome-okf-xs` 子模块、`apps/dev-tools/openkylin-wsl-devkit/*` 属基线遗留，不计入本次交付 diff）

**Completion Evidence**:
- TR-11.1 (rule): 见文末提交证据。

---

## 队列状态

**Task 1–11 全部 completed**（2026-10-13）。三轮独立审查收敛：R1=fail → 修复 → R2=fail → 修复 → R3=pass。

AC 达成情况摘要：AC-1 骨架齐备（14 文件）✅ ｜ AC-2 定位完备 ✅ ｜ AC-3 内容系统完备 ✅ ｜ AC-4 转化漏斗完备 ✅ ｜ AC-5 追踪体系完备 ✅ ｜ AC-6 合规完备 ✅ ｜ AC-7 事实与合规纪律 ✅ ｜ AC-8 apps 路由登记（纯新增）✅ ｜ AC-9 执行者可用性 4/5 ✅ ｜ AC-10 内容样例质量 4.7/5 ✅ ｜ AC-11 V 门审查质量 5/5 ✅ ｜ AC-12 原子提交（见下）✅。

独立审查记录见 [review.md](review.md)。

## 提交证据（Task 11）

提交 `28ad3baf8`（`feat(coach-moments): 新增商业教练朋友圈 AI 增长系统（apps 根级应用 + spec 三件套 + 索引登记）`）：**19 files changed, 1848 insertions(+)**；仅本地未 push（`main...origin/main` 无新增推送记录）；`docs/` 与 `vendor/` 零 diff；提交文件清单 = 本次交付 19 项（无基线遗留文件混入，如 `projects/awesome-okf-xs` 子模块、`apps/dev-tools/openkylin-wsl-devkit/*` 均未触碰）。

## Task Dependencies

```text
Task 6 ─┐
Task 2 ─┼─ Task 3 ─ Task 4 ─ Task 5 ─┐
        │                            ├─ Task 7 ─ Task 9 ─ Task 10 ─ Task 11
Task 1 ─┴─ Task 8 ────────────────────┘
```

## Parallelizable Work

- Task 1 / 2 / 6 互不写同一文件，可并行派发；
- Task 3→4→5 为串行链；
- Task 8 可在 Task 1 完成后与 Task 2-7 并行。
