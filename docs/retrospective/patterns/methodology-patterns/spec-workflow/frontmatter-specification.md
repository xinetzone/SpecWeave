---
id: "frontmatter-specification"
title: "通用PRD Spec YAML Frontmatter元数据规范"
source: "retrospective-analysis"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/spec-workflow/frontmatter-specification.toml"
created_at: "2026-07-09"
completed_at: "2026-07-09"
status: "completed"
theme: "methodology-patterns"
version: "1.0"
archive_location: "docs/retrospective/patterns/methodology-patterns/spec-workflow/"
parent_spec: "universal-prd-template-extraction"
reference_spec: "first-principles-comprehensive-research"
---
# 通用PRD Spec YAML Frontmatter元数据规范

## 概述

本规范定义了通用PRD Spec的YAML frontmatter元数据标准，为所有新项目Spec提供统一的机器可读元数据层，支持自动化索引、检索、状态追踪和生命周期管理。

本规范基于对`first-principles-comprehensive-research`等经过完整生命周期验证的高质量Spec的第一性原理解构分析提炼而成。

---

## 一、必填字段（7个）

所有PRD Spec必须包含以下字段，缺失任何一个都会导致Spec无法被系统识别。

| 字段名 | 含义 | 取值规范 | 填写时机 |
|--------|------|----------|----------|
| **id** | 文档唯一标识符 | kebab-case英文命名，全局唯一，与目录名一致；格式：`[项目主题]-[项目类型]`，如`first-principles-comprehensive-research` | Spec创建时立即填写，一旦确定不可修改 |
| **title** | 项目中文标题 | 简洁明了的中文标题，准确描述项目核心内容；不超过50个汉字 | Spec创建时填写，项目范围重大变更时可更新 |
| **source** | 项目来源 | 字符串，说明项目发起来源；可选值：`用户/spec指令`、`retrospective-analysis`（复盘派生）、`pattern-extraction`（模式萃取）、`maintenance`（维护任务）或自定义来源 | Spec创建时填写 |
| **created_at** | 创建日期 | ISO 8601日期格式：`YYYY-MM-DD`，如`"2026-07-09"`；使用双引号包裹 | Spec创建时自动填写当天日期 |
| **status** | 生命周期状态 | 见下方"状态机定义"章节，仅允许5个合法值：`candidate`、`planning`、`in-progress`、`completed`、`archived` | 随项目进展实时更新 |
| **theme** | 主题分类 | kebab-case英文，对应`.trae/specs/`下的一级目录分类；现有分类：`retrospectives-insights`、`standards-tools`、`docs-restructure`、`core-foundation`、`roles-governance`、`spec-workflow`、`methodology-patterns` | Spec创建时填写，确定归档目录后不可修改 |
| **version** | Spec版本号 | 语义化版本：`MAJOR.MINOR`，如`"1.0"`；初始版本为`"0.1"`（规划中），正式立项为`"1.0"`，重大变更升级主版本号，增量更新升级次版本号 | Spec创建时填`"0.1"`，每次重大更新时递增 |

### 必填字段示例

```yaml
---
id: "my-new-project-research"
title: "我的新项目研究"
source: "用户/spec指令"
created_at: "2026-07-09"
status: "planning"
theme: "retrospectives-insights"
version: "0.1"
---
```

---

## 二、推荐字段（9个）

以下字段为推荐字段，根据项目实际需要选用，不强制要求但强烈建议在对应场景填写。

| 字段名 | 含义 | 取值规范 | 填写时机 |
|--------|------|----------|----------|
| **completed_at** | 完成日期 | ISO 8601日期格式：`YYYY-MM-DD`；项目验收通过时填写 | 项目完成、所有AC通过时填写 |
| **archive_location** | 归档位置 | 相对路径字符串，指明项目产出物最终归档的docs目录位置；如`"docs/knowledge/learning/first-principles/"` | 项目规划阶段确定归档目录时填写，或完成时填写 |
| **last_updated** | 最后更新日期 | ISO 8601日期格式：`YYYY-MM-DD`；每次更新Spec内容时同步更新 | Spec每次修改时更新 |
| **parent_spec** | 父Spec ID | 字符串，引用父项目的id；用于表示Spec之间的派生/子项目关系；如`"universal-prd-template-extraction"` | 派生子项目创建时填写 |
| **child_specs** | 子Spec ID列表 | YAML列表，列出所有从本Spec派生的子项目id；如`["frontmatter-specification", "universal-prd-template"]` | 子项目创建时更新父Spec此字段 |
| **reference_spec** | 参考Spec ID | 字符串，引用作为模板/参考的Spec id | Spec创建时如果参考了其他Spec则填写 |
| **key_commits** | 关键提交记录 | YAML列表，每项格式：`"commit-hash: 提交说明"`；记录项目关键里程碑提交；如`"838b37e7: 知识档案初版完成（12文件）"` | 项目关键里程碑达成时追加记录 |
| **total_files** | 产出文件总数 | 整数，项目最终产出的文件数量；如`12` | 项目完成时统计填写 |
| **patterns_extracted** | 萃取模式数量 | 整数，项目完成后沉淀到模式库的可复用模式数量；如`7` | 项目完成、模式萃取后填写 |

### 推荐字段完整示例

```yaml
---
id: "first-principles-comprehensive-research"
title: "第一性原理全面资料搜集与系统化档案建立"
source: "用户/spec指令"
created_at: "2026-07-09"
completed_at: "2026-07-09"
last_updated: "2026-07-09"
status: "completed"
theme: "retrospectives-insights"
version: "1.1"
archive_location: "docs/knowledge/learning/first-principles/"
total_files: 12
patterns_extracted: 7
key_commits:
  - "838b37e7: 知识档案初版完成（12文件）"
  - "1d7b5ae: Spec引用验证模式沉淀"
---
```

