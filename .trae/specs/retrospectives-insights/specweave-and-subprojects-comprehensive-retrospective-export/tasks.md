---
type: Tasks
id: "specweave-and-subprojects-comprehensive-retrospective-export-tasks"
version: "1.0.0"
source: "spec.md（同目录）"
---

# Tasks：SpecWeave 与其第一方子项目全面复盘

## Task 1: 启动三前置与范围锁定

- [x] **Status**: `completed`
- **Priority**: P0
- **Depends On**: —
- **Description**: 读取磁盘 `AGENTS.md`、`context-routing.md`、`projects/AGENTS.md`、`apps/AGENTS.md`；完成内容敏感度预检（公开）；探测 git/python 全路径；向用户确认范围（第一方全量）与申请处理方式。
- **AC Addressed**: —
- **Test Requirements**: 三个锚点（启动协议 / 文档边界 / 内容敏感度预检）同时存在
- **Notes**: 用户选择「第一方全量」；Meoo 申请选择「先调研→给草稿→用户确认」
- **Completion Evidence**: `git` 探测为 `C:\Program Files\Git\cmd\git.exe`；python 为 `D:\Users\xinzo\anaconda3\python.exe`（py314 环境 `D:\Users\xinzo\anaconda3\envs\py314\python.exe`）

## Task 2: R 事实采集

- [x] **Status**: `completed`
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 采集全量时间跨度、提交构成、贡献者、四区域资产规模、子项目各自提交量、CI 门禁结构、增量窗口事件、工作区时点状态；编号 F-001 起。
- **AC Addressed**: AC-1、AC-2
- **Test Requirements**: G1 门——Grep 因果词（因为/导致/所以/由于/因此）命中数为 0；抽查 ≥10 条回溯
- **Notes**: 全量数 + 增量窗口（2026-07-20 起）双轨记录
- **Completion Evidence**: `facts.md` F-001~F-069；抽查表 11/11 命中（见 `facts.md` §抽查记录）

## Task 3: I 洞察萃取

- [x] **Status**: `completed`
- **Priority**: P0
- **Depends On**: Task 2
- **Description**: 提炼 5 条四元组洞察，与 2026-07-19 基线报告做差异分析（强化/反转/新增/无变化）。
- **AC Addressed**: AC-3
- **Test Requirements**: G2 门——每条四元组完整、引用 ≥2 个 F 编号、无悬空引用、深度自评 ≥4
- **Notes**: 系统性根因表述为「与现有事实一致的一种解释」，并列出竞争假设
- **Completion Evidence**: `insights.md` I-1~I-5

## Task 4: E 模式萃取与去重裁决

- [x] **Status**: `completed`
- **Priority**: P1
- **Depends On**: Task 3
- **Description**: 对两个候选模式分别裁决：C1（跨期指标口径对齐）→ 新建 L1；C2（身份别名归并计量）→ 并入既有 `community-metric-triple-check`。
- **AC Addressed**: AC-4、AC-10
- **Test Requirements**: G3 门——新建模式含触发场景（适用/不适用）、核心步骤、反模式、迁移验证；并入差异点 ≤3 条且原内容零损失
- **Notes**: 通用动作表述，专有值降为案例证据
- **Completion Evidence**: `e-stage-pattern.md`

## Task 5: V 对抗审查

- [x] **Status**: `completed`
- **Priority**: P1
- **Depends On**: Task 3
- **Description**: 四视角（魔鬼代言人/新人/老板/未来）攻击洞察与结论，意见 ≥5 条，采纳 ≥2 条。
- **AC Addressed**: AC-5
- **Test Requirements**: 必含 ≥1 条指向事实证据强度不足；不采纳意见附理由
- **Notes**: E 阶段不改写 I 结论，限定以下传方式处理
- **Completion Evidence**: `v-adversarial-review.md` V-1~V-6，采纳 4 条

## Task 6: A 原子行动项

- [x] **Status**: `completed`
- **Priority**: P1
- **Depends On**: Task 5
- **Description**: 产出 7 条行动项，逐条含优先级/Owner/触发条件/可判定验收标准。
- **AC Addressed**: AC-6
- **Test Requirements**: G4 门——单一职责、可独立验证；无空话式表述
- **Notes**: 与 07-19 报告 8 条行动项的遗留项区分标注
- **Completion Evidence**: `actionable-items.md` A-1~A-7

## Task 7: 报告归档与索引登记

- [x] **Status**: `completed`
- **Priority**: P0
- **Depends On**: Task 4、Task 6
- **Description**: 落盘报告四文件；登记 `project-reports/index.md` 与 `project-reports/README.md`；完成模式入库四处登记。
- **AC Addressed**: AC-7、AC-10、AC-11
- **Test Requirements**: `index.md` 为纯 toctree 无 frontmatter；三件套 frontmatter 含 `type`/`source`
- **Notes**: 域 toctree 按字母序；主索引总表最易遗漏
- **Completion Evidence**: 报告目录四文件 + 模式四处登记（详见 `review.md` Completion Evidence）

## Task 8: 质量门与独立审查

- [x] **Status**: `completed`
- **Priority**: P0
- **Depends On**: Task 7
- **Description**: 运行 `check-links.py`（报告目录 + 模式库目录）、YAML/TOML 解析实测、禁用项 Grep；委派 fresh-context 只读子代理执行独立审查并回填 `review.md`。
- **AC Addressed**: AC-8、AC-9、AC-11
- **Test Requirements**: 断链 0 新增；禁用项命中 0；P0 项修复并回归
- **Notes**: 既有无关文件的历史断链须用 git log 证明非本次引入
- **Completion Evidence**: `review.md` 勾选表（AC 12/12 通过）+ 发现处置（P0 1 条、P1 3 条、P2 4 条全部修复或记录）+ 回归证据（报告目录、模式域目录与 Spec 目录三处 `check-links.py` 全部通过）

## Task 9: 原子提交（待用户指令）

- [ ] **Status**: `pending`
- **Priority**: P2
- **Depends On**: Task 8
- **Description**: 用户明确指令后，按单一职责拆分提交（建议：报告归档 / 模式入库与并入 / 索引登记 / Spec 三件套），默认不推送。
- **AC Addressed**: AC-12
- **Test Requirements**: 走 atomic-commit-cmd 三查暂存法
- **Notes**: 未经明确指令不创建提交
- **Completion Evidence**: —
