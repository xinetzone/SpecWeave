# Jira Skill Wiki 转 OKF 教程 - 产品需求文档

## Overview

- **Summary**: 将现有的 jira-skill 教程 Wiki（10个Markdown文档）转换为符合 OKF v0.2 规范的结构化知识包（Bundle），同时基于源码事实补充信源溯源、示例文档和完整的 frontmatter 元数据。
- **Purpose**: 现有 Wiki 文档虽然内容完整，但缺乏 OKF 规范要求的溯源（sources）、信任（generated/verified）、生命周期（status/stale_after）等元数据字段，且目录结构不符合 Bundle 规范。转换后可被 OKF 兼容的 AI 智能体和工具链直接消费。
- **Target Users**: 学习 jira-skill 插件的开发者、使用 AI 智能体操作 Jira 的工程师、维护 OKF 知识库的文档协作者。

## Goals

- 将现有10个概念文档迁移到 OKF Bundle 的 `concepts/` 目录
- 为所有文档添加符合 OKF v0.2 规范的 YAML frontmatter（type/title/description/tags/generated/verified/status/stale_after/sources）
- 创建 `references/` 信源登记目录，建立源码→文档的可验证溯源链路
- 新增 `examples/` 示例文档目录，提供可运行的实操示例
- 生成符合规范的根 `index.md`（含 okf_version）和各级子目录 `index.md`
- 创建 `log.md` 变更日志
- 所有交叉链接使用 `/` 开头的 bundle-relative 路径
- 通过 V 阶段独立验证：无虚构 API、链接无断裂、frontmatter 完整

## Non-Goals

- 不重写现有文档的核心内容（仅做格式转换和必要的事实校正）
- 不创建 Attested Computation 类型文档（本项目为教程类知识包，无可计算指标）
- 不修改源码目录 `d:\AI\.chaos\libs\tests\jira-skill`
- 不将 Bundle 发布到外部仓库或注册中心
- 不生成 PDF/HTML 等派生产物

## Background & Context

