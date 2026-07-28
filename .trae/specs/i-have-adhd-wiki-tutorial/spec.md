---
id: "i-have-adhd-wiki-tutorial"
title: "i-have-adhd ADHD友好输出技能 - Wiki教程"
source: "external/libs/i-have-adhd 源码分析与七概念方法论知识沉淀"
---

# i-have-adhd ADHD友好输出技能 - 产品需求文档

## Overview
- **Summary**: 基于七概念方法论（R→I→E→V知识沉淀链路），对 `external/libs/i-have-adhd` 开源项目进行系统性知识沉淀，生成结构化Wiki教程。该项目是一个跨AI编程助手的Agent Skills插件，通过10条输出规则重塑LLM响应格式，为ADHD（注意力缺陷多动障碍）用户或偏好简洁高效输出的开发者提供行动优先、步骤清晰、无冗余客套的AI交互体验。
- **Purpose**: 
  - 将i-have-adhd的设计理念、10条核心规则、跨平台适配方案、评估框架进行系统化整理
  - 沉淀为可复用的"ADHD友好输出模式"方法论资产
  - 为SpecWeave知识库提供高质量的Agent Skills实战案例
  - 帮助开发者理解如何设计认知友好型AI输出规范
- **Target Users**: 
  - AI Agent开发者（学习如何设计输出风格Skills）
  - 效率导向的程序员（希望获得更直接的AI编程助手输出）
  - ADHD用户或注意力易分散人群（寻求更适合的AI交互方式）
  - Agent Skills生态研究者（跨平台适配案例学习）

## Goals
- 完整覆盖i-have-adhd项目的核心设计：5大ADHD认知原理、10条输出规则、6条例外场景
- 提供8+主流AI编程助手平台的安装与配置指南（Claude Code、Codex、Cursor、Gemini CLI、Copilot、Zed、Hermes、Pi等）
- 解析always-on持久化机制（hooks实现、AGENTS.md配置）
- 记录项目的评估框架（5维评分rubric、A/B测试方法）
- 萃取可迁移的"认知友好型输出设计模式"
- 所有文档遵循SpecWeave知识库存放规范，支持myst-parser解析

## Non-Goals (Out of Scope)
- 不修改i-have-adhd上游源码（vendor目录禁止本地修改）
- 不创建新的ADHD辅助工具或插件
- 不涉及医学诊断或ADHD治疗建议（项目明确声明"No ADHD diagnosis needed"）
- 不进行心理学或神经科学深度学术研究
- 不翻译为日/韩等多语言版本（保持中文wiki，引用原有多语种README）

## Background & Context
- i-have-adhd（GitHub: ayghri/i-have-adhd）是MIT许可的开源Agent Skill，参考《The Adult ADHD Tool Kit》（J. Russell Ramsay & Anthony L. Rostain）设计
- 核心洞察：传统LLM输出存在"开场白冗余、步骤不明确、成果埋没、客套话泛滥"等问题，对工作记忆容量有限、启动困难、多巴胺稀缺的ADHD大脑极不友好
- 技术架构：遵循Agent Skills开放标准（SKILL.md + YAML frontmatter），支持plugin marketplace分发、SessionStart hooks自动注入、always-on配置文件持久化
- 跨平台适配：通过统一的SKILL.md核心 + 各平台特定配置文件（gemini.toml、plugin.json、marketplace.json等）实现"一次编写，多处运行"
- 评估体系：建立了Correctness(35%)/Autonomy(25%)/Actionability(20%)/Safety(10%)/Concision(10%)五维盲评框架，通过A/B测试验证输出质量不下降的前提下行动性显著提升

## Functional Requirements
- **FR-1**: Wiki必须包含项目概述章节：定位、核心理念、适用人群、许可证信息
- **FR-2**: Wiki必须解析5大ADHD认知驱动事实（工作记忆小、知行鸿沟、启动困难、时间感知模糊、多巴胺稀缺）
- **FR-3**: Wiki必须逐条详解10条输出规则，每条包含Bad/Good示例对比
- **FR-4**: Wiki必须列出6条例外场景（explain模式、破坏性操作确认、调试螺旋、歧义澄清、规则冲突、harness约束）
- **FR-5**: Wiki必须包含发送前自检清单（Pre-send check）的完整说明
- **FR-6**: Wiki必须提供各平台安装指南，至少覆盖Claude Code、Codex、Cursor、Gemini CLI、GitHub Copilot、Zed、Hermes、Pi 8个平台
- **FR-7**: Wiki必须说明always-on持久化机制：flag文件触发、hooks注入、AGENTS.md配置三种方式
- **FR-8**: Wiki必须解析评估框架：rubric五维权重、盲评流程、release gate标准
- **FR-9**: Wiki必须包含自定义与二次开发指南（fork修改SKILL.md、替换为个人版本）
- **FR-10**: Wiki必须包含故障排查章节（常见问题与解决方案）
- **FR-11**: Wiki必须萃取至少2个可复用模式：「认知原理→输出规则」映射模式、「跨平台Skill适配」模式

