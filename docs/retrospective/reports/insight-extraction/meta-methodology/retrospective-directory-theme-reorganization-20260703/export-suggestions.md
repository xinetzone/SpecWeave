---
id: "retrospective-directory-theme-reorganization-20260703-export"
title: "导出建议"
source: "session: directory-theme-reorganization-20260703"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/insight-extraction/meta-methodology/retrospective-directory-theme-reorganization-20260703/export-suggestions.toml"
---
# 导出建议

## 一、可沉淀为 patterns 的模式

### 1. 方法论模式：目录重组工作流（高优先级）

**模式名称**：directory-reorganization-workflow

**核心内容**：大规模目录重组的标准五步工作流：

1. **Pre-Pull 检查点**：`git fetch && git status`，确保工作区干净且与远程同步
2. **预扫描**：`grep -r "旧路径前缀"` 全局搜索所有引用点，列出受影响文件清单
3. **移动**：使用 `git mv` 批量移动文件（保持 git 历史追踪）
4. **路径更新**：按层处理——(a) 被移动文件内部的 x-toml-ref/相对链接 (b) 外部文件对被移动文件的引用 (c) 索引文档和 README
5. **验证**：grep 确认无残留旧路径 + 原子提交

**适用场景**：任何涉及 10+ 文件的目录结构重组、重命名、迁移操作。

**推荐沉淀位置**：`docs/retrospective/patterns/methodology-patterns/document-architecture/`

### 2. 方法论模式：Rename-Update 冲突解决（中优先级）

**模式名称**：rename-update-conflict-resolution

**核心内容**：当本地执行了 `git mv`（文件位置变更）而远程有内容更新时，冲突解决三步骤：
1. "由我们添加"的新文件 → 直接 `git add`（本地版本正确）
2. "双方修改"的文件 → `git checkout --theirs <新路径>` + `git add`（位置用 ours，内容用 theirs）
3. 手动合并文件 → 逐冲突块判断，保留新路径 + 最新内容描述

**推荐沉淀位置**：`docs/retrospective/patterns/methodology-patterns/governance-strategy/`

### 3. 方法论模式：4±1 主题分组阈值（中优先级）

**模式名称**：theme-grouping-4plus1-threshold

**核心内容**：当同目录条目超过 15 个时，按主题分为 3-6 个子目录（最佳 4-5 个），每个子目录 3-12 个条目。子目录名使用 kebab-case 语义化命名，不创建多级嵌套。

**推荐沉淀位置**：`docs/retrospective/patterns/methodology-patterns/document-architecture/`

## 二、需要更新的现有文档/配置

### 短期（本次会话内完成）

| 更新项 | 路径 | 动作 |
|-------|------|------|
| 新增复盘四件套 | `docs/retrospective/reports/insight-extraction/meta-methodology/retrospective-directory-theme-reorganization-20260703/` | 已创建（本文件及 execution-retrospective.md、insight-extraction.md、README.md） |
| reports/README.md 索引 | `docs/retrospective/reports/README.md` | 添加新复盘条目到 meta-methodology 表格和日期查找表 |
| retrospective/README.md 目录树 | `docs/retrospective/README.md` | 更新报告计数（30→31） |

### 中期（后续会话执行）

| 更新项 | 路径 | 动作 |
|-------|------|------|
| 沉淀目录重组工作流模式 | `docs/retrospective/patterns/methodology-patterns/document-architecture/` | 新增 directory-reorganization-workflow.md |
| 沉淀冲突解决模式 | `docs/retrospective/patterns/methodology-patterns/governance-strategy/` | 新增 rename-update-conflict-resolution.md |
| 更新原子提交命令文档 | `.agents/commands/atomic-commit.md` | 如有目录重组相关的注意事项，补充说明 |

## 三、可迁移到通用规范的建议

### 建议 1：在 .agents/commands/ 中添加"目录重组"命令模板

**内容**：类似 `retro`、`insight` 命令，定义目录重组任务的标准流程，包含 pre-pull 检查、路径扫描、移动、验证等步骤。

**价值**：下次遇到目录重组任务时，可以直接调用命令模板，避免遗漏步骤（如忘记先 pull、漏掉外部引用等）。

**优先级**：中

### 建议 2：THEME-CLASSIFICATION.md 作为目录级索引的标准实践

**内容**：每次对目录进行主题划分时，在目录根位置创建一个 THEME-CLASSIFICATION.md（或 CLASSIFICATION.md），记录分类方案、归类依据和文件清单。

**价值**：
- 为后续新增报告提供明确的归属指引
- 分类决策可追溯，避免后续重新分类时的争议
- 新成员可以通过阅读分类文档快速理解目录组织逻辑

**优先级**：高

## 四、暂不实施的建议

### 建议：为每个主题子目录创建独立的 README.md

**原因**：当前 4 个子目录每个包含 3-12 个报告，reports/README.md 中的分节表格已经提供了足够的导航信息。每个子目录再创建 README 会增加维护负担（新增报告需要更新两个索引），且当前报告数量尚未达到需要二级索引的阈值（建议阈值：单目录 >20 份报告）。

**触发条件**：当任一子目录内报告超过 20 份，或子目录内出现需要进一步分组的情况时，再考虑创建子目录 README。

## 五、独立洞察卡片

本次任务未产出需要单独提炼为 standalone 卡片的跨项目通用洞察（所有洞察均与"目录重组"这一特定操作类型紧密相关），模式沉淀至 patterns/ 即可。
