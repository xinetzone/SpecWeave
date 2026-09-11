---
title: "路径与命名前置约束检查单模板"
id: "path-naming-preflight"
source: "retrospective:retrospective-2026-09-11-pipeline-parable-refactor-lifecycle"
x-toml-ref: "../../.meta/toml/.agents/templates/path-naming-preflight-checklist-template.toml"
type: "checklist-template"
maturity_level: "L1"
created_date: "2026-09-11"
tags: [path-stability, naming, project-bootstrap, preflight, anti-refactor]
trigger_conditions:
  - 新建学习/文档类项目或任务链（扫描书转教程、知识包、Wiki、笔记集）
  - 工作目录落在 .chaos/、.temp/ 等 gitignore 临时区
  - 计划使用中文文件名或含空格/特殊字符的文件名
validation_count: 0
reuse_count: 0
related_patterns:
  - move-fix-verify-loop
  - temp-zone-consolidation
---

# 路径与命名前置约束检查单（Path & Naming Preflight）

> **来源**：从 [pipeline-parable 全生命周期复盘](../../playground/pipeline-parable/retrospective/retrospective-2026-09-11-pipeline-parable-refactor-lifecycle.md) 洞察 I-102 萃取。该项目在主任务链完成后连续经历三轮重构（目录重命名 ×2、文件英文化、跨区迁移），合计修复引用 30+ 处，均属启动期未锚定约束的「事后矫正」——矫正成本与引用数量成正比。本清单在任务启动时一次性拦截三类重构动机，把矫正成本前置为预防成本。

---

## 一、持久区锚定（工作目录判定）

- [ ] **区域属性已用脚本判定**：执行 `python .agents/scripts/check-source-path-stability.py`（或等价工具），确认工作目录不在 `TEMP_SEGMENTS`（`.chaos`/`.temp` 等 gitignore 临时区）——**禁止凭记忆判定**，内联规范副本可能过期，脚本读取的是磁盘与 gitignore 现状
- [ ] **持久区落位正确**：
  - 公开内容 → 根 `docs/` 或 `.trae/specs/<theme-subdir>/`
  - 私域内容 → `playground/<project>/`（内容敏感度预检判定）
- [ ] **溯源链同域共置**：源文件、中间产物、产出物、复盘四类资产规划在同一项目域内，产出物的 frontmatter `source` 字段不指向临时区路径

## 二、命名规范前置（英文 slug 约束）

- [ ] **文件名全部英文 slug**：形如 `01-preface.md`、`04-money-leverage-compound-interest.md`；禁止中文文件名、空格、特殊字符
- [ ] **目录名语义化英文**：不用 `notebook/`、`okf-wiki/` 这类过程性或产物类型名，用项目名或内容域命名（如 `notes/`、`summaries/`、`source/`）
- [ ] **序号前缀统一**：多位文件使用两位数字前缀（`01-`、`02-`），保证字典序 = 阅读序

## 三、frontmatter 溯源字段（启动即建）

- [ ] 每个产出物含 `source` 字段，指向项目内稳定相对路径
- [ ] 索引文件（`index.md` / `README.md`）建立时即登记 frontmatter（`id`/`date`/`type`/`source`）

## 四、豁免与例外

- [ ] 若确需在临时区启动（探索期未定型）：记录豁免理由于任务 frontmatter，并设定「定型检查点」——项目进入沉淀期时执行本清单 + 临时区资产归并模式

## 检验标准（怎么知道做对了）

- 任务启动后不存在「仅因路径/命名问题」触发的重构提交
- frontmatter `source` 字段全量可通过 `check-source-path-stability.py` 校验
- 目录结构在任务链结束时与启动时规划一致（无事后移动/重命名）

## 反模式（对应本清单要拦截的重构动机）

1. **临时区启动不设检查点**：项目落在 `.chaos/` 且 frontmatter 溯源指向临时路径，随时面临临时区清空导致溯源链断裂
2. **中文文件名先上后改**：图快使用中文文件名，引用积累后再做英文化重构，替换成本与引用数成正比
3. **frontmatter 事后补记**：产出物先写正文、迁移后才补 `source` 字段，补记过程中漏改旧路径引用
