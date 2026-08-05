# Agency Agents（The Agency）库系统学习与 Wiki 教程 Spec

## Why

`d:\AI\.chaos\libs\agency-agents` 是开源项目 **The Agency**（GitHub: `msitarzewski/agency-agents`），一个包含 **230+ 个 AI Agent 角色定义**、按 16+ 部门组织的 Markdown 资产库，配套安装/转换脚本、多工具集成与策略运行手册。当前项目内缺少对该库**本地文件夹本身**的系统性学习成果（既有 spec `agency-project-learning-wiki` 基于微信公众号文章，`agency-deep-learning-analysis` 仅聚焦深度学习原子化设计），多为零散引用。

本任务对该文件夹进行系统性学习（组织结构、Agent 文件格式、功能模块、脚本体系、集成方式、使用方法），沉淀一份**通俗易懂、结构清晰、适合不同技术水平开发者**的中文 Wiki 教程，纳入知识库成为长期参考。

## What Changes

- 系统研读 `agency-agents` 文件夹：顶层文件、部门目录、`scripts/`、`integrations/`、`strategy/`、`.github/workflows/`、`examples/` 等
- 在 `docs/knowledge/learning/03-agent-platforms-tools/agency-agents-wiki/` 下创建 **11 个原子化章节**（00-overview 至 10-summary-resources）
- 每个章节遵循 `open-code-review-wiki` 的格式惯例：YAML frontmatter（id/title/source/date/category/tags）、层次化标题、表格、Mermaid 图、章节导航
- 覆盖：整体架构、Agent 文件格式解析、部门名册、脚本体系、多工具集成、使用示例、策略运行手册、FAQ、最佳实践、总结与资源
- 更新知识库父目录索引（`docs/knowledge/learning/README.md` 或对应分类 README），实现交叉引用与导航闭环

## Impact

- **Affected docs**：新增 `docs/knowledge/learning/03-agent-platforms-tools/agency-agents-wiki/`（11 个文件）
- **Affected index**：`docs/knowledge/learning/` 分类 README 导航更新
- **Affected specs**：`retrospectives-insights/agency-agents-library-wiki`（本 Spec）
- **约束**：不修改 `agency-agents` 源库（vendor 只读）；不引入新依赖；遵循 kebab-case 文件名、YAML frontmatter、相对路径链接规范

## ADDED Requirements

### Requirement: 系统研读源文件夹
系统 SHALL 深入研读 `d:\AI\.chaos\libs\agency-agents` 的组织结构、Agent 文件格式、脚本体系与集成方式，采集客观事实作为 Wiki 内容基础。

#### Scenario: 事实采集
- **WHEN** 研读完成
- **THEN** 能准确说明部门划分、Agent 文件结构、install/convert 脚本用法、集成工具清单

### Requirement: 创建原子化 Wiki 章节
系统 SHALL 在目标目录创建 11 个原子化章节，覆盖整体架构、Agent 格式、部门名册、脚本、集成、使用示例、策略、FAQ、最佳实践、总结资源。

#### Scenario: 章节完整
- **WHEN** 全部章节创建完成
- **THEN** 每个章节含 YAML frontmatter、层次化内容、表格/Mermaid 图、章节间导航

### Requirement: 索引与导航闭环
系统 SHALL 更新知识库父目录索引，确保 Wiki 从父 README 可发现，章节间链接无断链。

#### Scenario: 链接有效
- **WHEN** 索引更新完成
- **THEN** 所有内部相对链接指向真实存在的目标文件，父 README 可导航到 Wiki

### Requirement: 质量校验
系统 SHALL 通过链接检查、文件名规范校验、frontmatter 一致性核验。

#### Scenario: 校验通过
- **WHEN** 全部写作完成
- **THEN** 章节总数、frontmatter 字段、文件名 kebab-case、内部链接有效性均符合项目规范

## MODIFIED Requirements

无（全新任务，不修改既有 spec）。

## REMOVED Requirements

无。

## Notes

- 内容级别：**公开内容**（开源项目本地副本），标准工作流，产出物存放于 `docs/knowledge/learning/`。
- 参考格式样本：`docs/knowledge/learning/03-agent-platforms-tools/open-code-review-wiki/`（最近更新的原子化子目录结构最完整）。
- 语言：本 Wiki 面向中文读者，全中文撰写。