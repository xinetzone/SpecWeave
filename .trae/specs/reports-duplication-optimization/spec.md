# 复盘报告体系重复内容优化 Spec

## Why

`docs/retrospective/reports/` 文件夹存在大量结构化重复：

1. **frontmatter source 重复引用**：每个子模块文档的 frontmatter 都包含相同的 `source` 字段，引用对应的汇总 `.md` 文件
2. **文档末尾关联模块引用重复**：每个子模块文档末尾都有相同的关联模块引用块
3. **README.md 结构重复**：每个子文件夹的 README.md 都有相同的"子模块导航"表格和"关联报告"结构
4. **汇总文件与子模块内容重复**：汇总 `.md` 文件包含了所有子模块的完整内容副本

这种重复降低了文档的信息密度，增加了维护成本。

## What Changes

### 重复内容识别

| 重复类型 | 出现位置 | 重复程度 |
|---------|---------|---------|
| frontmatter source 引用 | 所有子模块文档 | 高（全文件级重复） |
| 关联模块引用块 | 所有子模块文档末尾 | 高（全文件级重复） |
| README.md 导航结构 | 所有 README.md | 中（结构相同） |
| 汇总文件内容副本 | 汇总 .md 文件 | 高（完全重复） |

### 优化方案

1. **移除文档末尾关联模块引用块**：各子模块通过 frontmatter 的 source 字段建立溯源，文档末尾不再需要重复的关联引用
2. **统一 README.md 结构**：保留核心导航功能，移除冗余的关联报告部分（关联报告应通过导航表跳转，而非重复列出）
3. **精简汇总文件**：汇总文件保留结构化索引功能，内容引用子模块而非复制

## Impact

- 受影响文档：所有 `docs/retrospective/reports/` 下的子文件夹
- 预期效果：提升文档信息密度，降低维护成本，消除冗余引用

## ADDED Requirements

### Requirement: 移除文档末尾关联模块引用块

所有 `docs/retrospective/reports/` 下的子模块文档（`export-suggestions.md`、`insight-extraction.md`、`project-overview.md`、`execution-retrospective.md`），应移除文档末尾的关联模块引用块：

```
> **关联模块**：[project-overview.md](project-overview.md)、[execution-retrospective.md](execution-retrospective.md)、[insight-extraction.md](insight-extraction.md)、[export-suggestions.md](export-suggestions.md)
```

frontmatter 中的 `source` 字段已建立溯源关系，无需在正文末尾重复引用。

#### Scenario: 子模块文档优化
- **WHEN** 子模块文档包含末尾关联模块引用块
- **THEN** 移除该引用块，保留 frontmatter source 字段

### Requirement: 精简 README.md 结构

所有 `docs/retrospective/reports/` 下的 README.md，应保留"子模块导航"表格，移除或精简"关联报告"部分。

#### Scenario: README.md 优化
- **WHEN** README.md 包含"关联报告"部分
- **THEN** 评估关联报告的必要性：若该报告已通过其他导航途径可访问，则移除该部分

## MODIFIED Requirements

### Requirement: frontmatter source 字段标准化

保留 frontmatter 的 `source` 字段，作为唯一的溯源机制。source 字段格式：
```
source = "docs/retrospective/reports/{汇总文件名}.md"
```

