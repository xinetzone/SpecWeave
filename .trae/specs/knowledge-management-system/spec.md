# 项目知识管理系统 Spec

## Why
项目当前缺乏系统化的知识沉淀机制。复盘报告（[retrospective-report-agents-spec-system.md](../../../docs/retrospective/reports/spec-system/retrospective-report-agents-spec-system/)）明确指出需要将操作经验、平台兼容性手册等知识资产纳入项目知识库，实现经验的系统化沉淀与检索。每次开发任务中积累的踩坑记录、架构决策、最佳实践等知识散落在对话和临时代码中，需要一套结构化的知识管理系统来统一管理。

## What Changes
- 新增 `docs/knowledge/` 知识库目录，按类别组织知识条目
- 新增知识条目标准模板（YAML frontmatter + Markdown 正文）
- 新增知识库索引（README.md），支持按类别、标签、日期检索
- 新增索引自动生成脚本，扫描目录自动更新 README
- 新增 `.agents/` 体系与知识库的集成（AGENTS.md 增加知识库引用、角色添加知识查阅职责）
- 将现有知识资产（复盘报告、任务总结）迁移纳入知识库索引

## Impact
- Affected specs: 无（全新系统）
- Affected code: 新增 `docs/knowledge/` 目录及子目录；修改 `AGENTS.md` 增加知识库引用；修改 `.agents/roles/` 各角色定义增加知识查阅条款

## ADDED Requirements

### Requirement: 知识库目录结构
系统 SHALL 在 `docs/knowledge/` 下按类别建立知识库目录。

#### Scenario: 知识分类体系
- **WHEN** 开发者需要沉淀知识
- **THEN** 按以下分类选择对应目录存放：
  - `operations/`：操作经验（环境搭建、工具使用、命令速查）
  - `platform/`：平台兼容性（Windows/macOS/Linux 差异、依赖兼容性）
  - `troubleshooting/`：故障排查（常见错误、原因分析、解决方案）
  - `decisions/`：架构决策记录（ADR，记录技术选型背景与权衡）
  - `best-practices/`：最佳实践（编码规范、设计模式、工作流技巧）

#### Scenario: 目录不存在时自动创建
- **WHEN** 新增知识条目时目标分类目录不存在
- **THEN** 系统提示先创建目录，或由索引脚本自动创建缺失目录

### Requirement: 知识条目标准格式
系统 SHALL 为每条知识条目定义统一的 Markdown + YAML frontmatter 格式。

#### Scenario: 知识条目模板
- **WHEN** 创建新知识条目
- **THEN** 使用 `docs/knowledge/template.md` 模板，包含以下 frontmatter 字段：
  - `title`：标题
  - `category`：分类（operations/platform/troubleshooting/decisions/best-practices）
  - `tags`：标签列表
  - `date`：创建日期
  - `status`：状态（draft/reviewed/archived）
  - `author`：作者
  - `summary`：一句话摘要

#### Scenario: 知识条目正文结构
- **WHEN** 编写知识条目正文
- **THEN** 遵循"背景 → 问题/场景 → 解决方案/经验 → 参考"的标准结构

### Requirement: 知识库索引
系统 SHALL 维护 `docs/knowledge/README.md` 作为知识库入口和索引。

#### Scenario: 索引展示
- **WHEN** 开发者浏览知识库
- **THEN** README.md 展示：
  - 知识库总览（总条目数、各类别数量）
  - 按类别分组的条目列表（含标题、摘要、日期、标签、链接）
  - 按标签的关键词索引
  - 最近更新条目列表

#### Scenario: 索引自动更新
- **WHEN** 新增或修改知识条目后
- **THEN** 运行 `docs/knowledge/scripts/generate_index.py` 自动扫描所有条目，生成更新后的 README.md

### Requirement: 索引自动生成脚本
系统 SHALL 提供 Python 脚本自动扫描知识库并生成索引。

#### Scenario: 扫描知识条目
- **WHEN** 运行 `generate_index.py`
- **THEN** 脚本递归扫描 `docs/knowledge/` 下所有 `.md` 文件（排除 template.md 和 README.md），解析 YAML frontmatter，提取元数据

#### Scenario: 生成 README.md
- **WHEN** 扫描完成后
- **THEN** 脚本生成 README.md，包含：
  - 统计摘要（总条目数、各类别数量）
  - 按类别分组的条目列表（表格形式）
  - 按标签聚合的索引
  - 最近更新（按日期倒序 TOP 10）
  - 自动生成时间戳

#### Scenario: 条目缺失元数据时的处理
- **WHEN** 某个知识条目缺少必要 frontmatter 字段
- **THEN** 脚本输出警告但继续处理，缺失字段使用默认值或留空

### Requirement: .agents 体系与知识库集成
系统 SHALL 将知识库整合到智能体规范体系中。

#### Scenario: AGENTS.md 引用知识库
- **WHEN** 智能体启动并读取 AGENTS.md
- **THEN** AGENTS.md 中包含知识库的引用路径（`docs/knowledge/README.md`），引导智能体在相关任务中主动查阅知识库

#### Scenario: 角色知识查阅职责
- **WHEN** 各角色定义中增加知识查阅条款
- **THEN** developer 角色在遇到环境问题时查阅 `troubleshooting/`，architect 在做技术决策时查阅 `decisions/`，reviewer 在审查时参考 `best-practices/`

### Requirement: 现有知识资产纳入
系统 SHALL 将现有知识资产纳入知识库索引体系。

#### Scenario: 复盘报告纳入
- **WHEN** 索引脚本运行
- **THEN** `docs/retrospective/` 下的复盘报告在知识库 README 中作为"相关资源"列出，不强制迁移

#### Scenario: 任务总结纳入
- **WHEN** 索引脚本运行
- **THEN** `docs/task-summaries/` 下的任务总结在知识库 README 中作为"相关资源"列出