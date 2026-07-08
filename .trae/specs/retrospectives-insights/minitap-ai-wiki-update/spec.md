---
id: "minitap-ai-wiki-update-spec"
title: "Minitap.ai官网系统学习与wiki更新PRD"
date: "2026-07-07"
---

# Minitap.ai官网系统学习与wiki更新 - Product Requirement Document

## Overview
- **Summary**: 系统研究Minitap官网（https://www.minitap.ai/）的产品信息、核心功能、技术优势、客户案例、最新动态等内容，基于研究成果创建标准化wiki文档，并更新相关的现有知识库文档，确保内容的准确性、时效性和完整性。
- **Purpose**: Minitap是mobile-use开源项目的商业公司，其官网包含产品定位、功能特性、技术指标、客户案例等关键信息，与已有的mobile-use深度学习分析形成互补。需要将官网信息系统化为结构化wiki文档，补充开源代码分析之外的产品视角。
- **Target Users**: AI Agent开发者、移动自动化测试工程师、技术研究者、SpecWeave知识库使用者

## Goals
- 创建minitap-official-wiki.md完整wiki文档，覆盖官网所有关键信息
- 更新mobile-use-deep-learning-analysis.md，补充商业产品视角和开源项目关系
- 遵循现有wiki文档格式规范（frontmatter、目录结构、章节组织）
- 确保所有信息准确、有来源标注、时效性说明
- 与现有模式库和复盘文档形成交叉引用

## Non-Goals (Out of Scope)
- 不深入分析mobile-use开源代码（此前已完成）
- 不创建非官网来源的推测性内容
- 不进行Minitap产品竞品对比分析
- 不修改模式库文件（仅做交叉引用）
- 不翻译官网内容为英文（保持中文为主，关键术语保留英文）

## Background & Context
- 已有成果：mobile-use开源项目深度学习分析报告（mobile-use-deep-learning-analysis.md）、复盘报告（retrospective-mobile-use-deep-learning-20260707/）、2个架构模式沉淀
- 缺失视角：现有资料主要从开源代码角度分析，缺乏商业产品定位、功能特性、定价策略、客户案例等官网视角
- Minitap官网关键信息：AndroidWorld基准测试100%准确率、minitest产品（零脚本QA Agent）、集成生态、客户名单、融资新闻、技术博客
- 现有wiki格式参考：anthropic-agent-roadmap-wiki.md（12章节标准结构）

## Functional Requirements
- **FR-1**: 创建minitap-official-wiki.md，包含官网核心信息提取
  - 产品定位与核心价值主张
  - 核心功能特性详解（minitest零脚本测试、AI Agent QA、多平台支持）
  - 技术指标与基准测试（AndroidWorld 100%、开源mobile-use关系）
  - 集成生态（GitHub/Slack/Jira/CI等）
  - 支持平台与技术栈（iOS/Android/Web、React Native/Flutter/Native）
  - 客户案例与客户logo展示
  - 定价与成本节约数据
  - 最新动态与博客文章
  - 媒体报道与融资信息
  - FAQ与资源链接
- **FR-2**: 更新mobile-use-deep-learning-analysis.md，补充商业产品章节
  - 添加Minitap公司与开源项目关系说明
  - 补充商业产品minitest功能介绍
  - 添加官网最新动态链接
- **FR-3**: 遵循wiki格式规范
  - 标准frontmatter（title/category/source/date/tags等）
  - 清晰的目录导航
  - 分章节结构化内容
  - 适当的表格和列表
  - 所有外部资源链接
  - 相关资源交叉引用

## Non-Functional Requirements
- **NFR-1**: 内容准确性 - 所有信息来源于官网，关键数据标注来源链接
- **NFR-2**: 时效性 - frontmatter标注文档创建日期和信息更新日期
- **NFR-3**: 可读性 - 章节结构清晰，使用适当的标题层级，关键信息用表格呈现
- **NFR-4**: 可维护性 - 内容模块化，便于后续更新
- **NFR-5**: 一致性 - 与现有wiki文档风格、格式、术语保持一致

## Constraints
- **Technical**: 使用Markdown格式，遵循现有wiki文档结构
- **Business**: 信息仅限官网公开内容，不包含内部信息或推测
- **Dependencies**: 依赖defuddle工具提取网页内容，依赖现有wiki格式模板

## Assumptions
- 官网内容为最新公开信息，可直接引用
- 现有mobile-use分析报告路径正确：docs/knowledge/learning/03-agent-platforms-tools/mobile-use-deep-learning-analysis.md
- wiki文档存放位置：docs/knowledge/learning/03-agent-platforms-tools/
- 信息来源以主站为主，博客和benchmark页面可作为补充

## Acceptance Criteria

### AC-1: minitap-official-wiki.md创建完成
- **Given**: 已获取minitap.ai官网完整内容
- **When**: 完成wiki文档撰写
- **Then**: 文档包含10个以上核心章节，覆盖产品/功能/技术/客户/定价/动态等维度，格式符合wiki规范
- **Verification**: `human-judgment`

### AC-2: 内容准确性验证
- **Given**: wiki文档已完成
- **When**: 检查关键数据和声明
- **Then**: 所有技术指标（如AndroidWorld 100%）、客户名单、产品特性均与官网一致，关键信息有来源链接
- **Verification**: `human-judgment`

### AC-3: mobile-use-deep-learning-analysis.md更新完成
- **Given**: 新wiki文档已创建
- **When**: 更新现有mobile-use分析报告
- **Then**: 补充商业产品视角章节，说明开源项目与商业产品关系，不破坏原有内容结构
- **Verification**: `human-judgment`

### AC-4: 格式规范符合要求
- **Given**: 所有文档已完成
- **When**: 对照现有wiki格式检查
- **Then**: frontmatter完整，目录导航清晰，章节结构合理，交叉引用正确，文件命名符合kebab-case规范
- **Verification**: `human-judgment`

### AC-5: 交叉引用完整性
- **Given**: 文档已创建
- **When**: 检查相关文档引用
- **Then**: 新wiki引用mobile-use分析报告、复盘报告、相关模式文件；现有报告引用新wiki
- **Verification**: `human-judgment`

## Open Questions
- [ ] 是否需要单独获取benchmark页面和博客页面的详细内容？
- [ ] mobile-use分析报告的更新是新增独立章节还是在现有章节中补充？
- [ ] 是否需要在wiki中包含与其他QA工具（Maestro/Appium/Playwright）的对比表格？
