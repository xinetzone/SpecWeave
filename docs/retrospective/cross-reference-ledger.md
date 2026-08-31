---
type: Reference
title: "双体系引用收敛台账（ACT-5）"
date: "2026-08-31"
status: active
source: "docs/retrospective/reports/concepts/milestone/docs-full-retrospective-20260831.md 第六章 ACT-5"
---

# 双体系引用收敛台账（ACT-5）

> 本台账登记 `docs/`（OKF v0.2 文档中心）与 `.agents/docs/`（智能体执行配套文档）双体系之间的存量跨区引用，执行"冻结新增、存量分批、声明对齐"治理策略。
>
> 决策记录：2026-08-31 经用户确认——①方向：冻结 + 台账 + 声明修订；②复盘目录归属：以 `docs/retrospective/` 为准，`.agents/docs/retrospective/` 为历史归档、冻结新增。

## 一、边界规则（2026-08-31 生效）

| 规则 | 内容 | 落位 |
|------|------|------|
| R1 | 新增对外可读文档（Wiki/知识包/报告/教程）一律入根 `docs/` | 根 AGENTS.md 文档边界条款 |
| R2 | `docs/` 内文档**不得新增**指向 `.agents/docs/` 的跨区引用（冻结） | 根 AGENTS.md + global-core-rules 路径解析规则 |
| R3 | 复盘报告与模式库以 `docs/retrospective/` 为准；`.agents/docs/retrospective/` 冻结新增，仅作历史归档 | 根 AGENTS.md + global-core-rules |
| R4 | `.agents/` 规范内引用根 `docs/` 知识源时使用 `../docs/...` 相对路径；引用 `.agents/docs/` 时使用 `docs/...` | global-core-rules 路径解析规则 |
| R5 | 路径引用一律以文件实际位置为准，禁止沿用"docs/ 自动解析为 .agents/docs/"的历史隐式规则 | global-core-rules 路径解析规则 |
| R6 | `docs/` 指向 `.agents/scripts|skills|commands|rules|templates` 等规范执行层的引用为体系间合法导航（脚本/技能唯一实体在 `.agents/`），不改写，但须保证路径有效 | 本台账 B3 批次 |

## 二、存量基线（2026-08-31 实测）

### 2.1 `docs/` → `.agents/` 跨区引用：675 处匹配 / 227 个文件

| 目标前缀 | 处数 | 定性 | 处置批次 |
|----------|------|------|----------|
| `.agents/docs/`（含 retrospective 镜像） | 404 | 文档双体系负债，冻结+分批改写 | B1/B2 |
| `.agents/scripts/` | 154 | 规范执行层引用，合法保留 | B3 |
| `.agents/templates/` | 19 | 规范执行层引用，合法保留 | B3 |
| `.agents/commands/` | 15 | 规范执行层引用，合法保留 | B3 |
| `.agents/skills/` | 14 | 规范执行层引用，合法保留 | B3 |
| `.agents/README*` | 14 | 规范容器入口引用，逐处复核 | B2 |
| `.agents/rules/` | 11 | 规范执行层引用，合法保留 | B3 |
| `.agents/capability-*` | 9 | 规范执行层引用，合法保留 | B3 |
| `.agents/protocols/` | 4 | 规范执行层引用，合法保留 | B3 |
| `.agents/capabilities/` | 2 | 规范执行层引用，合法保留 | B3 |
| `.agents/roles/` | 2 | 规范执行层引用，合法保留 | B3 |
| `.agents/modules/` | 2 | 规范执行层引用，合法保留 | B3 |
| `.agents/VENDOR-INTEGRATION.md` | 2 | 规范文档引用，合法保留 | B3 |
| 其他（tools/global-core/context-routing/config/cases/ONBOARDING/workflows 各 1） | 7 | 规范执行层引用，合法保留 | B3 |
| 文本噪声（非链接语境匹配） | ≈10 | 复核后排除 | — |

### 2.2 `.agents/docs/` → `docs/` 反向引用：164 处 / 82 个文件

按 R4 规则分批校正为 `../docs/...` 实际路径（B4 批次）。

### 2.3 双份目录

