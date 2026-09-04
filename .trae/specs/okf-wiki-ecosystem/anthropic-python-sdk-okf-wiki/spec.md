# Anthropic 生态 OKF Wiki - Product Requirement Document

## Overview
- **Summary**: 系统化学习 `external/libs/anthropics/` 目录下全部6个Anthropic官方开源项目，按照 OKF v0.2 规范在 `projects/awesome-okf-xs/doc/bundles/ai/anthropic/` 生成结构化中文Wiki。采用分层策略：**anthropic-sdk-python**（Python SDK核心）走完整 source-code-to-okf-wiki 五阶段流程（R→I→E→V），其余5个子项目（claude-code、claude-cookbooks、financial-services、prompt-eng-interactive-tutorial、skills）根据内容性质进行结构化文档整理与索引。
- **Purpose**: 为中文开发者提供Anthropic生态的全景中文文档——从SDK底层架构到Claude Code工具链、从Cookbook示例到提示词工程、从官方Skills库到金融服务垂直方案，所有内容事实可溯源、格式统一、无虚构API。
- **Target Users**: Claude API开发者、Claude Code用户、AI Agent开发者、提示词工程师、使用Anthropic生态的金融/企业开发者。

## 覆盖的6个子项目

| # | 子目录 | 内容性质 | 文档化策略 |
|---|--------|---------|-----------|
| 1 | anthropic-sdk-python | 官方Python SDK（Stainless生成+手动扩展，~2万行核心代码） | **深度源码分析**：完整R→I→E→V五阶段流程 |
| 2 | claude-code | Claude Code终端AI编码工具（Node.js，含plugins体系） | **工具与插件文档**：概念+使用指南+插件索引 |
| 3 | claude-cookbooks | 官方示例集（Jupyter notebooks、Python脚本、模式） | **示例索引+概念提炼**：按能力域分类整理 |
| 4 | financial-services | 金融服务垂直方案（Cowork插件+Managed Agents模板） | **方案索引**：Agent/插件架构说明+清单 |
| 5 | prompt-eng-interactive-tutorial | 提示词工程交互式教程（9章课程） | **教程中文整理**：章节结构化+要点提炼 |
| 6 | skills | 官方Skills库（xlsx/docx/pptx/frontend-design等10+skill） | **Skills索引+重点Skill详解** |

## Goals
- 创建组织级bundle `ai/anthropic/`，包含生态总览index.md和6个子bundle
- **python-sdk**：完成R阶段80+条事实采集→I阶段架构洞察→E阶段分批生成（6 references + 10-11 concepts + 5-6 examples + 各级index）→V阶段Grep级API验证零虚构
- **claude-code**：生成CLI使用概念文档、plugins体系说明、核心插件索引
- **cookbooks**：按能力域（工具调用、多模态、RAG、子Agent、评估等）分类整理示例索引，提炼核心模式概念
- **prompt-engineering**：将9章教程内容结构化为中文概念文档，提炼核心原则
- **official-skills**：生成Skills库总索引，重点详解skill-creator（Skill开发工具）和claude-api（API参考Skill）
- **financial-services**：生成金融Agent架构概念文档+Agent/插件清单索引
- 全部文档通过 `invoke gates.toctrees` 和 `invoke gates.utf8` 质量门
- 更新 `ai/index.md` 添加anthropic组织bundle

## Non-Goals (Out of Scope)
- 不翻译所有Jupyter notebook全文（cookbooks/下notebook众多，做索引和模式提炼）
- 不逐个详解skills/下每个skill的scripts代码（做索引+重点skill详解）
- 不覆盖financial-services/下的partner-built第三方插件
- 不修改任何源码（vendor区域禁止本地修改）
- C阶段模式沉淀不纳入本次任务（后续单独执行）
- 不实际执行API调用（无API Key），代码示例为可运行框架

