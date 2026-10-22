---
name: skill-mirror-archive
version: 1.0.0
description: "外部技能镜像归档工作流（Skill Mirror Archive）。当用户提到『把 XX 技能归档到 .agents/skills』、『技能镜像入库』、『平台技能导入』、『镜像归档』、『外部技能导入』、『把技能存进工作区技能库』，或涉及把外部平台/IDE 的技能（如 TeleAgent、Trae IDE）放入 .agents/skills/ 时，必须使用此技能。本技能封装：sovereign-rollout 四阶段治理门（S0 零写入提案→S1 批准门→S2 落盘保真→S3 验证）+ 镜像保真复制（frontmatter source 溯源与隐私泛化）+ 登记面裁剪（镜像不迁 capability-registry、不建 .meta/toml）+ check-links/哈希核验 + 原子提交（不推送）。核心价值：把三次镜像导入（v1.15/v1.16/v1.27）的工程经验固化为可复现流程，解决手抄漂移、source 隐私泄漏、登记面膨胀、check-links 单文件漏检等反直觉陷阱。"
argument-hint: "<技能源路径或技能名>"
user-invocable: true
paths:
  - ".agents/skills/**"
  - ".agents/skills/README.md"
  - ".agents/skills/CHANGELOG.md"
  - ".agents/scripts/check-links.py"
  - ".agents/scripts/check-skill-quality.py"
title: "外部技能镜像归档（Skill Mirror Archive）"
x-toml-ref: "../../../.meta/toml/.agents/skills/skill-mirror-archive/SKILL.toml"
---

# 外部技能镜像归档（Skill Mirror Archive）

> ⚠️ **本技能是完整编排层**：治理门复用 [sovereign-rollout-cmd](../sovereign-rollout-cmd/SKILL.md)（S0 提案→S1 批准→S2 落盘→S3 验证报告），本技能只封装专有技术动作（保真复制/source 溯源/登记面裁剪）。不要绕过本技能直接复制外部技能文件。

## 1. Skill ID

`skill-mirror-archive`（内部ID，对外名称：外部技能镜像归档）

## 2. 功能描述

将外部平台技能（TeleAgent / Trae IDE 等）镜像入库 `.agents/skills/`，供工作区统一发现与版本追溯：

| 环节 | 动作 | 产出 |
|------|------|------|
| S0 事实采集 | 源文件盘点/行数/grep 冲突/索引 git 现状（全部实测） | 事实清单 F-xxx |
| S0 提案 | 五节草案（背景/落盘位置/草案全文/关联资产/待批准清单），零写入 | 提案 |
| S1 批准门 | 用户逐项确认 | 批准记录 |
| S2 落盘保真 | Copy-Item + frontmatter source 溯源 + 登记面裁剪 | 镜像 + 索引更新 |
| S3 验证 | check-links / 哈希 / 敏感信息扫描 | 0 断链 + 证据 |
| C 原子提交 | 三查暂存 + UTF-8 文件 + git commit -F，不推送 | 可追溯提交 |

核心功能：保真复制（不手抄）、source 溯源（隐私泛化）、登记面双轨（镜像/原生）、原子提交闭环。

> **为什么「镜像原貌」是铁律？** 外部技能的价值在其正文；改造/重写会引入漂移并破坏版权溯源。镜像技能与原生技能（按 SKILL-TEMPLATE 五要素）是双轨制，靠 frontmatter `source` 字段区分——本技能专治镜像轨，原生轨另有 skill-creator。

## 3. 何时使用本技能

当用户提到以下内容时触发：
- "把 XX 技能归档到 .agents/skills"、"技能镜像入库"、"平台技能导入"、"镜像归档"、"外部技能入库"
- 任何把工作区之外（TeleAgent 用户目录 / Trae IDE builtin / 其他平台）的技能放入 `.agents/skills/` 的请求

不适用（换轨路由）：
- 技能已在工作区，仅换存放位置 → 迁移模式 [skill-migration-position-governance](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/skill-migration-position-governance.md)
- 从零原创技能 → [skill-creator](../../../vendor/flexloop/apps/chaos/.agents/skills/skill-creator/SKILL.md) + [SKILL-TEMPLATE.md](../SKILL-TEMPLATE.md)
- 仓内技能优化/调试 → [skill-development](../../rules/skill-development.md)

