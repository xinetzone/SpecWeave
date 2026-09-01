---
type: Reference
title: "双体系引用收敛台账（ACT-5）"
date: "2026-08-31"
status: completed
completed: "2026-09-01"
source: "docs/retrospective/reports/concepts/milestone/docs-full-retrospective-20260831.md 第六章 ACT-5"
---

# 双体系引用收敛台账（ACT-5）

> 本台账登记 `docs/`（OKF v0.2 文档中心）与 `.agents/docs/`（智能体执行配套文档）双体系之间的存量跨区引用，执行"冻结新增、存量分批、声明对齐"治理策略。
>
> 决策记录：2026-08-31 经用户确认——①方向：冻结 + 台账 + 声明修订；②复盘目录归属：以 `docs/retrospective/` 为准，`.agents/docs/retrospective/` 为历史归档、冻结新增。
>
> **结项公告（2026-09-01）**：本台账随 `.agents/docs/` 整体迁入 `docs/` 文档中心而自然结项——2657 个文件经 git rename 迁入 `docs/` 对应板块、41 个与 docs 原生落地页重复的文件删除，git 追踪的 `.agents/docs/` 文件数为 0；B1-B5 批次全部消解/完成，**迁移引入断链 = 0**。下文规则、基线、批次与复验方法作为治理历史保留，结项状态见各章标注；迁移全过程档案见 `.trae/specs/agents-docs-migration/`（spec.md / tasks.md / mapping.md）。

## 一、边界规则（2026-08-31 生效）

| 规则 | 内容 | 落位 | 结项状态（2026-09-01） |
|------|------|------|------------------------|
| R1 | 新增对外可读文档（Wiki/知识包/报告/教程）一律入根 `docs/` | 根 AGENTS.md 文档边界条款 | ✅ 继续有效：单文档中心确立即为本条的完全实现 |
| R2 | `docs/` 内文档**不得新增**指向 `.agents/docs/` 的跨区引用（冻结） | 根 AGENTS.md + global-core-rules 路径解析规则 | ⛔ 使命终结：冻结对象 `.agents/docs/` 已随迁移消亡（git 追踪文件数=0），引用该路径即成断链，由 check-links 门禁硬性拦截 |
| R3 | 复盘报告与模式库以 `docs/retrospective/` 为准；`.agents/docs/retrospective/` 冻结新增，仅作历史归档 | 根 AGENTS.md + global-core-rules | ⛔ 使命终结：旧侧归档已整体迁入 `docs/retrospective/`（archives/assets/concepts/frameworks/guides/patterns 各板块），双份目录不复存在 |
| R4 | `.agents/` 规范内引用根 `docs/` 知识源时使用 `../docs/...` 相对路径；引用 `.agents/docs/` 时使用 `docs/...` | global-core-rules 路径解析规则 | 🟡 部分保留：前半句（`.agents/` 规范引用 `docs/` 用 `../docs/...`）继续有效；后半句随 `.agents/docs/` 实体消亡失效 |
| R5 | 路径引用一律以文件实际位置为准，禁止沿用"docs/ 自动解析为 .agents/docs/"的历史隐式规则 | global-core-rules 路径解析规则 | ✅ 继续有效：迁移后全部引用已按文件实际位置重写，历史隐式规则彻底作废 |
| R6 | `docs/` 指向 `.agents/scripts|skills|commands|rules|templates` 等规范执行层的引用为体系间合法导航（脚本/技能唯一实体在 `.agents/`），不改写，但须保证路径有效 | 本台账 B3 批次 | ✅ 继续有效：执行层实体仍在 `.agents/`；迁移后经 check-links 全量校验路径有效（见 B3 结项记录） |

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

### 2.4 基线收口（2026-09-01 结项实测）

- **2.1 节 675 处/227 文件**：指向 `.agents/docs/` 的 404 处随迁移目标整体迁入 `docs/` 而消解，源链接经全仓改写收敛——主改写 593 链接/245 文件、`.agents` 裸顶级目录补漏 19 链接/4 文件、`docs/knowledge` 策展修复 256 本地链接/55 文件（另含 249 文件 frontmatter 的 x-toml-ref 深度校正）；指向 `.agents/scripts|skills|commands|rules|templates` 等执行层的约 240 处按 R6 保留，迁移后经 check-links 全量校验路径有效。
- **2.2 节 164 处/82 文件**：反向引用的源文件已全部迁入 `docs/`（`.agents/docs/` 实体消亡，git 追踪数=0），迁移文件内部链接按新位置重写，反向跨区引用不复存在。
- **2.3 节双份目录**：retrospective 旧侧（archives/assets/concepts/frameworks/guides/patterns + 根级日期复盘）整体迁入 `docs/retrospective/`；asset-inventory 等资产随迁；41 个与 docs 原生落地页重复的文件（README 等）作为重复件删除（git D=41）。
- **收口证据**：迁移后 `docs/knowledge` 复跑 check-links，本地断链 137 条与迁移前既存缺口登记**逐元组相等（0 新增、0 遗漏）**，迁移引入断链 = 0。既存缺口（外部 `file:///d:/spaces/chaos` 引用 56 条、gitignored `.chaos/` 本地引用 15 条、pyinvoke/conda 等内容缺页群、okf 上游仓库结构引用群等）与 1044 条 TOML 元数据镜像既存悬空，统一登记于迁移 spec backlog（`.trae/specs/agents-docs-migration/mapping.md`），均非本次迁移引入。

## 三、分批台账