---

## 三、Status生命周期状态机

### 状态定义

| 状态 | 含义 | 允许的前置状态 | 典型停留时长 |
|------|------|----------------|--------------|
| **candidate** | 候选/待评估 | 无（初始状态） | 数小时~数天 |
| **planning** | 规划中 | candidate | 数小时~1天 |
| **in-progress** | 执行中 | planning | 数小时~数周 |
| **completed** | 已完成 | in-progress | 永久（归档前） |
| **archived** | 已归档 | completed | 永久 |

### 状态转换图

```
    +-----------+
    | candidate |  <-- 项目想法产生，创建空Spec
    +-----+-----+
          |
          | 评估通过，开始编写Spec
          v
    +-----------+
    | planning  |  <-- 编写Goals/FR/NFR/AC等内容
    +-----+-----+
          |
          | Spec评审通过，开始执行
          v
    +-------------+
    | in-progress |  <-- 执行任务，更新进度
    +------+------+
           |
           | 所有AC验证通过
           v
    +-----------+
    | completed |  <-- 项目验收完成，产出归档
    +-----+-----+
          |
          | 长期存档，不再活跃
          v
    +----------+
    | archived |
    +----------+
```

### 状态转换规则

1. **candidate → planning**：
   - 触发条件：项目想法经过初步评估，决定投入资源进行详细规划
   - 必填字段已全部填写（version此时为0.1）
   - Spec框架已搭建，开始填充具体章节

2. **planning → in-progress**：
   - 触发条件：Spec所有核心章节完成（Overview/Goals/FR/NFR/AC/Constraints/Assumptions）
   - AC可验证，Goals可衡量，范围边界清晰
   - 经过评审（可自我评审）确认Spec质量达标
   - version升级到1.0（正式版本）

3. **in-progress → completed**：
   - 触发条件：所有Acceptance Criteria验证通过
   - 产出物已归档至archive_location指定位置
   - completed_at字段填写完成日期
   - key_commits记录所有关键里程碑
   - 如有模式沉淀，patterns_extracted已填写

4. **completed → archived**：
   - 触发条件：项目完成后经过一段时间（如1-2周），确认无后续迭代
   - 或项目被明确标记为不再活跃
   - 相关复盘报告已完成

### 回退规则

- **不建议状态回退**：状态应单向向前流转
- **例外情况**：planning状态发现重大方向问题，可回退到candidate重新评估；但in-progress及之后状态不允许回退
- **版本迭代**：如需在completed后进行重大变更，应创建子Spec或新版本（version升级），而非回退状态

---

## 四、格式规范

### 通用要求

1. **格式**：标准YAML格式，使用`---`作为开始和结束标记
2. **缩进**：使用2空格缩进，禁止使用Tab
3. **字符串**：建议所有字符串值使用双引号包裹（特别是日期）
4. **命名**：所有字段名使用kebab-case（小写字母+连字符）
5. **顺序**：字段建议按以下顺序排列：
   - id → title → source → created_at → completed_at → last_updated
   - status → theme → version → archive_location
   - parent_spec → child_specs → reference_spec
   - total_files → patterns_extracted → key_commits
6. **文件位置**：frontmatter必须位于文件最开头，`---`之前不能有任何内容（包括空行）

### 最小合规示例（规划阶段）

```yaml
---
id: "example-project"
title: "示例项目"
source: "用户/spec指令"
created_at: "2026-07-09"
status: "planning"
theme: "retrospectives-insights"
version: "0.1"
---
```

### 完整合规示例（完成阶段）

```yaml
---
id: "frontmatter-specification"
title: "通用PRD Spec YAML Frontmatter元数据规范"
source: "retrospective-analysis"
created_at: "2026-07-09"
completed_at: "2026-07-09"
last_updated: "2026-07-09"
status: "completed"
theme: "methodology-patterns"
version: "1.0"
archive_location: "docs/retrospective/patterns/methodology-patterns/spec-workflow/"
parent_spec: "universal-prd-template-extraction"
reference_spec: "first-principles-comprehensive-research"
key_commits:
  - "abc1234: Frontmatter规范初稿完成"
---
```

---

## 五、填写时机速查表

| 项目阶段 | 需要填写/更新的字段 |
|----------|---------------------|
| **创建空Spec** | id, title, source, created_at, status="candidate", theme, version="0.1" |
| **开始规划** | status → "planning"，填充Spec正文 |
| **开始执行** | status → "in-progress", version → "1.0" |
| **关键里程碑** | key_commits追加记录，last_updated更新 |
| **项目完成** | status → "completed", completed_at填写日期，total_files统计，patterns_extracted填写，last_updated更新 |
| **长期归档** | status → "archived" |
| **派生子项目** | 父Spec的child_specs添加子项目id，子Spec的parent_spec填写父id |

---

## 六、与现有工具链的兼容性

本规范与项目现有工具链完全兼容：

1. **check-spec-format.py**：必填字段检查作为格式检查的一部分
2. **docgen-cmd**：基于id/title/status/theme等字段生成导航表和看板
3. **ci-check-cmd**：frontmatter格式正确性作为CI检查项
4. **check-links.py**：archive_location等路径字段可被链接检查工具验证

---

## 七、字段扩展原则

- 新增字段必须使用kebab-case命名
- 项目特定字段建议加前缀（如`custom-`）避免与通用字段冲突
- 新增通用字段需经过至少3个不同项目验证后才能加入本规范
- 禁止删除或重命名已定义的必填/推荐字段（可标记为deprecated但至少保留一个版本周期）
