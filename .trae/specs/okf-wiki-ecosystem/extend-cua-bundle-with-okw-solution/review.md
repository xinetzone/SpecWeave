# Cua 知识束扩展 × cua+okw 最优解 - Review Checklist

> 本文档仅在 Review 阶段填写。Specify 和 Plan 阶段不得修改此文件。

## Review History

| 轮次 | 日期 | 审查者 | 结果 | 备注 |
|------|------|--------|------|------|
| R1 | 2026-10-16 | 独立验证子代理（Task 8）+ 修复子代理（Task 10） | pass（修复后） | 首次审查发现 P0=0 / P1=1 / P2=3；P1 与 P2 已在 Task 10 修复；P1-2（父级索引被并行会话改动）判为**非本次变更**，如实标注 |

---

## 审查检查点

### 事实与溯源
- [x] **CP-1**: 第二篇所有关键事实（组件名、榜单数值、许可名称、命令、定价、日期）均有 F 编号引用（验证：F-066~F-154 共 89 号全部被定义且被引用，无悬空/错配）
- [x] **CP-2**: 双份 F 编号一致（spec `facts.md` ↔ 束 `references/second-article-facts.md`：各 89 行，集合相等、66~154 连续、差集 0）
- [x] **CP-3**: F-066 起与既有 F-001~F-065 无编号冲突、无重复；既有事实体未被改写（`git diff` 仅追加：`article-source.md` 仅 +1 行）
- [x] **CP-4**: P0 项均有核验结论（✅/⚠️/❌）与来源 URL；榜单/自述数据明确标注为转述值（第二轮 20 项 = 14✅/6⚠️/0❌）
- [x] **CP-5**: 跨信源对账四元组（现象/差异/影响/处置）覆盖 Fleets↔Spaces、SDK/CLI 命名、主语言、Stars 四版快照

### 合成章节（cua×okw）
- [x] **CP-6**: `concepts/06-cua-okw-solution.md` 顶部含**「合成设计（synthesis）· 未在本机实测」**声明（L35–37，且逐节复述边界）
- [x] **CP-7**: 全程无"已实测可用/验证通过/已跑通"等未经证据支持的表述（机械检索三串各 0 命中；声明块与正文措辞已改写）
- [x] **CP-8**: okw 侧事实均可回溯至 `apps/dev-tools/openkylin-wsl-devkit/README.md` 或 `apps/dev-tools/openkylin-wsl-devkit/doc/*`；无依据处以「待核」标注
- [x] **CP-9**: 章节覆盖：分层架构分工 / 模块选型判据表 / 组合路径 / 前置条件 / 风险与未验证项清单（6 小节齐备）
- [x] **CP-10**: 选型判据表对四类场景（无 GUI 命令任务 / 需 GUI 且要求隔离 / 可复现开发环境 / 评测与训练）均给出建议
- [x] **CP-11**: 未验证项写明验证路线（8 项：#1~#4 未验证含验证路线，#5~#8 风险含缓解方式）

### OKF 规范合规
- [x] **CP-12**: 目录结构符合 OKF v0.2（index + concepts/ + references/ + log，无 examples 且两问理由成立）
- [x] **CP-13**: 每个非保留 `.md` 文件含可解析 frontmatter 且 `type` 非空（12 个非保留文件通过；2 个子目录 `index.md` 按 OKF §10/§13 豁免）
- [x] **CP-14**: 每个 `index.md` 的 `{toctree}` 条目数与实际文件数一致（束根 3 / concepts 7 / references 3）
- [x] **CP-15**: 根 `index.md` 声明的文件计数 = 实际文件数（声明 14 = 实测 14）
- [x] **CP-16**: 相对链接全部可达，无 `file:///` 绝对路径（14 个 md、168 条相对链接 BROKEN=0，含 10 层深链指向 `docs/`、`apps/`）
- [x] **CP-17**: 时效性内容标注时点；`stale_after` 未早于 2026-12-31（`03`/`02` 快照与 API 时点分列；F-140 带 2026-10-16 时点）

### 索引与计数
- [x] **CP-18**: `concepts/index.md`、`references/index.md` 导航表与 toctree 均已收录新增文档
- [x] **CP-19**: 本次变更**未改动**父级/域/总索引计数（`git diff` 对 `doc/bundles/index.md`、`jishu/ai/index.md` 检索 "cua" **0 命中**；其改动来自并行会话的 `wecom-topic-scenarios` 束，与本 spec 无关，按"不回滚用户/并行改动"原则未触碰）
- [x] **CP-20**: 新章节可从束根经 toctree 到达（根 `index.md` → `concepts/index` → `06-cua-okw-solution`）

### 机械门禁
- [x] **CP-21**: toctree 完整性通过（`python scripts/check-toctrees.py` → exit 0；`invoke gates.toctrees` 因本机 `invocations` 包元数据缺失不可用，属环境故障非项目问题）
- [x] **CP-22**: 计数对账通过（`python scripts/check-bundles-index.py` → exit 0「9 域/61 组/641 束，五面一致」；641 含并行会话新增束）
- [x] **CP-23**: UTF-8 通过（`python scripts/check-utf8.py` → exit 0「11688 文件有效 UTF-8」）

### 交付
- [x] **CP-24**: `log.md` 含第二轮 R→I→E→V 记录与 G1–G4 结论（并已回填 Task 8 四视角结论；文件状态为 新增 2 / 修改 8 / 沿用 4）
- [x] **CP-25**: 子模块内原子提交完成，仅含本次束改动（commit `137483e7`，10 files changed, 643 insertions(+), 29 deletions(-)；工作区剩余改动均为并行会话产物）

---

## 可行动发现（Actionable Findings）

| # | 严重程度 | 发现描述 | 对应 AC | 修复建议 | 状态 |
|---|---------|---------|---------|---------|------|
| 1 | P1 | 核验分级计数不一致：§6 结论表为 14✅/6⚠️，但正文与索引多处写作 13✅/7⚠️ | AC-3, AC-6 | 以表为准归一化为 14✅/6⚠️/0❌ | ✅ 已修复（Task 10） |
| 2 | P1 | 工作区 `doc/bundles/index.md`、`jishu/ai/index.md` 出现改动（计数 640→641） | AC-8 | 判定归属：来自并行会话 `wecom-topic-scenarios` 束（diff 无 cua 字样）；**不回滚**，提交时显式指定路径隔离 | ✅ 已处置（Task 9 路径隔离 + log 备注） |
| 3 | P2 | `log.md` 第二轮文件状态汇总"修改 5/沿用 7"与实测（修改 8/沿用 4）不符 | AC-7 | 更正汇总与清单 #4/#8/#11 状态列 | ✅ 已修复（Task 10） |
| 4 | P2 | `references/second-article-facts.md` 的 `status: draft` 异于束内 `stable` | AC-7 | 改为 `stable` | ✅ 已修复（Task 10） |
| 5 | P2 | `concepts/06` 声明块含字面串，可能被门禁误判 | AC-5 | 改写为不含易误判字面串的等价表述 | ✅ 已修复（Task 10 + 复核） |