| 批次 | 范围 | 策略 | 优先级 | 状态 |
|------|------|------|--------|------|
| B1 | `docs/` → `.agents/docs/retrospective/` 镜像引用（404 处中主体） | 按 `docs/retrospective/` 新体系逐类改指；新体系无对应目标的登记 backlog，不凭空创建 | P1 | ✅ 已结项（2026-09-01）：镜像随 2657 文件整体迁移并入 `docs/retrospective/`；引用经主改写与 knowledge 策展修复全部改指新体系，新体系无对应目标的既存缺口登记 backlog |
| B2 | `docs/` → `.agents/docs/` 其余文档引用（guides/standards/patterns 等，含 README 14 处） | 逐类评估：对外读者需要的内容迁入 `docs/`；纯智能体规范引用改述为文字说明或删除 | P2 | ✅ 已结项（2026-09-01）：guides/standards/patterns 等内容随整体迁移进入 `docs/` 对应板块（tech/knowledge/retrospective），引用同步改写；重复落地页 41 个删除 |
| B3 | `docs/` → `.agents/scripts\|skills\|commands\|rules\|templates` 等执行层引用（约 240 处） | 体系间合法导航，不改写；纳入链接有效性检查，断链即修 | P2 | ✅ 已结项（2026-09-01）：按 R6 保留不改写；迁移后 check-links 全量校验路径有效；检查器 EXCLUDED_DIRS 已纳入 `projects/`（与 `vendor/` 同为 git submodule，主仓检查不越界，子模块问题走子项目流程） |
| B4 | `.agents/docs/` → `docs/` 反向引用 164 处 | 按 R4 校正为 `../docs/...` 实际路径；目标不存在的登记 | P2 | ✅ 已结项（2026-09-01）：源文件（82 个）已全部迁入 `docs/`，反向跨区引用随实体消亡；迁移文件内部链接按新位置重写（含 x-toml-ref 元数据引用 1783 行同步校正） |
| B5 | `.agents/docs/retrospective/` 历史归档处置 | 冻结新增；assets 等待迁移项逐批评估迁移至 `docs/retrospective/` | P3 | ✅ 已结项（2026-09-01）：历史归档整体迁入 `docs/retrospective/`（archives/assets/concepts/frameworks/guides/patterns），asset-inventory 随迁；旧侧目录 git 追踪数=0 |

> 每批启动时：先按复验命令生成本批明细清单 → 修复 → 重跑三道门禁（check-toctrees/check-frontmatter/check-utf8）→ 在 `docs/log.md` 留痕（批次、数量、归零证据）→ 更新本台账状态。
>
> **2026-09-01 结项注**：B1-B5 已全部完成/消解，上述分批流程不再触发；本台账转为治理历史记录，后续单文档中心的链接健康由 check-links 门禁常态保障。

## 四、复验方法（可复现）

```powershell
# 结项后终态校验（2026-09-01 起生效；旧版分批度量命令依赖 .agents\docs 目录，已随迁移失效）
cd d:\AI

# 1. 实体消亡校验：git 追踪的 .agents/docs 文件数应为 0
(git ls-files .agents/docs | Measure-Object -Line).Lines  # 期望：0

# 2. 引用残留扫描：追踪文件中引用 .agents/docs/ 路径的位置
#    期望仅历史语境：reports/ 复盘快照、.trae/specs/ 过程档案、本台账历史章节
git grep -n '\.agents[\\/]docs[\\/]' -- '*.md' |
  Select-String -NotMatch '\.trae[\\/]specs|reports[\\/]|cross-reference-ledger'

# 3. 链接有效性回归：迁移引入断链必须为 0
#    （输出中既存缺口的定性与清单见 .trae/specs/agents-docs-migration/mapping.md backlog）
python .agents\scripts\check-links.py --path docs --check-frontmatter-paths
python .agents\scripts\check-links.py --path .agents

# 4. 文档门禁
cd d:\AI\docs; python scripts/check-toctrees.py; python scripts/check-frontmatter.py; python scripts/check-utf8.py
```

## 五、批次处理记录

| 日期 | 批次 | 处理数量 | 结果 | 留痕 |
|------|------|----------|------|------|
| 2026-08-31 | 台账建立 | — | 声明修订完成（根 AGENTS.md 文档边界条款 + global-core-rules 路径解析规则/敏感度分流/知识库链接共 5 处）；R2 冻结生效；存量基线登记 | docs/log.md |
| 2026-08-31 | 基线附注（ACT-4 遗留） | 5 处 | ACT-4 索引修复中将 5 处断链改指 `.agents/docs/` 归档副本（methodology-patterns 清单表 2 行：plugin-bridge-standard-integration、automation-idempotent-four-elements；3 个根级模式文件 source_report/溯源行：awesome-okf-xs-ci-integration 报告）。冻结前已计入 2.1 基线（404 处内），R2 生效后不再新增；对应内容在 `docs/` 树无副本，B1/B5 批次迁移时优先处置 | 本台账 |
| 2026-09-01 | B1-B5 整体结项（`.agents/docs/` → `docs/` 统一迁移） | 2657 文件 rename / 41 重复件删除 / 593+19+256 链接改写 / 249 文件 frontmatter 深度校正 | `.agents/docs/` 整体迁入 `docs/` 文档中心（git 追踪 `.agents/docs/`=0）；B1/B2/B4/B5 随实体迁移自然消解，B3 按 R6 保留并经 check-links 全量校验；迁移引入断链=0（修复后 137 条本地断链与迁移前既存登记逐元组相等，0 新增 0 遗漏）；既存缺口与 1044 条 TOML 镜像悬空登记 spec backlog；R2/R3 使命终结、R1/R5/R6 继续有效、R4 部分保留；台账状态 active→completed | docs/log.md、`.trae/specs/agents-docs-migration/`（spec/tasks/mapping） |