## Non-Functional Requirements
- **NFR-1**: 文档必须使用myst-parser兼容的MyST Markdown格式，frontmatter包含source、id、title字段
- **NFR-2**: 所有代码引用必须使用可点击的绝对路径链接格式（遵循SpecWeave规范）
- **NFR-3**: 文档结构采用Wiki风格：00-overview.md作为入口，各章节独立原子化文件
- **NFR-4**: 示例对比（Before/After）必须使用表格或并列代码块清晰展示
- **NFR-5**: 安装命令必须可直接复制执行，标注平台差异
- **NFR-6**: 模式萃取部分必须包含触发场景、核心步骤、反模式、迁移验证四要素
- **NFR-7**: 所有产出物存放于 `.agents/docs/knowledge/learning/03-agent-platforms-tools/i-have-adhd-wiki/`

## Constraints
- **Technical**: 
  - 必须遵循SpecWeave现有Wiki目录结构（参考agent-skills-wiki、open-code-review-wiki等）
  - 使用MyST Markdown，禁止使用HTML标签（必要时除外）
  - 代码块必须标注正确语言（bash/markdown/json/python等）
- **Business**: 
  - 内容保持客观技术分析，不涉及医学建议
  - 尊重原项目MIT许可证，注明来源
- **Dependencies**: 
  - 源文件路径：`d:\spaces\SpecWeave\external\libs\i-have-adhd\`
  - 参考现有Wiki结构：`.agents/docs/knowledge/learning/03-agent-platforms-tools/`

## Assumptions
- 用户希望Wiki教程使用中文编写（根据用户profile偏好）
- i-have-adhd是稳定版本，核心规则短期内不会有重大变更
- SpecWeave知识库已建立完善的分类索引机制
- 用户已了解Agent Skills基本概念（如不了解可参考已有的agent-skills-wiki）

## Acceptance Criteria

### AC-1: Wiki结构完整性
- **Given**: Wiki教程生成完成
- **When**: 检查目录结构
- **Then**: 存在00-overview.md入口文件 + 6个以上独立章节文件 + README.md索引，所有文件位于正确路径
- **Verification**: `programmatic`
- **Notes**: 通过文件系统检查验证

### AC-2: 10条核心规则全覆盖
- **Given**: Wiki核心规则章节完成
- **When**: 逐条核对SKILL.md中的10条规则
- **Then**: 每条规则都有规则说明、Bad示例、Good示例，无遗漏
- **Verification**: `programmatic`
- **Notes**: 与 [SKILL.md](file:///d:/spaces/SpecWeave/external/libs/i-have-adhd/skills/i-have-adhd/SKILL.md) 对比验证

### AC-3: 5大认知原理与规则映射清晰
- **Given**: 设计理念章节完成
- **When**: 审查认知原理与规则对应关系
- **Then**: 每条原理都能映射到至少1条具体规则，形成"原理→规则"闭环
- **Verification**: `human-judgment`
- **Notes**: 检查逻辑连贯性和设计可解释性

### AC-4: 跨平台安装指南可执行
- **Given**: 安装指南章节完成
- **When**: 审查各平台安装命令
- **Then**: 每个支持的平台都有安装、验证、更新、卸载、always-on完整步骤，命令格式正确
- **Verification**: `human-judgment`
- **Notes**: 对照 [INSTALL.md](file:///d:/spaces/SpecWeave/external/libs/i-have-adhd/INSTALL.md) 验证准确性

### AC-5: 可复用模式萃取达标
- **Given**: 模式萃取章节完成
- **When**: 按G3质量门检查模式文档
- **Then**: 每个模式包含触发场景、核心步骤、反模式、迁移验证，且可迁移至非AI输出领域（如技术文档写作、API设计）
- **Verification**: `human-judgment`
- **Notes**: 验证模式抽象层级足够，非仅适用于当前项目

### AC-6: 文档格式符合SpecWeave规范
- **Given**: 所有文档生成完成
- **When**: 检查frontmatter、路径引用、代码块格式
- **Then**: 所有文件包含正确frontmatter，链接使用相对路径或file:///绝对路径格式，代码块标注语言
- **Verification**: `programmatic`
- **Notes**: 可运行link-check或格式检查脚本验证

### AC-7: 评估框架完整记录
- **Given**: 评估体系章节完成
- **When**: 核对evals目录文档
- **Then**: 五维评分标准、权重、盲评流程、release gate条件均有记录
- **Verification**: `programmatic`
- **Notes**: 对照 [rubric.md](file:///d:/spaces/SpecWeave/external/libs/i-have-adhd/evals/rubric.md) 验证

## Open Questions
- [ ] 是否需要补充Trae IDE平台的适配说明？（原项目未明确提到Trae，但Trae兼容Agent Skills标准）
- [ ] 是否需要在Wiki中加入"快速上手"一页纸Cheat Sheet？
- [ ] 模式萃取部分是否需要单独沉淀到patterns/目录？