| 目录 | docs/ 侧 | .agents/docs/ 侧 | 裁定 |
|------|----------|------------------|------|
| retrospective | OKF v0.2 新体系（patterns/reports/log，门禁全覆盖） | 旧体系（archives/assets/concepts/frameworks/guides/patterns + 根级日期复盘） | 以 `docs/retrospective/` 为准；旧侧冻结新增 |
| 资产清单 | 无（待迁移） | `.agents/docs/retrospective/assets/asset-inventory.md` 存在 | B5：评估迁移，迁移前根 AGENTS.md 链接保留旧侧目标并标注"待迁移" |

## 三、分批台账

| 批次 | 范围 | 策略 | 优先级 | 状态 |
|------|------|------|--------|------|
| B1 | `docs/` → `.agents/docs/retrospective/` 镜像引用（404 处中主体） | 按 `docs/retrospective/` 新体系逐类改指；新体系无对应目标的登记 backlog，不凭空创建 | P1 | 未启动 |
| B2 | `docs/` → `.agents/docs/` 其余文档引用（guides/standards/patterns 等，含 README 14 处） | 逐类评估：对外读者需要的内容迁入 `docs/`；纯智能体规范引用改述为文字说明或删除 | P2 | 未启动 |
| B3 | `docs/` → `.agents/scripts\|skills\|commands\|rules\|templates` 等执行层引用（约 240 处） | 体系间合法导航，不改写；纳入链接有效性检查，断链即修 | P2 | 未启动 |
| B4 | `.agents/docs/` → `docs/` 反向引用 164 处 | 按 R4 校正为 `../docs/...` 实际路径；目标不存在的登记 | P2 | 未启动 |
| B5 | `.agents/docs/retrospective/` 历史归档处置 | 冻结新增；assets 等待迁移项逐批评估迁移至 `docs/retrospective/` | P3 | 未启动 |

> 每批启动时：先按复验命令生成本批明细清单 → 修复 → 重跑三道门禁（check-toctrees/check-frontmatter/check-utf8）→ 在 `docs/log.md` 留痕（批次、数量、归零证据）→ 更新本台账状态。

## 四、复验方法（可复现）

```powershell
# 1. docs/ → .agents/ 跨区引用存量统计（B1/B2/B3 进度度量）
cd d:\AI\docs
$files = Get-ChildItem -Recurse -Filter *.md -File | Where-Object { $_.FullName -notmatch '\\_build\\' }
$cross = foreach ($f in $files) {
  $text = Get-Content $f.FullName -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
  [regex]::Matches($text, '(\.\./)+(\.agents[\\/]docs[\\/][^\s\)"#]*)') | ForEach-Object { $_.Groups[2].Value }
}
$cross.Count  # R2 冻结口径：仅统计指向 .agents/docs/ 的引用；B1+B2 归零目标

# 2. 反向引用统计（B4 进度度量）
cd d:\AI
(Get-ChildItem .agents\docs -Recurse -Filter *.md -File | ForEach-Object {
  $t = Get-Content $_.FullName -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
  [regex]::Matches($t, '(\.\.[\\/])+(docs[\\/])').Count
} | Measure-Object -Sum).Sum

# 3. 新增冻结校验（R2）：审查 git diff 中 docs/ 下新增/修改文件是否引入新的 .agents/docs/ 链接
git diff --name-only -- docs/ | ForEach-Object { Select-String -Path $_ -Pattern '(\.\./)+\.agents[\\/]docs[\\/]' }
# 期望输出：空（新增跨区引用数=0）

# 4. 三道门禁
cd d:\AI\docs; python scripts/check-toctrees.py; python scripts/check-frontmatter.py; python scripts/check-utf8.py
```

## 五、批次处理记录

| 日期 | 批次 | 处理数量 | 结果 | 留痕 |
|------|------|----------|------|------|
| 2026-08-31 | 台账建立 | — | 声明修订完成（根 AGENTS.md 文档边界条款 + global-core-rules 路径解析规则/敏感度分流/知识库链接共 5 处）；R2 冻结生效；存量基线登记 | docs/log.md |
| 2026-08-31 | 基线附注（ACT-4 遗留） | 5 处 | ACT-4 索引修复中将 5 处断链改指 `.agents/docs/` 归档副本（methodology-patterns 清单表 2 行：plugin-bridge-standard-integration、automation-idempotent-four-elements；3 个根级模式文件 source_report/溯源行：awesome-okf-xs-ci-integration 报告）。冻结前已计入 2.1 基线（404 处内），R2 生效后不再新增；对应内容在 `docs/` 树无副本，B1/B5 批次迁移时优先处置 | 本台账 |