## Background & Context
- **源码根目录**: `d:\spaces\SpecWeave\external\libs\anthropics\`
- **输出根目录**: `d:\spaces\SpecWeave\projects\awesome-okf-xs\doc\bundles\ai\anthropic\`
- **Bundle结构**:
  ```
  ai/anthropic/                    # 组织级bundle
  ├── index.md                     # 生态总览（okf_version + toctree）
  ├── log.md
  ├── python-sdk/                  # 子bundle 1: Python SDK（深度）
  ├── claude-code/                 # 子bundle 2: Claude Code
  ├── cookbooks/                   # 子bundle 3: Cookbook示例集
  ├── prompt-engineering/          # 子bundle 4: 提示词工程教程
  ├── official-skills/             # 子bundle 5: 官方Skills库
  └── financial-services/          # 子bundle 6: 金融服务方案
  ```
- **方法论**: python-sdk使用 `source-code-to-okf-wiki` 完整五阶段；其他子bundle基于内容分析整理，V阶段做链接和引用验证
- **参考范例**: coze/coze-py（完整SDK Bundle）、deepseek/下的子bundle结构

## Functional Requirements
- **FR-1**: 组织级bundle创建，含生态总览index.md、toctree、各子bundle导航
- **FR-2**: python-sdk子bundle完成R→I→E→V全流程，产出facts.md、insights.md、完整OKF文档
- **FR-3**: claude-code子bundle包含CLI概念文档、插件体系说明、插件索引
- **FR-4**: cookbooks子bundle包含能力域分类索引、核心模式概念文档、精选示例
- **FR-5**: prompt-engineering子bundle包含9章教程的中文结构化概念文档
- **FR-6**: official-skills子bundle包含Skills总索引、SKILL.md格式规范、重点skill（skill-creator/claude-api）详解
- **FR-7**: financial-services子bundle包含Agent架构说明、Agent清单、垂直插件索引
- **FR-8**: 所有子bundle有各自的index.md和log.md
- **FR-9**: 所有文档frontmatter符合OKF v0.2规范
- **FR-10**: 交叉链接使用`/`开头bundle-relative路径，python-sdk内API引用经Grep验证零虚构
- **FR-11**: 更新ai/index.md添加anthropic条目

## Non-Functional Requirements
- **NFR-1**: python-sdk的API引用100%经Grep源码验证存在
- **NFR-2**: 全部文档中文撰写，英文术语首次出现括号注释
- **NFR-3**: 代码块标注语言类型
- **NFR-4**: 通过 `invoke gates.toctrees` 和 `invoke gates.utf8`
- **NFR-5**: 分批生成，每批≤7文档，保证上下文质量
- **NFR-6**: 各子bundle文档结尾有「相关概念」或「相关资源」章节

## Constraints
- **Technical**: OKF v0.2规范、awesome-okf-xs frontmatter规范、Sphinx myst_parser构建
- **Business**: 产出位于projects/awesome-okf-xs/（git submodule），遵循子项目规范
- **Scope**: 6个子项目全覆盖，但深度分层（SDK最深入，其他以索引/概念/指南为主）

## Assumptions
- anthropics下6个子目录内容完整可访问
- prompt-eng-interactive-tutorial即使只有README也按README内容生成结构化文档
- 用户接受分层深度策略（SDK源码分析 vs 其他子项目内容整理）
- 批量文档生成通过general_purpose_task子代理分批委派

## Acceptance Criteria

### AC-1: 组织级bundle完整
- **Given**: 6个子项目内容可访问
- **When**: 组织级bundle创建完成
- **Then**: `ai/anthropic/`存在，index.md含okf_version、Anthropic生态简介、6个子bundle导航、toctree引用所有子bundle；log.md有初始记录
- **Verification**: `programmatic`

### AC-2: python-sdk R阶段事实完整零推测
- **Given**: anthropic-sdk-python源码可访问
- **When**: R阶段完成
- **Then**: facts.md含80+编号事实，覆盖客户端/消息/流式/工具/Beta/多后端/中间件/异常8模块，每条有源码路径，无推断词
- **Verification**: `human-judgment`

### AC-3: python-sdk I阶段洞察完整
- **Given**: facts.md完成
- **When**: I阶段完成
- **Then**: insights.md含3-5洞察四元组+知识地图+文档清单
- **Verification**: `human-judgment`

### AC-4: python-sdk E阶段文档完整
- **Given**: insights.md完成
- **When**: E阶段完成
- **Then**: python-sdk/下有6+ references、10-11 concepts、5-6 examples、各级index、log.md；references先行、index最后写；frontmatter完整
- **Verification**: `programmatic` + `human-judgment`

### AC-5: python-sdk V阶段零虚构API
- **Given**: 所有文档生成完成
- **When**: V阶段完成
- **Then**: 所有类名/方法名经Grep源码验证存在；无断链；frontmatter完整；问题全部修复
- **Verification**: `programmatic`

### AC-6: claude-code子bundle完整
- **Given**: claude-code目录可访问
- **When**: 该子bundle完成
- **Then**: 包含CLI安装与使用概念、插件体系说明、plugins/下核心插件索引、index.md、log.md
- **Verification**: `human-judgment`

### AC-7: cookbooks子bundle完整
- **Given**: claude-cookbooks目录可访问
- **When**: 该子bundle完成
- **Then**: 包含能力域分类索引、工具调用/多模态/RAG/子Agent等核心模式概念、精选示例文档、index.md、log.md
- **Verification**: `human-judgment`

### AC-8: prompt-engineering子bundle完整
- **Given**: prompt-eng-interactive-tutorial目录可访问
- **When**: 该子bundle完成
- **Then**: 包含提示词工程核心原则概念文档、9章教程要点结构化整理、index.md、log.md
- **Verification**: `human-judgment`

### AC-9: official-skills子bundle完整
- **Given**: skills目录可访问
- **When**: 该子bundle完成
- **Then**: 包含SKILL.md格式规范概念、Skills总索引（按类别分组）、skill-creator和claude-api重点详解、index.md、log.md
- **Verification**: `human-judgment`

### AC-10: financial-services子bundle完整
- **Given**: financial-services目录可访问
- **When**: 该子bundle完成
- **Then**: 包含金融Agent架构概念、Agent清单（Pitch/Market Researcher/GL Reconciler等）、垂直插件索引、index.md、log.md
- **Verification**: `human-judgment`

### AC-11: 质量门通过
- **Given**: 所有子bundle完成
- **When**: 运行质量门
- **Then**: `invoke gates.toctrees`和`invoke gates.utf8`通过，ai/index.md已更新
- **Verification**: `programmatic`

## Open Questions
- [ ] prompt-eng-interactive-tutorial只有README无章节文件，是否只基于README内容生成？（当前假设：是）
- [ ] official-skills下10+个skill，除skill-creator和claude-api外是否需要更深入文档？（当前计划：其余仅在索引中列出）
- [ ] cookbooks下大量Jupyter notebooks，是否需要转换notebook内容？（当前计划：做索引+模式提炼，不全文转换）
