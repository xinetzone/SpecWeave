---
id: "templates-task-retrospective-template-readme"
title: "任务复盘报告模板使用说明"
source: "retrospective-report-standardization-20260708"
x-toml-ref: "../../../.meta/toml/.agents/templates/task-retrospective-template/README.toml"
---
# 任务复盘报告模板（三文件精简架构）

> **来源**：基于 [retrospective-report-standardization-20260708](../../../docs/retrospective/reports/task-reports/retrospective-report-standardization-20260708/README.md) 复盘报告结构沉淀
> **v1.0**：2026-07-10 首次发布

---

## 设计原则：三文件精简架构

本模板适用于**单任务/单日复盘**，用 3 个文件覆盖"入口导航→完整报告→洞察萃取"全流程，比综合复盘模板（7文件）更轻量：

| 文件 | 职责 | 行数上限 |
|------|------|---------|
| `README.md` | 入口导航：文件索引 + 基本信息 + 核心数据 + 关键洞察摘要 | <80行 |
| `retrospective-report.md` | 完整报告：执行摘要 + 事实还原 + 过程分析 + 行动项 + 经验总结 | ~200行 |
| `insight-extraction.md` | 洞察萃取：核心洞察 + 与现有模式关系 + 经验教训 | ~150行 |

---

## 与其他复盘模板的关系

| 模板 | 适用场景 | 文件数 | 对比 |
|------|---------|--------|------|
| **本模板（任务复盘）** | 单任务/单日复盘，有洞察和行动项 | 3 | 精简三文件，复制即用 |
| [comprehensive-retrospective-template](../comprehensive-retrospective-template/README.md) | 全生命周期/里程碑复盘，含行动项闭环 | 7核心+2可选 | 多文件SSOT架构，适合周期≥1周的项目 |
| [insight-extraction-template.md](../insight-extraction-template.md) | 快速洞察萃取，无完整报告需求 | 1 | 单文件三段式，只覆盖洞察部分 |

### 选择决策树

```
复盘任务规模？
├─ 周期≥1周、提交≥50次、多角色 → comprehensive-retrospective-template
├─ 单任务/单日、有洞察和行动项 → 本模板（task-retrospective-template）⭐
└─ 只需萃取洞察，无需完整报告 → insight-extraction-template.md
```

---

## 使用步骤

### Step 1：复制模板

```bash
# 创建复盘目录
mkdir -p docs/retrospective/reports/<task-reports|project-governance|...>/retrospective-<topic>-<YYYYMMDD>/

# 复制模板目录下所有文件到复盘目录
cp -r .agents/templates/task-retrospective-template/template/* \
      docs/retrospective/reports/<category>/retrospective-<topic>-<YYYYMMDD>/
```

### Step 2：替换占位符

所有 `{{占位符}}` 需要替换为实际内容：

| 占位符 | 说明 | 示例 |
|--------|------|------|
| `{{topic}}` | 复盘主题（kebab-case） | `frontmatter-standardization` |
| `{{YYYYMMDD}}` / `{{YYYY-MM-DD}}` | 日期 | `20260710` / `2026-07-10` |
| `{{复盘主题}}` | 中文标题 | `Frontmatter 标准化复盘` |
| `{{任务来源}}` | 触发任务 | `task:frontmatter-batch-repair` |
| `{{N}}` | 序号/数量 | `3` |

### Step 3：填写 frontmatter

遵循 [frontmatter 规范模板6（复盘报告）](../../rules/frontmatter-metadata-standard/04-templates-errors.md)：

**YAML（文件内，最小化）**：`id` / `source` / `x-toml-ref`

**TOML（外部文件）**：`title` / `category` / `date` / `status` / `tags` / `session_id` / `related_insights`

> 三文件 id 必须唯一，加后缀区分：`-readme` / `-report` / `-insights`

### Step 4：按需裁剪

- 无洞察萃取需求时，省略 `insight-extraction.md`，在 README 中删除对应索引行
- 行动项较少时，可在 `retrospective-report.md` 的"洞察与建议"章节内联，不单独拆文件
- 时间线超过 15 个节点时，考虑改用 [comprehensive-retrospective-template](../comprehensive-retrospective-template/README.md)

### Step 5：验证

```bash
# 链接检查
python .agents/scripts/check-links.py --path <复盘报告目录>

# frontmatter 检查（参照模板6检查清单）
# 确认三文件 id 唯一、x-toml-ref 路径正确、TOML 文件存在
```

---

## 文件间引用规范

```
README.md（入口）
  ├──→ retrospective-report.md（完整报告）
  │     └──→ insight-extraction.md（洞察，SSOT）
  └──→ insight-extraction.md（洞察，SSOT）
```

**引用方向规则**：
- README 引用其他两个文件，但不重复其内容
- retrospective-report.md 的"洞察与建议"章节引用 insight-extraction.md，不重复洞察详情
- insight-extraction.md 不引用 retrospective-report.md（避免循环引用）

---

## 版本历史

- v1.0 (2026-07-10)：基于 retrospective-report-standardization-20260708 复盘报告结构沉淀，三文件精简架构