> **为什么触发要明确边界？** 即使只说了"技能入库"，也先按本技能 S0 事实采集走一遍（零写入），再判定走哪条轨；先事实后决策。

## 4. 方案选择决策树

```
技能入库请求
├─ 外部来源（平台/IDE/他人目录）→ 本技能镜像归档（S0→S3→C）
├─ 已有本地技能，只换位置 → skill-migration-position-governance 迁移
├─ 从零原创 → skill-creator + SKILL-TEMPLATE 五要素
└─ 目标同名冲突 → 停，走 SKILL_MIRROR_001 冲突裁决
```

## 5. 输入参数与依赖

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| 源路径 | string | 是 | - | 外部技能目录/文件绝对路径 |
| 目标名 | string | 否 | 源技能名 | 目标目录名（`.agents/skills/<目标名>`） |
| dry_run | boolean | 否 | false | S0 提案阶段恒为 true（零写入），S1 批准后关 |

依赖：PowerShell（Copy-Item/Get-FileHash）、git、`grep`/`rg`、`python`（check-links.py / check-skill-quality.py）。

> **为什么写操作必须 dry-run？** 主权区落盘进 git 历史不可逆；提案+批准门就是 dry-run 机制，杜绝未经预览的写入。

## 6. 核心步骤（S0→S3→C）

### 6.0 S0 事实采集（零写入）
1. 源盘点：文件清单、行数（`(Get-Content <file>).Count` 实测）
2. 冲突检测：`grep -r <技能名> .agents/skills/`（命中即停）
3. 索引现状：`git status --porcelain -- .agents/skills/README.md .agents/skills/CHANGELOG.md`
4. 先例参照：读同类镜像 frontmatter（如 docx/SKILL.md）与登记行，定格式

> **为什么先查实例再定格式？** 镜像惯例随工作区演进（v1.15→v1.27），以磁盘上的最新同类资产为准，不从记忆/内联副本猜格式。

### 6.1 S0 提案（遵循 sovereign-rollout-cmd）
五节结构：背景 / 落盘位置 / 草案全文（frontmatter 齐全）/ 关联资产 / 待批准事项清单。任何文件写入前必须获得批准。

### 6.2 S1 批准门
用户逐条批准；批准前零写入。

### 6.3 S2 落盘保真（本轨专有）
1. 复制保真：`Copy-Item` 源 → 目标（禁止重打正文）
2. 前置 frontmatter（镜像形制字段）：`name`/`description`（沿用平台描述）/`source`（隐私泛化）
3. 登记面裁剪：镜像 → README/CHANGELOG 两处；原生 → README+注册表+TOML 全量
4. 保真核验：`EndsWith(源正文)` 逐字、references 类 `Get-FileHash` 全等、行数=源行数+frontmatter 块行数
5. 幂等检查：目标已存在且哈希一致 → 报"已归档"并停止（不重复落盘）

> **为什么 source 要隐私泛化？** 源绝对路径含平台用户 ID 等标识，写入 git 历史后公开推送不可逆；溯源的价值在"可识别来源+归档日期+版权声明"，不在"可还原本机路径"。

### 6.4 S3 验证
- `python .agents/scripts/check-links.py --path .agents/skills/<目标名>` → 0 断链
- 新链接目标 `Test-Path` 显式存在（check-links 对单文件按目录漏检，见 Gotchas）
- 原生技能：`python .agents/scripts/check-skill-quality.py <name>` 记录质量分

### 6.5 C 原子提交
- 三查暂存：`git add` 只含目标路径；`git diff --cached --name-status` 确认；绝不 `git add -A`
- UTF-8 临时文件 + `git commit -F`（防 PowerShell 中文乱码）；Conventional Commits 中文主体
- **不推送远端**（除非用户明确要求，先裁决版权边界）

> **为什么必须原子提交？** 镜像入库是工作区资产的版本化入口；分开提交才能独立回滚/追查，混入他人变更会阻塞回滚。

## 7. 安全检查清单

