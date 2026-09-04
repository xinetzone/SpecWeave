# Jira Skill Wiki 转 OKF 教程 - 实施计划

## Task 1: 创建 Bundle 目录结构

- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 jira-skill-wiki/ 下创建 concepts/、examples/、references/ 子目录
  - 将现有10个文档（00-overview.md 至 09-glossary.md）移入 concepts/ 目录
  - 保留旧 README.md 但标记为废弃（后续由 index.md 替代）
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-1.1: concepts/ 目录存在且包含10个 .md 文件；evidence: LS 目录列表
  - `rule` TR-1.2: examples/ 和 references/ 目录存在；evidence: LS 目录列表

## Task 2: 生成 references/ 信源登记

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 references/source-code.md：登记源码目录结构、核心模块、版本信息
  - 创建 references/api-reference.md：登记所有CLI脚本、子命令、参数
  - 创建 references/official-docs.md：登记官方文档、Jira API参考、Agent Skills标准
  - 创建 references/index.md（无 frontmatter）
- **Acceptance Criteria Addressed**: AC-1, AC-3
- **Test Requirements**:
  - `rule` TR-2.1: references/ 包含3个信源文档 + index.md；evidence: LS
  - `rule` TR-2.2: 每个信源文档有正确的 type: Reference frontmatter；evidence: Read 验证

## Task 3: 转换 concepts/ 文档 frontmatter（批次1：00-03）

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 为 00-overview.md、01-architecture.md、02-installation.md、03-quickstart.md 添加/更新 OKF frontmatter
  - frontmatter 包含：type（Concept）、title、description、tags、generated、verified、status、stale_after、sources
  - sources 指向 references/ 下的对应信源
  - 修正交叉链接为 `/` 开头的 bundle-relative 路径
  - 每个文档结尾添加"## 相关概念"章节（如不存在）
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-5
- **Test Requirements**:
  - `rule` TR-3.1: 4个文件均包含完整必填 frontmatter 字段；evidence: Read 验证
  - `rule` TR-3.2: sources 中引用的文件均存在；evidence: 路径检查
  - `rule` TR-3.3: 交叉链接使用 `/` 开头；evidence: Grep 检查无 `../` 链接

## Task 4: 转换 concepts/ 文档 frontmatter（批次2：04-06）

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 为 04-jira-communication.md、05-jira-syntax.md、06-jql.md 添加/更新 OKF frontmatter
  - 同 Task 3 的要求
  - 重点验证文档中引用的脚本名、子命令名与源码一致
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-4.1: 3个文件均包含完整必填 frontmatter 字段；evidence: Read
  - `rule` TR-4.2: 文档中引用的所有脚本名在源码中存在；evidence: Grep 源码验证
  - `rule` TR-4.3: 交叉链接使用 `/` 开头；evidence: Grep

## Task 5: 转换 concepts/ 文档 frontmatter（批次3：07-09）

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 为 07-best-practices.md、08-troubleshooting.md、09-glossary.md 添加/更新 OKF frontmatter
  - 同 Task 3 的要求
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-5
- **Test Requirements**:
  - `rule` TR-5.1: 3个文件均包含完整必填 frontmatter 字段；evidence: Read
  - `rule` TR-5.2: 交叉链接使用 `/` 开头；evidence: Grep

## Task 6: 创建 examples/ 示例文档

- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 创建 examples/basic-cli-usage.md：搜索、获取、创建、评论等基础CLI命令示例
  - 创建 examples/workflow-automation.md：意图动词（work/qa/act）、多步转换路径、QA聚合等工作流示例
  - 创建 examples/syntax-templates.md：Bug报告模板、特性请求模板的填充和验证示例
  - 创建 examples/index.md（无 frontmatter）
- **Acceptance Criteria Addressed**: AC-1, AC-7
- **Test Requirements**:
  - `rule` TR-6.1: examples/ 包含3个示例文档 + index.md；evidence: LS
  - `rubric` TR-6.2: 示例可操作性；scale 1-5；anchors 1=无法运行/3=基本正确/5=完整含输出和注意事项；threshold >= 4；evidence: 审查示例文档

## Task 7: 生成根 index.md 和 log.md

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 3, Task 4, Task 5, Task 6
- **Description**:
  - 创建根 index.md，含 okf_version: "0.2" frontmatter 和完整目录导航
  - 创建 concepts/index.md（无 frontmatter），列出10个概念文档
  - 创建 log.md，记录2026-08-28的转换工作
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-7.1: 根 index.md 包含 okf_version 字段；evidence: Read
  - `rule` TR-7.2: concepts/index.md 无 frontmatter；evidence: Read 首行
  - `rule` TR-7.3: log.md 包含日期标题和转换记录；evidence: Read

## Task 8: V阶段 - 独立验证与修复

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 结构检查：所有必需文件存在
  - Frontmatter 检查：每个内容文档字段完整
  - 链接检查：所有交叉链接目标存在
  - API真实性检查：Grep 源码验证文档中引用的所有脚本名、类名、方法名
  - 代码示例检查：CLI命令与源码中定义的子命令一致
  - 发现问题逐一修复
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-8.1: 零断裂链接；evidence: 链接检查结果
  - `rule` TR-8.2: 零虚构 API；evidence: Grep 验证报告
  - `rule` TR-8.3: 所有 frontmatter 必填字段完整；evidence: 检查脚本/手动验证
  - `rubric` TR-8.4: 内容完整性；scale 1-5；anchors 1=大量丢失/3=核心保留/5=准确保留；threshold >= 4；evidence: 对比原文档

## Task 9: C阶段 - 模式萃取与沉淀

- **Status**: `pending`
- **Priority**: low
- **Depends On**: Task 8
- **Description**:
  - 回顾本次"批量Markdown文档→OKF Bundle"转换过程
  - 记录遇到的问题和修复方式
  - 更新现有批量转换模式文档（如需要）
- **Acceptance Criteria Addressed**: None（过程改进任务）
- **Test Requirements**:
  - `rule` TR-9.1: 产出经验总结；evidence: 文档或记录