- 现有 Wiki 位于 `d:\AI\.agents\docs\knowledge\learning\01-agent-protocols-interfaces\jira-skill-wiki\`
- 源码位于 `d:\AI\.chaos\libs\tests\jira-skill\`（v3.29.0，git submodule）
- OKF v0.2 规范位于 `d:\AI\projects\awesome-okf-xs\doc\bundles\meta\okf-spec\references\okf-spec.md`
- 转换方法论：source-code-to-okf-wiki 技能的 R→I→E→V→C 五阶段链路
- 现有文档已通过七概念方法论初步生成，内容质量较高，主要差距在 OKF 格式合规性

## Functional Requirements

- **FR-1**: 现有10个文档（00-overview 至 09-glossary）迁移至 `concepts/` 目录，文件名保持不变
- **FR-2**: 每个概念文档必须包含完整的 OKF frontmatter 字段
- **FR-3**: `references/` 目录至少包含3个信源文档：源码结构、API参考、官方文档
- **FR-4**: `examples/` 目录至少包含3个示例文档：基础CLI使用、工作流自动化、语法模板
- **FR-5**: 根 `index.md` 包含 `okf_version: "0.2"` frontmatter 和完整目录导航
- **FR-6**: 所有概念文档的 `sources` 字段指向 `references/` 下已存在的信源文件
- **FR-7**: 所有交叉链接使用 `/` 开头的 bundle-relative 路径
- **FR-8**: `log.md` 记录本次转换的日期和内容
- **FR-9**: 概念文档中引用的所有类名、方法名、脚本名必须在源码中存在（Grep验证）

## Non-Functional Requirements

- **NFR-1**: 所有文档使用中文撰写，英文技术术语首次出现时括号注释
- **NFR-2**: frontmatter 时间戳使用 ISO 8601 UTC 格式
- **NFR-3**: 代码块标注语言，API调用与源码签名一致
- **NFR-4**: 每个概念文档结尾包含"## 相关概念"章节
- **NFR-5**: 文件名使用 kebab-case 纯英文

## Constraints

- **Technical**:
  - 输出目录必须为现有的 `d:\AI\.agents\docs\knowledge\learning\01-agent-protocols-interfaces\jira-skill-wiki\`
  - 不得修改源码目录（vendor 区域只读）
  - 必须遵循 OKF v0.2 规范
  - Windows 平台路径分隔符注意事项
- **Business**:
  - 现有文档内容不得丢失
  - 保持原有的学习路径顺序（00→09）
- **Dependencies**:
  - 源码事实采集已完成（facts.md）
  - OKF v0.2 规范已读取

## Assumptions

- 现有 Wiki 文档内容基本准确，与源码 v3.29.0 一致
- 输出目录中的旧文件（00-09开头的文件和README.md）可以被替换/重组
- 用户希望在现有目录内重组为 OKF 结构，而非创建新目录

## Acceptance Criteria

### AC-1: Bundle 目录结构完整

- **Type**: `rule`
- **Given**: 转换完成后的 jira-skill-wiki 目录
- **When**: 检查目录结构
- **Then**: 必须包含 index.md、log.md、concepts/（含10个文档+index.md）、examples/（含3个文档+index.md）、references/（含3个文档+index.md）
- **Pass Condition**: 所有必需文件和目录均存在
- **Evidence**: LS 目录列表

### AC-2: Frontmatter 合规

- **Type**: `rule`
- **Given**: 所有 .md 概念文档（concepts/ 和 examples/ 下的内容文件）
- **When**: 检查 YAML frontmatter
- **Then**: 必须包含 type、title、description、tags、generated、verified、status、stale_after、sources 字段；子目录 index.md 不含 frontmatter；根 index.md 含 okf_version
- **Pass Condition**: 所有文档通过 frontmatter 检查
- **Evidence**: Grep/Read 验证每个文件

### AC-3: 信源溯源有效

- **Type**: `rule`
- **Given**: 每个概念文档的 sources 字段
- **When**: 解析 sources[].resource 路径
- **Then**: 所有指向 references/ 下的文件必须存在
- **Pass Condition**: 无断裂的信源引用
- **Evidence**: 路径存在性检查

### AC-4: 无虚构 API

- **Type**: `rule`
- **Given**: 文档中出现的所有脚本名、类名、方法名
- **When**: 在源码目录中 Grep 验证
- **Then**: 每个引用的 API 名称必须在源码中存在
- **Pass Condition**: 零虚构 API
- **Evidence**: Grep 搜索结果

### AC-5: 交叉链接无断裂

- **Type**: `rule`
- **Given**: 文档中所有 markdown 链接
- **When**: 检查链接目标
- **Then**: 所有 `/` 开头的 bundle-relative 链接目标文件存在
- **Pass Condition**: 无断裂链接
- **Evidence**: 链接检查脚本/手动验证

### AC-6: 内容完整性

- **Type**: `rubric`
- **Dimension**: 现有文档内容保留度
- **Scale**: 1-5
- **Anchors**: 1 = 大量内容丢失或被错误修改；3 = 核心内容保留但部分细节遗漏；5 = 所有原有内容准确保留，仅格式变化
- **Pass Threshold**: >= 4
- **Evidence**: 对比原文档和转换后文档

### AC-7: 示例质量

- **Type**: `rubric`
- **Dimension**: 示例文档的可操作性和准确性
- **Scale**: 1-5
- **Anchors**: 1 = 示例无法运行或含错误；3 = 示例基本正确但缺少说明；5 = 示例完整可运行，含预期输出和注意事项
- **Pass Threshold**: >= 4
- **Evidence**: 审查 examples/ 下3个文档

## Open Questions

- [ ] 现有 README.md 是否保留（OKF Bundle 根目录使用 index.md 而非 README.md）？