- [ ] S0 四项实测（源文件/行数/冲突/索引）完成
- [ ] 幂等检查：目标已存在且哈希一致时跳过并提示，不重复落盘
- [ ] 批准门已过（批准清单与执行一一对应）
- [ ] 正文全程 Copy-Item，无手抄
- [ ] source 无绝对路径/用户 ID；版权/自托管声明齐
- [ ] 登记面按镜像或原生惯例，不越界（capability-registry/TOML 只对原生）
- [ ] check-links 0 断链 + 新链接 Test-Path 通过
- [ ] 暂存三查只含目标文件
- [ ] 提交信息 UTF-8 无乱码，未推送

## 8. 常见错误

| 错误码 | 场景 | 处理 |
|--------|------|------|
| SKILL_MIRROR_001 | 同名冲突 | 停；报用户裁决（覆盖/改名/放弃），不静默覆盖 |
| SKILL_MIRROR_002 | source 含绝对路径/平台用户 ID | 泛化改写后重扫（敏感信息检测） |
| SKILL_MIRROR_003 | check-links 单文件漏检（exit 0 但 0 文件） | Test-Path 显式核验新增链接目标 |
| SKILL_MIRROR_004 | pre-commit 敏感信息扫描命中 | 定位、改写、重跑后继续 |
| SKILL_MIRROR_005 | 未经批准被要求写入 | 拒绝并回退 S0（治理门不跳过） |

## 9. Gotchas（陷阱与反直觉）

1. **手抄漂移**：手写正文必引入换行/全半角差异；Copy-Item + 哈希核验是唯一可靠手段。
2. **check-links 单文件假通过**：`--path` 传单文件按目录解析，扫 0 文件也报"通过"；新增链接必须 Test-Path。
3. **source 隐私固化**：用户级路径/ID 进 git 历史即永久化（推送公开不可逆）。
4. **登记面膨胀**：镜像技能误登 capability-registry / 建 TOML 会造成治理资产被外部快照淹没。
5. **git add -A 混入**：工作区常有他人变更，一律按路径精确 add。
6. **PowerShell 中文提交乱码**：`git commit -m 中文` 乱码；UTF-8 文件 + `-F` 解决。

> **为什么 Gotchas 高于步骤？** 步骤可从模板复制，真正决定成败的是这些"不报错但坏结果"的隐性陷阱。

## 10. 关键参考

| 参考 | 路径 | 用途 |
|------|------|------|
| 治理门 | [sovereign-rollout-cmd](../sovereign-rollout-cmd/SKILL.md) | S0-S4 提案/批准/落盘/报告 |
| 方法论编排 | [seven-concepts-cmd](../seven-concepts-cmd/SKILL.md) | R→I→E→V→C 沉淀链路 |
| 原创技能 | [SKILL-TEMPLATE.md](../SKILL-TEMPLATE.md) | 原生技能五要素规范 |
| 迁移模式 | [skill-migration-position-governance](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/skill-migration-position-governance.md) | 仓内技能迁移 |
| 链接校验 | [check-links.py](../../scripts/check-links.py) | S3 断链验证 |
| 质量门 | [check-skill-quality.py](../../scripts/check-skill-quality.py) | 原生技能质量分 |
| 首例 | [CHANGELOG.md](../CHANGELOG.md) v1.27 | 完整归档案例参考 |

## 11. 成熟度与演进

- **成熟度 L1**（v1.0.0）：完整链路以 v1.27 TeleAgent 平台技能镜像单案例验证；镜像惯例有 v1.15/v1.16/v1.27 三次导入佐证
- **升 L2 条件**：第二次独立来源家族镜像归档成功并回填本节
- **演进方向**：批量镜像（同源多技能）、镜像版本对比、自动保真校验脚本

## 12. Changelog

- **v1.0.0** (2026-10-21): 初始版本。萃取 sc-20261021-teleagent-skill-archive 全链路（TeleAgent 平台技能镜像，commit 0b0e4d4bf）：sovereign-rollout 四阶段映射、Copy 保真、source 隐私泛化、登记面双轨裁剪、check-links 单文件漏检兜底、5 错误码 + 6 Gotchas，成熟度 L1。